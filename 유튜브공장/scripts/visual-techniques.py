#!/usr/bin/env python3
"""Read-only CLI for the YouTube Factory visual-technique registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.visual_technique_registry import (  # noqa: E402
    audit_registry,
    load_registry,
    search_techniques,
    select_techniques,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit, search, or select from the project-local technique catalog."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("audit", help="Validate schema, local paths, and source locks.")

    search = commands.add_parser("search", help="Search active and dormant entries.")
    search.add_argument("query")
    search.add_argument("--status", action="append", dest="statuses")

    select = commands.add_parser("select", help="Select a route-safe technique set.")
    select.add_argument("--intent", action="append", required=True, dest="intents")
    select.add_argument("--phase", required=True)
    select.add_argument("--provider", default="GENERIC")
    select.add_argument("--runtime", default="ANY")
    select.add_argument("--limit", type=int)
    select.add_argument("--include-on-demand", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    registry = load_registry()

    if args.command == "audit":
        findings = audit_registry(registry)
        print(json.dumps({"ok": not findings, "findings": findings}, ensure_ascii=False, indent=2))
        return 0 if not findings else 1

    if args.command == "search":
        payload = search_techniques(args.query, statuses=args.statuses, registry=registry)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    payload = select_techniques(
        intents=args.intents,
        phase=args.phase,
        provider_scope=args.provider,
        render_runtime=args.runtime,
        limit=args.limit,
        include_on_demand=args.include_on_demand,
        registry=registry,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
