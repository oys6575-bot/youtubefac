#!/usr/bin/env python3
"""Run the mobile dashboard gateway on loopback only."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import uvicorn


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="유튜브공장 모바일 Dashboard Gateway")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--config", type=Path, default=ROOT / "config/mobile-dashboard.yaml")
    parser.add_argument("--projects", type=Path, default=ROOT / "projects")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be between 1024 and 65535")
    if not args.config.is_file():
        parser.error(f"mobile config not found: {args.config}")

    from backlot.mobile_security import load_mobile_config

    config = load_mobile_config(args.config)
    gateway = config.get("gateway") or {}
    if gateway.get("host", "127.0.0.1") != "127.0.0.1":
        parser.error("gateway.host must be 127.0.0.1")
    configured_port = int(gateway.get("port", args.port))
    if args.port != 8787 and args.port != configured_port:
        parser.error("command port must match gateway.port")

    os.environ["MOBILE_DASHBOARD_CONFIG"] = str(args.config.resolve())
    os.environ["OPENMONTAGE_PROJECTS_DIR"] = str(args.projects.resolve())
    os.chdir(ROOT)
    uvicorn.run(
        "backlot.server:app",
        host="127.0.0.1",
        port=configured_port,
        access_log=False,
        proxy_headers=False,
        server_header=False,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
