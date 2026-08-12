#!/usr/bin/env python3
"""Copy only role-approved secrets without logging their values."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

from dotenv import dotenv_values


ROLE_ALLOWLISTS = {
    "control": (),
    "research": ("YOUTUBE_API_KEY",),
    "verification": (),
    "story_visual": (),
    "production": (
        "PEXELS_API_KEY",
        "PIXABAY_API_KEY",
        "UNSPLASH_ACCESS_KEY",
    ),
    "qa": (),
}

GLOBAL_ALLOWED_KEYS = frozenset(
    key for allowlist in ROLE_ALLOWLISTS.values() for key in allowlist
)
RUNTIME_ALLOWLIST = frozenset(
    {
        "OPENMONTAGE_PROJECTS_DIR",
        "OPENMONTAGE_CACHE_DIR",
    }
)


class ProvisionError(ValueError):
    """Raised when a role or its required secret material is invalid."""


def _serialize(keys: Iterable[str], values: dict[str, str | None]) -> str:
    lines: list[str] = []
    for key in keys:
        value = values.get(key)
        if not isinstance(value, str) or not value:
            raise ProvisionError(f"required key is missing: {key}")
        if "\n" in value or "\r" in value:
            raise ProvisionError(f"multiline secret values are unsupported: {key}")
        lines.append(f"{key}={value}\n")
    return "".join(lines)


def provision_role_env(
    role: str,
    source: Path,
    target: Path,
    *,
    runtime_values: dict[str, str] | None = None,
) -> dict[str, object]:
    """Atomically write a mode-0600 env containing only the role allowlist."""

    if role not in ROLE_ALLOWLISTS:
        raise ProvisionError(f"unknown role: {role}")
    try:
        raw = dotenv_values(source)
    except OSError as exc:
        raise ProvisionError(f"cannot read source env: {source}") from exc

    allowlist = ROLE_ALLOWLISTS[role]
    supplied_runtime = runtime_values or {}
    disallowed_runtime = sorted(set(supplied_runtime) - RUNTIME_ALLOWLIST)
    if disallowed_runtime:
        raise ProvisionError(f"runtime key is not allowlisted: {disallowed_runtime[0]}")
    runtime_lines: list[str] = []
    for key in sorted(supplied_runtime):
        value = supplied_runtime[key]
        if not isinstance(value, str) or not value or "\n" in value or "\r" in value:
            raise ProvisionError(f"invalid runtime value: {key}")
        runtime_lines.append(f"{key}={value}\n")
    content = "".join(runtime_lines) + _serialize(allowlist, dict(raw))
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        os.chmod(target, 0o600)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        Path(temporary).unlink(missing_ok=True)
        raise
    return {
        "role": role,
        "keys_present": list(allowlist),
        "runtime_keys": sorted(supplied_runtime),
    }


def merge_allowed_secret(source: Path, target: Path, key: str) -> dict[str, object]:
    """Atomically merge one globally allowlisted key into a private env file."""

    if key not in GLOBAL_ALLOWED_KEYS:
        raise ProvisionError(f"secret name is not allowlisted: {key}")
    source_values = dict(dotenv_values(source))
    value = source_values.get(key)
    if not isinstance(value, str) or not value:
        raise ProvisionError(f"required key is missing: {key}")
    if "\n" in value or "\r" in value:
        raise ProvisionError(f"multiline secret values are unsupported: {key}")

    target_values = dict(dotenv_values(target)) if target.exists() else {}
    target_values[key] = value
    lines: list[str] = []
    for name, current in target_values.items():
        if not isinstance(name, str) or not isinstance(current, str):
            continue
        if "\n" in current or "\r" in current:
            raise ProvisionError(f"multiline secret values are unsupported: {name}")
        lines.append(f"{name}={current}\n")

    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.writelines(lines)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        os.chmod(target, 0o600)
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        Path(temporary).unlink(missing_ok=True)
        raise
    return {"key": key, "present": True}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True, choices=sorted(ROLE_ALLOWLISTS))
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--projects-root", type=Path)
    args = parser.parse_args()
    try:
        runtime_values = (
            {"OPENMONTAGE_PROJECTS_DIR": str(args.projects_root.resolve())}
            if args.projects_root
            else None
        )
        status = provision_role_env(
            args.role,
            args.source,
            args.target,
            runtime_values=runtime_values,
        )
    except ProvisionError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, **status}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
