from __future__ import annotations

import hashlib
import json

from tools.video.media_review_pipeline import run_media_review


def write_json(path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_pipeline_writes_review_progress_and_nonhuman_checkpoint(tmp_path) -> None:
    project = tmp_path / "pilot"
    manifest = {
        "schema_version": "1.0.0",
        "project_id": "pilot",
        "collection_status": "completed",
        "generated_at": "2026-08-13T00:00:00+00:00",
        "queries": [],
        "source_summary": {
            "attempted": [], "completed": [], "failed": [], "discovered": 0,
            "accepted": 0, "downloaded": 0, "duplicates": 0, "rejected_counts": {},
        },
        "items": [],
    }
    write_json(project / "artifacts/media_collection_manifest.json", manifest)
    write_json(
        project / "artifacts/topic_selection.json",
        {"selected_candidate_id": "rana-plaza"},
    )
    write_json(
        project / "artifacts/topic_shortlist.json",
        {"candidates": [{
            "id": "rana-plaza", "title": "라나 플라자 붕괴",
            "location": "Savar, Bangladesh", "collapse_date": "2013-04-24",
        }]},
    )
    result = run_media_review(
        project,
        supplement=False,
        generated_at="2026-08-13T00:00:00+00:00",
    )
    review_path = project / "artifacts/media_relevance_review.json"
    progress = json.loads(
        (project / "automation/progress/media_relevance_review.json").read_text()
    )
    checkpoint = json.loads((project / "checkpoint_media_relevance_review.json").read_text())
    assert result == json.loads(review_path.read_text())
    assert result["base_manifest_sha256"] == hashlib.sha256(
        (project / "artifacts/media_collection_manifest.json").read_bytes()
    ).hexdigest()
    assert progress["state"] == "completed"
    assert checkpoint["status"] == "completed"
    assert checkpoint["human_approval_required"] is False
    assert checkpoint["human_approved"] is False
    assert checkpoint["artifacts"]["media_relevance_review"] == result


def test_pipeline_does_not_rewrite_collection_manifest(tmp_path) -> None:
    project = tmp_path / "pilot"
    manifest_path = project / "artifacts/media_collection_manifest.json"
    write_json(manifest_path, {
        "schema_version": "1.0.0", "project_id": "pilot", "collection_status": "completed",
        "generated_at": "2026-08-13T00:00:00+00:00", "queries": [],
        "source_summary": {"attempted": [], "completed": [], "failed": [], "discovered": 0,
                           "accepted": 0, "downloaded": 0, "duplicates": 0, "rejected_counts": {}},
        "items": [],
    })
    write_json(project / "artifacts/topic_selection.json", {"selected_candidate_id": "test-collapse"})
    write_json(project / "artifacts/topic_shortlist.json", {"candidates": [{
        "id": "test-collapse", "title": "Test collapse", "location": "Test City",
        "collapse_date": "2000-01-01",
    }]})
    before = manifest_path.read_bytes()
    run_media_review(project, supplement=False)
    assert manifest_path.read_bytes() == before
