"""Security boundary for Backlot's Tailscale-only mobile routes."""

from __future__ import annotations

import base64
import hashlib
import hmac
import ipaddress
import os
import secrets
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Mapping

import yaml

from backlot.mobile_actions import Actor


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT / "config/mobile-dashboard.yaml"


class MobileAuthError(PermissionError):
    def __init__(self, code: str, status_code: int = 403):
        super().__init__(code)
        self.code = code
        self.status_code = status_code


def load_mobile_config(path: Path | None = None) -> dict[str, Any]:
    target = path or Path(os.environ.get("MOBILE_DASHBOARD_CONFIG", DEFAULT_CONFIG_PATH))
    if not target.is_file():
        return {"enabled": False, "allowed_users": []}
    value = yaml.safe_load(target.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("mobile dashboard config must be a mapping")
    users = value.get("allowed_users") or []
    if not isinstance(users, list):
        raise ValueError("allowed_users must be a list")
    seen: set[str] = set()
    for user in users:
        if not isinstance(user, dict):
            raise ValueError("allowed_users entries must be mappings")
        login = user.get("login")
        user_id = user.get("user_id")
        if (
            not isinstance(login, str)
            or not login.strip()
            or login != login.strip()
            or any(token in login for token in ("*", "?", "[", "]"))
        ):
            raise ValueError("allowed_users requires an exact login, never a wildcard")
        if login in seen:
            raise ValueError("allowed_users contains a duplicate exact login")
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("allowed_users requires a stable user_id")
        seen.add(login)
    if value.get("enabled"):
        origin = value.get("canonical_origin")
        if not isinstance(origin, str) or not origin.startswith("https://") or origin.endswith("/"):
            raise ValueError("enabled mobile dashboard requires canonical_origin https://host without slash")
        if not users:
            raise ValueError("enabled mobile dashboard requires at least one exact allowed user")
    return value


def _b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


class MobileSecurity:
    """Authenticate Serve identity and protect decision POST requests.

    Tailscale Serve injects the verified login header and strips a client's
    spoofed copy.  Serve does not expose a numeric user id header, so the
    stable id recorded in receipts comes from the exact-login allowlist.
    """

    def __init__(self, config: Mapping[str, Any], *, secret: bytes | None = None):
        self.config = dict(config)
        self.enabled = bool(self.config.get("enabled"))
        self.canonical_origin = str(self.config.get("canonical_origin") or "")
        self.max_payload_bytes = int(self.config.get("max_payload_bytes", 8192))
        self.rate_limit_per_minute = int(self.config.get("rate_limit_per_minute", 30))
        self._secret = secret or secrets.token_bytes(32)
        self._users = {
            str(item["login"]): str(item["user_id"])
            for item in self.config.get("allowed_users", [])
            if isinstance(item, Mapping) and item.get("login") and item.get("user_id")
        }
        self._rate: dict[str, deque[float]] = defaultdict(deque)

    def authenticate(self, client_host: str | None, tailscale_login: str | None) -> Actor:
        if not self.enabled:
            raise MobileAuthError("mobile_dashboard_disabled", 503)
        try:
            loopback = bool(client_host) and ipaddress.ip_address(client_host).is_loopback
        except ValueError:
            loopback = False
        if not loopback:
            raise MobileAuthError("gateway_not_loopback", 403)
        if not tailscale_login:
            if self.config.get("allow_local_development") is True and self._users:
                login, user_id = next(iter(self._users.items()))
                return Actor(tailscale_login=login, tailscale_user_id=user_id)
            raise MobileAuthError("tailscale_identity_missing", 401)
        user_id = self._users.get(tailscale_login)
        if user_id is None:
            raise MobileAuthError("tailscale_user_forbidden", 403)
        return Actor(tailscale_login=tailscale_login, tailscale_user_id=user_id)

    def issue_session(self) -> tuple[str, str]:
        session_id = _b64url(secrets.token_bytes(24))
        signature = hmac.new(self._secret, session_id.encode(), hashlib.sha256).hexdigest()
        cookie = f"{session_id}.{signature}"
        token = hmac.new(self._secret, f"csrf:{session_id}".encode(), hashlib.sha256).hexdigest()
        return cookie, token

    def verify_post(self, cookie: str | None, token: str | None, origin: str | None) -> None:
        if not cookie or "." not in cookie:
            raise MobileAuthError("csrf_session_missing", 403)
        session_id, signature = cookie.rsplit(".", 1)
        expected_signature = hmac.new(
            self._secret, session_id.encode(), hashlib.sha256
        ).hexdigest()
        expected_token = hmac.new(
            self._secret, f"csrf:{session_id}".encode(), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature) or not token or not hmac.compare_digest(
            token, expected_token
        ):
            raise MobileAuthError("csrf_invalid", 403)
        if not origin or not hmac.compare_digest(origin, self.canonical_origin):
            raise MobileAuthError("origin_invalid", 403)

    def enforce_rate_limit(self, actor: Actor, *, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        bucket = self._rate[actor.tailscale_login]
        while bucket and current - bucket[0] >= 60:
            bucket.popleft()
        if len(bucket) >= self.rate_limit_per_minute:
            raise MobileAuthError("action_rate_limited", 429)
        bucket.append(current)
