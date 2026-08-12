#!/usr/bin/env python3
"""Fail-closed operational audit for the dedicated mobile endpoint."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _truthy_leaf(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_truthy_leaf(item) for item in value.values())
    if isinstance(value, list):
        return any(_truthy_leaf(item) for item in value)
    return value is True or (isinstance(value, str) and value.lower() in {"true", "yes", "enabled"})


def _walk(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def audit_serve_status(status: dict[str, Any], port: int) -> list[str]:
    findings: list[str] = []
    proxies: list[str] = []
    for key, value in _walk(status):
        if "funnel" in str(key).lower() and _truthy_leaf(value):
            findings.append("public endpoint flag is enabled")
        if str(key).lower() == "proxy" and isinstance(value, str):
            proxies.append(value)
    if not proxies:
        findings.append("no Serve proxy target found")
    for proxy in proxies:
        parsed = urlparse(proxy)
        if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
            findings.append(f"Serve proxy is not loopback-only: {proxy}")
        if parsed.port != port:
            findings.append(f"Serve proxy port does not match gateway: {proxy}")
    return findings


def audit_cached_certificate(cert_dir: Path, domains: list[str]) -> list[str]:
    """Require tailscaled's non-empty cached certificate for every Serve domain."""
    findings: list[str] = []
    if not domains:
        return ["no Tailscale certificate domain found"]
    for domain in domains:
        cert_file = cert_dir / f"{domain}.crt"
        if not cert_file.is_file() or cert_file.stat().st_size == 0:
            findings.append(f"cached TLS certificate is missing: {domain}")
    return findings


def audit_coordinator_health(
    path: Path, *, max_age_seconds: float = 30.0
) -> list[str]:
    if not path.is_file():
        return ["coordinator health file is missing"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        pid = int(value["pid"])
        timestamp = datetime.fromisoformat(str(value["timestamp"]).replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - timestamp.astimezone(timezone.utc)).total_seconds()
        if age < -5 or age > max_age_seconds:
            return [f"coordinator health is stale: {age:.1f}s"]
        os.kill(pid, 0)
    except ProcessLookupError:
        return ["coordinator process is not running"]
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return [f"coordinator health is invalid: {exc}"]
    return []


def preflight_is_ok(findings: list[str], *, backend: str, health_ok: bool) -> bool:
    return not findings and backend == "Running" and health_ok


def _run_json(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "command failed")
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise RuntimeError("command returned non-object JSON")
    return value


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="유튜브공장 모바일 endpoint 사전 점검")
    parser.add_argument(
        "--socket",
        type=Path,
        default=Path(f"/tmp/ytf-mobile-{os.getuid()}/tailscaled.sock"),
    )
    parser.add_argument(
        "--coordinator-health",
        type=Path,
        default=root / ".runtime/mobile-dashboard/coordinator-health.json",
    )
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--tailscale", default="/opt/homebrew/bin/tailscale")
    parser.add_argument(
        "--cert-dir",
        type=Path,
        default=root / ".runtime/mobile-dashboard/tailscale/state/certs",
    )
    args = parser.parse_args()
    report: dict[str, Any] = {"ok": False, "checks": {}, "findings": []}

    try:
        with socket.create_connection(("127.0.0.1", args.port), timeout=2):
            report["checks"]["loopback_listener"] = "PASS"
        with urllib.request.urlopen(f"http://127.0.0.1:{args.port}/api/health", timeout=3) as response:
            health = json.load(response)
        report["checks"]["gateway_health"] = "PASS" if health.get("ok") else "FAIL"
        status = _run_json([args.tailscale, f"--socket={args.socket}", "status", "--json"])
        report["checks"]["tailscale_backend"] = status.get("BackendState", "UNKNOWN")
        domains = [str(value) for value in status.get("CertDomains", []) if value]
        certificate_findings = audit_cached_certificate(args.cert_dir, domains)
        report["findings"].extend(certificate_findings)
        report["checks"]["tls_certificate"] = "PASS" if not certificate_findings else "FAIL"
        serve = _run_json([args.tailscale, f"--socket={args.socket}", "serve", "status", "--json"])
        findings = audit_serve_status(serve, args.port)
        report["findings"].extend(findings)
        report["checks"]["private_serve"] = "PASS" if not findings else "FAIL"
        coordinator_findings = audit_coordinator_health(args.coordinator_health)
        report["findings"].extend(coordinator_findings)
        report["checks"]["coordinator"] = (
            "PASS" if not coordinator_findings else "FAIL"
        )
        report["ok"] = preflight_is_ok(
            report["findings"],
            backend=str(status.get("BackendState")),
            health_ok=health.get("ok") is True,
        )
    except Exception as exc:
        report["findings"].append(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
