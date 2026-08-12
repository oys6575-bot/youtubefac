"""Hash-bound media inventory shared by the dashboard and OpenMontage selection."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path


RECOMMENDED_CATEGORIES = frozenset(
    {"event_direct", "news_report", "official_record", "explanatory"}
)


def _read(path: Path) -> dict | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _loaded(project: Path) -> tuple[list[dict], dict[str, dict], bool]:
    manifest_path = project / "artifacts/media_collection_manifest.json"
    manifest = _read(manifest_path) or {}
    base_items = [row for row in manifest.get("items", []) if isinstance(row, dict)]
    review = _read(project / "artifacts/media_relevance_review.json") or {}
    try:
        digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    except OSError:
        digest = ""
    valid = bool(digest and review.get("base_manifest_sha256") == digest)
    items = list(base_items)
    if valid and isinstance(review.get("supplement_manifest"), dict):
        items.extend(
            row
            for row in review["supplement_manifest"].get("items", [])
            if isinstance(row, dict)
        )
    decisions = {
        row.get("media_id"): row
        for row in review.get("decisions", [])
        if valid and isinstance(row, dict) and isinstance(row.get("media_id"), str)
    }
    return items, decisions, valid


def all_reviewed_items(project: str | Path) -> list[dict]:
    """Return every collected item with fail-closed review projections."""
    items, decisions, review_valid = _loaded(Path(project))
    output = []
    seen = set()
    for item in sorted(items, key=lambda row: str(row.get("id") or "")):
        media_id = item.get("id")
        if not isinstance(media_id, str) or media_id in seen:
            continue
        seen.add(media_id)
        decision = decisions.get(media_id)
        decision_valid = bool(
            decision and decision.get("media_sha256") == item.get("sha256")
        )
        row = deepcopy(item)
        if review_valid and decision_valid:
            category = decision["category"]
            eligibility = decision["eligibility"]
            reason = str(decision.get("usefulness") or "reviewed")
        else:
            category = "unknown"
            eligibility = "held"
            reason = "automatic relevance review is missing or no longer matches these bytes"
        row.update(
            {
                "category": category,
                "eligibility": eligibility,
                "review_reason": reason,
                "recommended": (
                    eligibility == "eligible" and category in RECOMMENDED_CATEGORIES
                ),
            }
        )
        output.append(row)
    return output


def eligible_items_for_openmontage(
    project: str | Path, *, allow_generic: bool = False
) -> list[dict]:
    """Return the production-safe pool; generic B-roll needs explicit later opt-in."""
    allowed = set(RECOMMENDED_CATEGORIES)
    if allow_generic:
        allowed.add("generic_broll")
    return [
        row
        for row in all_reviewed_items(project)
        if row["category"] in allowed
        and (row["eligibility"] == "eligible" or (allow_generic and row["category"] == "generic_broll"))
    ]
