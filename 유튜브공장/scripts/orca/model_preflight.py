#!/usr/bin/env python3
"""Read-only preflight for the exact Orca role deployment."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from dotenv import dotenv_values

from lib.orca_model_routing import DEFAULT_ROUTING_PATH, load_routing


CommandProbe = Callable[[str], dict[str, object]]
ModelProbe = Callable[[str], dict[str, object]]

COMMANDS = {
    "orca": ["/opt/homebrew/bin/orca", "status", "--json"],
    "codex": ["codex", "login", "status"],
    "claude": ["claude", "auth", "status", "--json"],
    "hermes": ["hermes", "--version"],
    "git": ["git", "status", "--short", "--branch"],
}

SECRET_NAMES = (
    "YOUTUBE_API_KEY",
    "PEXELS_API_KEY",
    "PIXABAY_API_KEY",
    "UNSPLASH_ACCESS_KEY",
)


def probe_command(name: str) -> dict[str, object]:
    command = COMMANDS[name]
    executable = command[0]
    if "/" not in executable and shutil.which(executable) is None:
        return {"ok": False, "detail": "not_found"}
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "detail": type(exc).__name__}
    detail = "ready" if completed.returncode == 0 else f"exit_{completed.returncode}"
    return {"ok": completed.returncode == 0, "detail": detail}


def probe_models(endpoint: str) -> dict[str, object]:
    url = f"{endpoint.rstrip('/')}/models"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            payload = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "available_models": [],
            "primary_available": False,
            "detail": type(exc).__name__,
        }
    models = sorted(
        item["id"]
        for item in payload.get("data", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    )
    return {
        "ok": True,
        "available_models": models,
        "primary_available": "qwen3.6-35b-a3b-mlx" in models,
    }


def build_preflight_report(
    factory_root: Path,
    *,
    command_probe: CommandProbe = probe_command,
    model_probe: ModelProbe = probe_models,
    env_path: Path | None = None,
    routing_path: Path | None = None,
) -> dict[str, object]:
    """Build a value-free status report; never return environment values."""

    root = factory_root.resolve()
    selected_routing = routing_path or root / "config" / "orca-model-routing.yaml"
    routing = load_routing(selected_routing)
    checks = {name: command_probe(name) for name in COMMANDS}
    checks["lm_studio"] = model_probe(routing["local_models"]["endpoint"])
    source_env = env_path or root / ".env"
    values = dotenv_values(source_env) if source_env.exists() else {}
    secret_status = {
        name: isinstance(values.get(name), str) and bool(values.get(name))
        for name in SECRET_NAMES
    }
    all_checks = all(bool(item.get("ok")) for item in checks.values())
    exact_model = bool(checks["lm_studio"].get("primary_available"))
    return {
        "ok": all_checks and exact_model,
        "factory_cwd": str(root),
        "routing_schema_version": routing["schema_version"],
        "checks": checks,
        "secret_status": secret_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--factory-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
    )
    args = parser.parse_args()
    report = build_preflight_report(args.factory_root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
