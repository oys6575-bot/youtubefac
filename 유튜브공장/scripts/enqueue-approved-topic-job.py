#!/usr/bin/env python3
"""Queue one explicitly approved pre-feature topic without changing its receipt."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backlot.mobile_actions import enqueue_approved_topic_job


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projects", type=Path, required=True)
    parser.add_argument("--project", required=True)
    parser.add_argument("--receipt", required=True)
    args = parser.parse_args()
    created = enqueue_approved_topic_job(
        args.projects, args.project, args.receipt
    )
    print(
        json.dumps(
            {
                "ok": True,
                "project_id": args.project,
                "receipt_id": args.receipt,
                "job_created": created,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
