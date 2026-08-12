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
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--tailscale", default="/opt/homebrew/bin/tailscale")
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
        serve = _run_json([args.tailscale, f"--socket={args.socket}", "serve", "status", "--json"])
        findings = audit_serve_status(serve, args.port)
        report["findings"].extend(findings)
        report["checks"]["private_serve"] = "PASS" if not findings else "FAIL"
        report["ok"] = not findings and status.get("BackendState") == "Running" and health.get("ok") is True
    except Exception as exc:
        report["findings"].append(str(exc))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
