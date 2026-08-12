#!/usr/bin/env python3
"""Install isolated per-user dashboard, Tailscale, and Coordinator services."""

from __future__ import annotations

import argparse
import os
import plistlib
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LABEL_DASHBOARD = "com.mk.youtube-factory.dashboard"
LABEL_TAILSCALE = "com.mk.youtube-factory.tailscale"
LABEL_COORDINATOR = "com.mk.youtube-factory.coordinator"


def service_plists() -> dict[str, dict]:
    runtime = ROOT / ".runtime/mobile-dashboard"
    tailscale_runtime = runtime / "tailscale"
    tailscale_socket_dir = Path(f"/tmp/ytf-mobile-{os.getuid()}")
    logs = runtime / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    python = ROOT / ".venv/bin/python"
    config = ROOT / "config/mobile-dashboard.yaml"
    projects = ROOT / "projects"
    tailscaled = Path("/opt/homebrew/opt/tailscale/bin/tailscaled")
    coordinator = ROOT / "scripts/mobile-dashboard-coordinator.py"
    routing = ROOT / "config/orca-model-routing.yaml"
    orca = shutil.which("orca")
    for required in (python, config, tailscaled, coordinator, routing):
        if not required.is_file():
            raise FileNotFoundError(f"required service file not found: {required}")
    if not orca:
        raise FileNotFoundError("required Orca CLI not found on PATH")
    tailscale_runtime.mkdir(parents=True, exist_ok=True)
    tailscale_socket_dir.mkdir(parents=True, exist_ok=True)
    (tailscale_runtime / "state").mkdir(exist_ok=True)
    common = {"RunAtLoad": True, "KeepAlive": True, "ProcessType": "Background"}
    return {
        LABEL_DASHBOARD: {
            "Label": LABEL_DASHBOARD,
            "ProgramArguments": [
                str(python), str(ROOT / "scripts/mobile-dashboard.py"),
                "--config", str(config), "--projects", str(projects), "--port", "8787",
            ],
            "WorkingDirectory": str(ROOT),
            "EnvironmentVariables": {
                "PYTHONPATH": str(ROOT),
                "MOBILE_DASHBOARD_CONFIG": str(config),
                "OPENMONTAGE_PROJECTS_DIR": str(projects),
            },
            "StandardOutPath": str(logs / "dashboard.out.log"),
            "StandardErrorPath": str(logs / "dashboard.err.log"),
            **common,
        },
        LABEL_TAILSCALE: {
            "Label": LABEL_TAILSCALE,
            "ProgramArguments": [
                str(tailscaled), "--tun=userspace-networking",
                f"--state={tailscale_runtime / 'tailscaled.state'}",
                f"--statedir={tailscale_runtime / 'state'}",
                f"--socket={tailscale_socket_dir / 'tailscaled.sock'}",
            ],
            "WorkingDirectory": str(ROOT),
            "StandardOutPath": str(logs / "tailscaled.out.log"),
            "StandardErrorPath": str(logs / "tailscaled.err.log"),
            **common,
        },
        LABEL_COORDINATOR: {
            "Label": LABEL_COORDINATOR,
            "ProgramArguments": [
                str(python),
                str(coordinator),
                "--projects",
                str(projects),
                "--routing",
                str(routing),
                "--health",
                str(runtime / "coordinator-health.json"),
                "--poll-seconds",
                "2",
            ],
            "WorkingDirectory": str(ROOT),
            "EnvironmentVariables": {
                "PYTHONPATH": str(ROOT),
                "OPENMONTAGE_PROJECTS_DIR": str(projects),
                "ORCA_CLI": orca,
                "HOME": str(Path.home()),
                "PATH": ":".join(
                    [
                        str(Path(orca).parent),
                        str(Path.home() / ".local/bin"),
                        "/opt/homebrew/bin",
                        "/usr/bin",
                        "/bin",
                    ]
                ),
            },
            "StandardOutPath": str(logs / "coordinator.out.log"),
            "StandardErrorPath": str(logs / "coordinator.err.log"),
            **common,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="유튜브공장 모바일 서비스 설치")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true")
    group.add_argument("--remove", action="store_true")
    group.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    launch_agents = Path.home() / "Library/LaunchAgents"
    domain = f"gui/{os.getuid()}"

    if args.remove:
        for label in (LABEL_DASHBOARD, LABEL_TAILSCALE, LABEL_COORDINATOR):
            path = launch_agents / f"{label}.plist"
            subprocess.run(["launchctl", "bootout", domain, str(path)], capture_output=True)
            if path.exists():
                path.unlink()
        return 0

    plists = service_plists()
    if args.dry_run:
        for label, value in plists.items():
            print(f"[{label}]")
            print(plistlib.dumps(value).decode("utf-8"))
        return 0

    launch_agents.mkdir(parents=True, exist_ok=True)
    for label, value in plists.items():
        path = launch_agents / f"{label}.plist"
        subprocess.run(["launchctl", "bootout", domain, str(path)], capture_output=True)
        path.write_bytes(plistlib.dumps(value, fmt=plistlib.FMT_XML, sort_keys=True))
        subprocess.run(["launchctl", "bootstrap", domain, str(path)], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
