"""Mandatory collection -> relevance review pipeline stage."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import uuid

import jsonschema

from lib.checkpoint import validate_checkpoint
from schemas.artifacts import validate_artifact
from tools.video.media_archive_supplement import (
    collect_archive_supplement,
    normalize_supplement_rights,
)
from tools.video.media_relevance_review import review_manifest


ROOT = Path(__file__).resolve().parents[2]
PROGRESS_SCHEMA = ROOT / "schemas/mobile-dashboard/media-relevance-progress.schema.json"


def _read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with open(temporary, "xb") as handle:
            handle.write((json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode())
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def topic_identity_from_project(project: Path) -> dict:
    selection = _read(project / "artifacts/topic_selection.json")
    shortlist = _read(project / "artifacts/topic_shortlist.json")
    selected_id = selection.get("selected_candidate_id")
    candidate = next(
        (row for row in shortlist.get("candidates", []) if row.get("id") == selected_id),
        None,
    )
    if not candidate:
        raise ValueError("selected topic candidate is missing from shortlist")
    slug_name = " ".join(str(selected_id).split("-"))
    english_name = f"{slug_name} collapse" if "collapse" not in slug_name else slug_name
    aliases = [str(candidate.get("title") or ""), slug_name]
    if selected_id == "rana-plaza":
        english_name = "Rana Plaza collapse"
        aliases.extend(["Rana Plaza", "Savar building collapse"])
    research_path = project / "artifacts/research_brief.json"
    if research_path.exists():
        topic = str(_read(research_path).get("topic") or "")
        aliases.extend(re.findall(r"[A-Za-z][A-Za-z\s-]{2,80}(?:collapse|disaster)", topic, re.I))
    location = str(candidate.get("location") or "")
    locations = [part.strip() for part in location.split(",") if part.strip()]
    dates = [str(candidate.get("collapse_date") or "")]
    return {
        "canonical_name": english_name.title().replace(" Collapse", " collapse"),
        "aliases": list(dict.fromkeys(value for value in aliases if value)),
        "locations": list(dict.fromkeys(locations)),
        "dates": [value for value in dates if value],
    }


def _progress(project_id: str, state: str, phase: str, counts: dict, now: str, error=None) -> dict:
    return {
        "version": "1.0",
        "project_id": project_id,
        "state": state,
        "phase": phase,
        "counts": {
            "total": counts.get("total", 0),
            "reviewed": counts.get("total", 0),
            "eligible": counts.get("eligible", 0),
            "excluded": counts.get("excluded", 0),
            "held": counts.get("held", 0),
        },
        "updated_at": now,
        "error": error,
    }


def _write_valid_progress(path: Path, value: dict) -> None:
    schema = json.loads(PROGRESS_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    ).validate(value)
    _atomic_json(path, value)


def run_media_review(
    project: str | Path,
    *,
    supplement: bool = True,
    max_items_per_query: int = 8,
    generated_at: str | None = None,
    archive_source_names: tuple[str, ...] | None = None,
    reuse_existing_supplement: bool = False,
) -> dict:
    """Run base review, gap-only archive supplement, and final canonical review."""
    project = Path(project).resolve()
    now = generated_at or datetime.now(timezone.utc).isoformat()
    manifest_path = project / "artifacts/media_collection_manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    validate_artifact("media_collection_manifest", manifest)
    identity = topic_identity_from_project(project)
    progress_path = project / "automation/progress/media_relevance_review.json"

    try:
        first = review_manifest(
            manifest,
            hashlib.sha256(manifest_bytes).hexdigest(),
            identity,
            generated_at=now,
        )
        _write_valid_progress(
            progress_path,
            _progress(manifest["project_id"], "reviewing", "base_review", first["counts"], now),
        )
        supplement_manifest = None
        if supplement:
            missing = {row["lane"] for row in first["coverage"] if row["status"] == "missing"}
            _write_valid_progress(
                progress_path,
                _progress(
                    manifest["project_id"], "supplementing", "archive_supplement",
                    first["counts"], now,
                ),
            )
            previous = (
                _read(project / "artifacts/media_relevance_review.json")
                if reuse_existing_supplement
                else {}
            )
            if isinstance(previous.get("supplement_manifest"), dict):
                supplement_manifest = previous["supplement_manifest"]
            else:
                supplement_manifest = collect_archive_supplement(
                    project_id=manifest["project_id"],
                    output_dir=project / "assets/source",
                    topic_identity=identity,
                    missing_lanes=missing,
                    max_items_per_query=max_items_per_query,
                    generated_at=now,
                    available_source_names=archive_source_names,
                )
            base_ids = {row["id"] for row in manifest.get("items", [])}
            supplement_manifest = normalize_supplement_rights(supplement_manifest)
            supplement_manifest["items"] = [
                row for row in supplement_manifest.get("items", []) if row["id"] not in base_ids
            ]
            validate_artifact("media_collection_manifest", supplement_manifest)

        final = review_manifest(
            manifest,
            hashlib.sha256(manifest_bytes).hexdigest(),
            identity,
            supplement_manifest=supplement_manifest,
            generated_at=now,
        )
        validate_artifact("media_relevance_review", final)
        review_path = project / "artifacts/media_relevance_review.json"
        _atomic_json(review_path, final)
        _write_valid_progress(
            progress_path,
            _progress(manifest["project_id"], "completed", "settled", final["counts"], now),
        )
        checkpoint = {
            "version": "1.0",
            "project_id": manifest["project_id"],
            "pipeline_type": "youtube-factory",
            "stage": "media_relevance_review",
            "status": "completed",
            "timestamp": now,
            "checkpoint_policy": "guided",
            "human_approval_required": False,
            "human_approved": False,
            "artifacts": {"media_relevance_review": final},
        }
        validate_checkpoint(checkpoint)
        _atomic_json(project / "checkpoint_media_relevance_review.json", checkpoint)
        if manifest_path.read_bytes() != manifest_bytes:
            raise RuntimeError("base collection manifest changed during review")
        return final
    except Exception as exc:
        failed = _progress(
            manifest.get("project_id", project.name), "failed", "settled", {}, now,
            error=f"{type(exc).__name__}: {exc}"[:2000],
        )
        _write_valid_progress(progress_path, failed)
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--no-supplement", action="store_true")
    parser.add_argument("--max-items-per-query", type=int, default=8)
    parser.add_argument("--archive-source", action="append", dest="archive_sources")
    parser.add_argument("--reuse-existing-supplement", action="store_true")
    args = parser.parse_args()
    result = run_media_review(
        args.project,
        supplement=not args.no_supplement,
        max_items_per_query=args.max_items_per_query,
        archive_source_names=tuple(args.archive_sources) if args.archive_sources else None,
        reuse_existing_supplement=args.reuse_existing_supplement,
    )
    print(json.dumps({"ok": True, "counts": result["counts"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
