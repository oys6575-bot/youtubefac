from __future__ import annotations

from pathlib import Path

import pytest

from backlot.mobile_security import (
    MobileAuthError,
    MobileSecurity,
    load_mobile_config,
)


CONFIG = {
    "enabled": True,
    "canonical_origin": "https://factory.tail.test",
    "allowed_users": [{"login": "owner@example.com", "user_id": "123"}],
    "rate_limit_per_minute": 3,
}


def test_exact_login_maps_to_configured_stable_actor() -> None:
    security = MobileSecurity(CONFIG, secret=b"x" * 32)
    actor = security.authenticate("127.0.0.1", "owner@example.com")
    assert actor.tailscale_login == "owner@example.com"
    assert actor.tailscale_user_id == "123"


@pytest.mark.parametrize(
    ("host", "login", "code"),
    [
        ("192.168.1.50", "owner@example.com", "gateway_not_loopback"),
        ("127.0.0.1", None, "tailscale_identity_missing"),
        ("127.0.0.1", "attacker@example.com", "tailscale_user_forbidden"),
        ("127.0.0.1", "OWNER@example.com", "tailscale_user_forbidden"),
    ],
)
def test_non_loopback_missing_and_nonexact_identity_are_rejected(host, login, code) -> None:
    security = MobileSecurity(CONFIG, secret=b"x" * 32)
    with pytest.raises(MobileAuthError, match=code):
        security.authenticate(host, login)


def test_csrf_cookie_token_and_origin_are_bound() -> None:
    security = MobileSecurity(CONFIG, secret=b"x" * 32)
    cookie, token = security.issue_session()
    security.verify_post(cookie, token, "https://factory.tail.test")
    with pytest.raises(MobileAuthError, match="csrf"):
        security.verify_post(cookie, "wrong", "https://factory.tail.test")
    with pytest.raises(MobileAuthError, match="origin"):
        security.verify_post(cookie, token, "https://evil.example")


def test_local_preview_requires_explicit_development_switch() -> None:
    preview = {**CONFIG, "allow_local_development": True}
    security = MobileSecurity(preview, secret=b"x" * 32)
    actor = security.authenticate("127.0.0.1", None)
    assert actor.tailscale_login == "owner@example.com"

    production = MobileSecurity(CONFIG, secret=b"x" * 32)
    with pytest.raises(MobileAuthError, match="tailscale_identity_missing"):
        production.authenticate("127.0.0.1", None)


def test_config_fails_closed_on_domain_wildcard_or_duplicate_login(tmp_path: Path) -> None:
    config = tmp_path / "mobile.yaml"
    config.write_text(
        """
enabled: true
canonical_origin: https://factory.tail.test
allowed_users:
  - {login: '*@example.com', user_id: '1'}
  - {login: '*@example.com', user_id: '2'}
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="exact login"):
        load_mobile_config(config)
