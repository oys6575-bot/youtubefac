from __future__ import annotations

import hashlib
import json

from lib.reviewed_media_inventory import (
    all_reviewed_items,
    eligible_items_for_openmontage,
)


def dump(path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def build_project(tmp_path):
    project = tmp_path / "pilot"
    categories = [
        ("EVENT", "event_direct", "eligible"),
        ("NEWS", "news_report", "eligible"),
        ("OFFICIAL", "official_record", "eligible"),
        ("EXPLAIN", "explanatory", "eligible"),
        ("GENERIC", "generic_broll", "excluded"),
        ("WRONG", "unrelated", "excluded"),
        ("UNKNOWN", "unknown", "held"),
    ]
    items = [{
        "id": f"MEDIA_{name}", "sha256": (str(index) * 64)[:64],
        "media_type": "image", "local_path": f"assets/source/images/{name}.jpg",
        "technical": {},
    } for index, (name, _category, _eligibility) in enumerate(categories, start=1)]
    manifest = {"project_id": "pilot", "items": items, "queries": []}
    manifest_path = project / "artifacts/media_collection_manifest.json"
    dump(manifest_path, manifest)
    decisions = [{
        "media_id": f"MEDIA_{name}", "media_sha256": items[index]["sha256"],
        "category": category, "eligibility": eligibility,
        "usefulness": f"{category} reason",
    } for index, (name, category, eligibility) in enumerate(categories)]
    dump(project / "artifacts/media_relevance_review.json", {
        "base_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "supplement_manifest": None, "decisions": decisions,
    })
    return project


def test_openmontage_inventory_excludes_unrelated_unknown_and_generic_by_default(tmp_path) -> None:
    project = build_project(tmp_path)
    ids = {item["id"] for item in eligible_items_for_openmontage(project)}
    assert ids == {"MEDIA_EVENT", "MEDIA_NEWS", "MEDIA_OFFICIAL", "MEDIA_EXPLAIN"}
    with_generic = {item["id"] for item in eligible_items_for_openmontage(project, allow_generic=True)}
    assert "MEDIA_GENERIC" in with_generic
    assert "MEDIA_WRONG" not in with_generic
    assert "MEDIA_UNKNOWN" not in with_generic


def test_inventory_projects_review_fields_and_preserves_excluded(tmp_path) -> None:
    rows = all_reviewed_items(build_project(tmp_path))
    wrong = next(row for row in rows if row["id"] == "MEDIA_WRONG")
    assert wrong["category"] == "unrelated"
    assert wrong["eligibility"] == "excluded"
    assert wrong["review_reason"] == "unrelated reason"


def test_tampered_base_manifest_fails_closed(tmp_path) -> None:
    project = build_project(tmp_path)
    manifest_path = project / "artifacts/media_collection_manifest.json"
    manifest_path.write_bytes(manifest_path.read_bytes() + b"\n")
    assert eligible_items_for_openmontage(project) == []
    assert all(row["eligibility"] == "held" for row in all_reviewed_items(project))
