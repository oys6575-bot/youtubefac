"""Atomic mutual exclusion for large local text and media runtimes."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


class LeaseConflictError(RuntimeError):
    """Raised when another owner holds or left an unrecovered lease."""


@dataclass(frozen=True)
class ResourceLease:
    path: Path
    lane: str
    owner: str
    ttl_seconds: int = 3600

    def __post_init__(self) -> None:
        if self.lane not in {"local_text", "local_media"}:
            raise ValueError("lane must be local_text or local_media")
        if not self.owner.strip():
            raise ValueError("owner must be non-empty")
        if self.ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

    def _read(self) -> dict[str, Any]:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise LeaseConflictError(f"cannot inspect existing lease: {exc}") from exc
        if not isinstance(payload, dict):
            raise LeaseConflictError("existing lease is not an object")
        return payload

    @staticmethod
    def _is_expired(payload: dict[str, Any]) -> bool:
        try:
            expires_at = datetime.fromisoformat(str(payload["expires_at"]))
        except (KeyError, TypeError, ValueError):
            return False
        if expires_at.tzinfo is None:
            return False
        return expires_at <= datetime.now(timezone.utc)

    def acquire(self) -> dict[str, Any]:
        """Acquire with O_EXCL; an expired file still requires explicit recovery."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        payload = {
            "version": "1.0",
            "lane": self.lane,
            "owner": self.owner,
            "acquired_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=self.ttl_seconds)).isoformat(),
            "pid": os.getpid(),
        }
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        try:
            descriptor = os.open(self.path, flags, 0o600)
        except FileExistsError as exc:
            existing = self._read()
            qualifier = "expired " if self._is_expired(existing) else ""
            raise LeaseConflictError(
                f"{qualifier}lease held by {existing.get('owner', 'unknown')} "
                f"on {existing.get('lane', 'unknown')}"
            ) from exc
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, sort_keys=True)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            self.path.unlink(missing_ok=True)
            raise
        return payload

    def release(self) -> None:
        """Release only a lease owned by this instance."""

        payload = self._read()
        if payload.get("owner") != self.owner or payload.get("lane") != self.lane:
            raise PermissionError("cannot release another owner's resource lease")
        self.path.unlink()

    def recover_expired(self, *, authority: str) -> dict[str, Any]:
        """Remove an expired lease only under the control role."""

        if authority != "control":
            raise PermissionError("only control can recover an expired resource lease")
        payload = self._read()
        if not self._is_expired(payload):
            raise LeaseConflictError("active resource lease cannot be recovered")
        self.path.unlink()
        return payload

