"""Exact-event archive supplementation for gaps found by relevance review."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from tools.video.rights_cleared_media_collection import RightsClearedMediaCollection


ARCHIVE_SOURCE_ALLOWLIST = (
    "archive_org",
    "wikimedia",
    "nara",
    "loc",
    "pond5_pd",
)

_LANE_QUERIES = {
    "event_site": ("{event} {location} collapse", "image", ["CLAIM_EVENT_SITE"]),
    "warning_cracks": ("{event} cracks warning day before collapse", "image", ["CLAIM_WARNING_CRACKS"]),
    "aftermath_rescue": ("{event} rescue aftermath", "video", ["CLAIM_AFTERMATH_RESCUE"]),
    "news_newspaper": ("{event} news report newspaper 2013", "any", ["CLAIM_NEWS_REPORT"]),
    "official_record": ("{event} ILO official record report", "document", ["CLAIM_OFFICIAL_RECORD"]),
    "map_structure": ("{event} building plan site map", "image", ["CLAIM_MAP_STRUCTURE"]),
}


def build_supplement_queries(topic_identity: dict, missing: set[str]) -> list[dict]:
    """Return exact-event queries only for review lanes that remain uncovered."""
    event = str(topic_identity["canonical_name"])
    location = " ".join(topic_identity.get("locations", [])[:2])
    rows = []
    for lane in sorted(missing):
        template = _LANE_QUERIES.get(lane)
        if not template:
            continue
        text, kind, claim_ids = template
        rows.append(
            {
                "lane": lane,
                "query": text.format(event=event, location=location).strip(),
                "kind": kind,
                "claim_ids": claim_ids,
            }
        )
    return rows


def _empty_manifest(project_id: str, generated_at: str) -> dict:
    return {
        "schema_version": "1.0.0",
        "project_id": project_id,
        "collection_status": "completed",
        "generated_at": generated_at,
        "queries": [],
        "source_summary": {
            "attempted": [],
            "completed": [],
            "failed": [],
            "discovered": 0,
            "accepted": 0,
            "downloaded": 0,
            "duplicates": 0,
            "rejected_counts": {},
        },
        "items": [],
    }


def _available_archive_names() -> tuple[str, ...]:
    from tools.video.stock_sources import available_sources

    names = {source.name for source in available_sources()}
    return tuple(name for name in ARCHIVE_SOURCE_ALLOWLIST if name in names)


def collect_archive_supplement(
    *,
    project_id: str,
    output_dir: str | Path,
    topic_identity: dict,
    missing_lanes: set[str],
    collector: RightsClearedMediaCollection | None = None,
    available_source_names: Iterable[str] | None = None,
    max_items_per_query: int = 8,
    generated_at: str | None = None,
) -> dict:
    """Collect reusable exact-event archive material without stock fallbacks."""
    generated_at = generated_at or datetime.now(timezone.utc).isoformat()
    specs = build_supplement_queries(topic_identity, missing_lanes)
    if not specs:
        return _empty_manifest(project_id, generated_at)

    names = set(available_source_names if available_source_names is not None else _available_archive_names())
    sources = [name for name in ARCHIVE_SOURCE_ALLOWLIST if name in names]
    if not sources:
        return _empty_manifest(project_id, generated_at)

    inputs = {
        "project_id": project_id,
        "output_dir": str(Path(output_dir)),
        "queries": [
            {"query": row["query"], "kind": row["kind"], "claim_ids": row["claim_ids"]}
            for row in specs
        ],
        "sources": sources,
        "max_items_per_query": max_items_per_query,
    }
    result = (collector or RightsClearedMediaCollection()).execute(inputs)
    if not result.success:
        raise RuntimeError(f"archive supplement failed: {result.error}")
    return result.data["manifest"]

