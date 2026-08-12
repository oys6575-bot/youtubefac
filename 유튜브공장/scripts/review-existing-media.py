#!/usr/bin/env python3
"""Review an existing immutable collection, with an explicit apply boundary."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from schemas.artifacts import validate_artifact
from tools.video.media_relevance_review import review_manifest
from tools.video.media_review_pipeline import run_media_review, topic_identity_from_project


def tracked_hashes(project: Path, manifest: dict) -> dict[str, str]:
    paths = [project / "artifacts/media_collection_manifest.json"]
    paths.extend(project / row["local_path"] for row in manifest.get("items", []))
    return {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--no-supplement", action="store_true")
    parser.add_argument("--max-items-per-query", type=int, default=8)
    parser.add_argument("--archive-source", action="append", dest="archive_sources")
    parser.add_argument("--reuse-existing-supplement", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    manifest_path = project / "artifacts/media_collection_manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    baseline = tracked_hashes(project, manifest)
    now = datetime.now(timezone.utc).isoformat()

    if args.apply:
        review = run_media_review(
            project,
            supplement=not args.no_supplement,
            max_items_per_query=args.max_items_per_query,
            generated_at=now,
            archive_source_names=tuple(args.archive_sources) if args.archive_sources else None,
            reuse_existing_supplement=args.reuse_existing_supplement,
        )
    else:
        review = review_manifest(
            manifest,
            hashlib.sha256(manifest_bytes).hexdigest(),
            topic_identity_from_project(project),
            generated_at=now,
        )
        validate_artifact("media_relevance_review", review)
        report = Path(tempfile.mkdtemp(prefix="ytf-media-review-")) / "media_relevance_review.json"
        report.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"dry_run": True, "report": str(report), "counts": review["counts"]}, ensure_ascii=False))

    final = tracked_hashes(project, manifest)
    if baseline != final:
        raise RuntimeError("immutable base manifest or source bytes changed")
    known_wrong = {
        row["media_id"]: row["eligibility"]
        for row in review["decisions"]
        if row["media_id"] in {
            "MEDIA_PEXELS_12734648", "MEDIA_PEXELS_15554614",
            "MEDIA_PEXELS_15554615", "MEDIA_PEXELS_15650838",
            "MEDIA_PEXELS_14673884", "MEDIA_PEXELS_17386637",
        }
    }
    if any(value == "eligible" for value in known_wrong.values()):
        raise RuntimeError("known wrong-event fixture entered eligible pool")
    if args.apply:
        print(json.dumps({
            "applied": True, "counts": review["counts"], "known_wrong": known_wrong,
            "base_files_preserved": len(baseline),
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
