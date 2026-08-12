#!/usr/bin/env python3
"""Recover one exactly identified crash-left local resource lease."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from lib.resource_lease import LeaseConflictError, ResourceLease


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", required=True, type=Path)
    parser.add_argument("--expected-owner", required=True)
    args = parser.parse_args()

    lease = ResourceLease(
        args.lock,
        lane="local_text",
        owner="control-recovery",
        ttl_seconds=60,
    )
    try:
        payload = lease.recover_stale(
            authority="control",
            expected_owner=args.expected_owner,
        )
    except (LeaseConflictError, PermissionError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "recovered_owner": payload["owner"],
                "recovered_lane": payload["lane"],
                "dead_pid": payload["pid"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
