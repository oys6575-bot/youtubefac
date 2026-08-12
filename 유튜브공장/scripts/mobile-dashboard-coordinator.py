#!/usr/bin/env python3
"""Long-running Coordinator for durable topic approval jobs."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backlot.auto_dispatch_worker import Coordinator
from backlot.orca_auto_dispatch import OrcaRunner
from lib.orca_model_routing import load_routing


def _log(event: str, **fields: object) -> None:
    print(
        json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": event,
                **fields,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects", type=Path, required=True)
    parser.add_argument(
        "--routing", type=Path, default=ROOT / "config/orca-model-routing.yaml"
    )
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--once", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.poll_seconds <= 0:
        raise SystemExit("--poll-seconds must be positive")
    projects = args.projects.resolve()
    projects.mkdir(parents=True, exist_ok=True)
    load_routing(args.routing)
    runner = OrcaRunner(ROOT, args.routing)
    coordinator = Coordinator(projects, runner)
    _log("coordinator_started", projects=str(projects), once=args.once)
    while True:
        processed = False
        try:
            processed = coordinator.process_next()
            if processed:
                _log("job_settled_or_advanced")
        except Exception as exc:
            _log("coordinator_iteration_failed", error=str(exc))
        if args.once:
            return 0
        if not processed:
            time.sleep(args.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
