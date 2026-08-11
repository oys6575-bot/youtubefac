#!/usr/bin/env python3
"""Offline sync, audit, search, and bounded-pack CLI for factory knowledge."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.knowledge_vault import (  # noqa: E402
    KnowledgeVaultError,
    audit_vault,
    load_knowledge_sources,
    resolve_knowledge_pack,
    search_vault,
    sync_vault,
)


def _emit(payload: Any, *, stream: Any = sys.stdout) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=stream)


def _resolve_input(root: Path, value: Path) -> Path:
    return value if value.is_absolute() else root / value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage the project-local, offline Obsidian knowledge vault."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Factory project root (defaults to this repository).",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="Materialize canonical cards without deleting notes.")
    commands.add_parser("audit", help="Report drift, broken links, and unsafe state.")

    search = commands.add_parser("search", help="Search all indexed knowledge statuses.")
    search.add_argument("query")
    search.add_argument(
        "--type",
        dest="entity_types",
        action="append",
        help="Optional entity type filter; may be repeated.",
    )

    pack = commands.add_parser("pack", help="Resolve an approved technique selection.")
    pack.add_argument("--selection", type=Path, required=True)
    pack.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root = args.root.resolve()
    try:
        sources = load_knowledge_sources(root=root)
        if args.command == "sync":
            _emit(asdict(sync_vault(sources, root=root)))
            return 0
        if args.command == "audit":
            findings = audit_vault(sources, root=root)
            _emit({"ok": not findings, "findings": findings})
            return 0 if not findings else 1
        if args.command == "search":
            entity_types = tuple(args.entity_types) if args.entity_types else None
            _emit(
                search_vault(
                    args.query,
                    entity_types=entity_types,
                    root=root,
                )
            )
            return 0
        if args.command == "pack":
            selection_path = _resolve_input(root, args.selection)
            selection = json.loads(selection_path.read_text(encoding="utf-8"))
            payload = resolve_knowledge_pack(selection, sources=sources, root=root)
            if args.output:
                output_path = _resolve_input(root, args.output)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                _emit({"ok": True, "output": output_path.relative_to(root).as_posix()})
            else:
                _emit(payload)
            return 0
    except (KnowledgeVaultError, OSError, json.JSONDecodeError) as exc:
        _emit({"ok": False, "error": str(exc)}, stream=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
