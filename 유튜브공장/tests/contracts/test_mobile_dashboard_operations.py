from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]


def load_preflight_module():
    path = ROOT / "scripts/mobile-dashboard-preflight.py"
    spec = importlib.util.spec_from_file_location("mobile_dashboard_preflight", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_gateway_runner_is_loopback_only() -> None:
    runner = (ROOT / "scripts/mobile-dashboard.py").read_text(encoding="utf-8")
    assert 'host="127.0.0.1"' in runner
    assert "0.0.0.0" not in runner
    assert "uvicorn" in runner


def test_tailscale_lifecycle_is_dedicated_and_serve_only() -> None:
    script = (ROOT / "scripts/mobile-dashboard-tailscale.sh").read_text(encoding="utf-8")
    assert ".runtime/mobile-dashboard/tailscale" in script
    assert "tailscaled.sock" in script
    assert "tailscaled.state" in script
    assert "serve --bg" in script
    assert "serve status --json" in script
    assert "tailscale funnel" not in script
    assert "egonari" not in script
    assert ".hermes" not in script


def test_tailscale_socket_uses_short_dedicated_macos_path() -> None:
    # macOS sockaddr_un rejects long worktree paths (typically > 103 bytes).
    script = (ROOT / "scripts/mobile-dashboard-tailscale.sh").read_text(encoding="utf-8")
    installer = (ROOT / "scripts/install-mobile-dashboard-services.py").read_text(encoding="utf-8")
    assert "/tmp/ytf-mobile-" in script
    assert "/tmp/ytf-mobile-" in installer


def test_lifecycle_reuses_healthy_launchd_daemon_instead_of_starting_a_second_one() -> None:
    script = (ROOT / "scripts/mobile-dashboard-tailscale.sh").read_text(encoding="utf-8")
    assert '"$TAILSCALE_BIN" --socket="$SOCKET" status --json >/dev/null 2>&1' in script


def test_serve_status_audit_accepts_only_loopback_proxy_and_no_public_flag() -> None:
    module = load_preflight_module()
    safe = {
        "TCP": {"443": {"HTTPS": True}},
        "Web": {"factory.tail.test:443": {"Handlers": {"/": {"Proxy": "http://127.0.0.1:8787"}}}},
        "AllowFunnel": {"factory.tail.test:443": False},
    }
    assert module.audit_serve_status(safe, 8787) == []

    public = {**safe, "AllowFunnel": {"factory.tail.test:443": True}}
    non_loopback = {
        "TCP": {"443": {"HTTPS": True}},
        "Web": {"factory.tail.test:443": {"Handlers": {"/": {"Proxy": "http://192.168.1.2:8787"}}}},
    }
    assert any("public" in finding for finding in module.audit_serve_status(public, 8787))
    assert any("loopback" in finding for finding in module.audit_serve_status(non_loopback, 8787))


def test_cached_certificate_audit_rejects_missing_certificate(tmp_path: Path) -> None:
    """A configured HTTPS proxy is not ready until tailscaled cached its certificate."""
    module = load_preflight_module()
    domain = "factory.tail.test"

    assert module.audit_cached_certificate(tmp_path, [domain]) == [
        f"cached TLS certificate is missing: {domain}"
    ]

    (tmp_path / f"{domain}.crt").write_text("certificate", encoding="utf-8")
    assert module.audit_cached_certificate(tmp_path, [domain]) == []


def test_preflight_verdict_fails_when_any_finding_exists() -> None:
    module = load_preflight_module()

    assert module.preflight_is_ok([], backend="Running", health_ok=True) is True
    assert module.preflight_is_ok(
        ["cached TLS certificate is missing: factory.tail.test"],
        backend="Running",
        health_ok=True,
    ) is False


def test_example_config_has_no_real_identity_and_requires_exact_users() -> None:
    config = (ROOT / "config/mobile-dashboard.example.yaml").read_text(encoding="utf-8")
    assert "owner@example.com" in config
    assert "allowed_users:" in config
    assert "canonical_origin: https://" in config
    assert "allow_everyone" not in config
    assert "0.0.0.0" not in config


def test_launch_agent_installer_uses_two_separate_services() -> None:
    installer = (ROOT / "scripts/install-mobile-dashboard-services.py").read_text(encoding="utf-8")
    assert "com.mk.youtube-factory.dashboard" in installer
    assert "com.mk.youtube-factory.tailscale" in installer
    assert "KeepAlive" in installer
    assert "plistlib" in installer
