#!/usr/bin/env python3
"""Run one local-heavy command under the factory's atomic resource lease."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Callable

from lib.resource_lease import LeaseConflictError, ResourceLease


Runner = Callable[[list[str]], int]


def _run(command: list[str]) -> int:
    return subprocess.run(command, check=False).returncode


def run_with_lease(
    lock_path: Path,
    *,
    lane: str,
    owner: str,
    command: list[str],
    runner: Runner = _run,
    ttl_seconds: int = 14400,
) -> int:
    if not command:
        raise ValueError("command cannot be empty")
    lease = ResourceLease(
        lock_path,
        lane=lane,
        owner=owner,
        ttl_seconds=ttl_seconds,
    )
    lease.acquire()
    try:
        return runner(command)
    finally:
        lease.release()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", required=True, type=Path)
    parser.add_argument("--lane", required=True, choices=["local_text", "local_media"])
    parser.add_argument("--owner", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    try:
        return run_with_lease(
            args.lock,
            lane=args.lane,
            owner=args.owner,
            command=command,
        )
    except LeaseConflictError as exc:
        print(f"RESOURCE_LANE_BUSY: {exc}")
        return 75


if __name__ == "__main__":
    raise SystemExit(main())

