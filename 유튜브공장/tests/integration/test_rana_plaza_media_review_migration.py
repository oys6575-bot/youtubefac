from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def dump(path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_existing_collection_migration_excludes_known_wrong_and_preserves_bytes(tmp_path) -> None:
    project = tmp_path / "rana"
    assets = []
    descriptors = [
        ("MEDIA_PEXELS_12734648", "war-in-ukraine-ruined-building"),
        ("MEDIA_PEXELS_15554614", "syria-earthquake-devastation"),
        ("MEDIA_PEXELS_14673884", "gray-rocks-on-shore"),
    ]
    for media_id, slug in descriptors:
        path = project / f"assets/source/images/{media_id}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(media_id.encode())
        assets.append({
            "id": media_id, "media_type": "image",
            "local_path": path.relative_to(project).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "source": "pexels", "source_url": f"https://pexels.com/photo/{slug}",
            "direct_url": None, "creator": "", "license": "Pexels License",
            "license_url": "https://www.pexels.com/license/", "public_domain_basis": None,
            "attribution_required": False, "attribution_text": "",
            "allowed_uses": ["display", "transform", "commercial"],
            "accessed_at": "2026-08-13T00:00:00+00:00", "claim_ids": ["CLAIM_INCIDENT"],
            "technical": {"format": "jpg", "width": 1, "height": 1,
                          "duration_seconds": 0, "size_bytes": path.stat().st_size},
        })
    manifest = {
        "schema_version": "1.0.0", "project_id": "rana", "collection_status": "completed",
        "generated_at": "2026-08-13T00:00:00+00:00", "queries": [],
        "source_summary": {"attempted": ["pexels"], "completed": ["pexels"], "failed": [],
                           "discovered": 3, "accepted": 3, "downloaded": 3,
                           "duplicates": 0, "rejected_counts": {}},
        "items": assets,
    }
    dump(project / "artifacts/media_collection_manifest.json", manifest)
    dump(project / "artifacts/topic_selection.json", {"selected_candidate_id": "rana-plaza"})
    dump(project / "artifacts/topic_shortlist.json", {"candidates": [{
        "id": "rana-plaza", "title": "라나 플라자 붕괴", "location": "Savar, Bangladesh",
        "collapse_date": "2013-04-24",
    }]})
    before = {path: path.read_bytes() for path in [
        project / "artifacts/media_collection_manifest.json",
        *(project / row["local_path"] for row in assets),
    ]}
    subprocess.run([
        str(ROOT / ".venv/bin/python"), str(ROOT / "scripts/review-existing-media.py"),
        "--project", str(project), "--apply", "--no-supplement",
    ], cwd=ROOT, check=True, capture_output=True, text=True)
    review = json.loads((project / "artifacts/media_relevance_review.json").read_text())
    excluded = {row["media_id"] for row in review["decisions"] if row["eligibility"] != "eligible"}
    assert excluded == {row[0] for row in descriptors}
    assert all(path.read_bytes() == value for path, value in before.items())
    checkpoint = json.loads((project / "checkpoint_media_relevance_review.json").read_text())
    assert checkpoint["human_approved"] is False
