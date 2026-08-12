from __future__ import annotations

import hashlib
import json
from pathlib import Path

from backlot.auto_dispatch import load_job
from backlot.auto_dispatch_worker import Coordinator
from backlot.orca_auto_dispatch import StageResult
from backlot.mobile_actions import Actor, enqueue_approved_topic_job, execute_action
from backlot.mobile_state import build_mobile_state
from tests.backlot.mobile_fixtures import build_topic_gate
from tests.backlot.test_auto_dispatch_worker import (
    FakeRunner,
    _checkpoint,
    _sha256,
    canonical_bytes,
    policy_failure,
)
from tests.backlot.test_mobile_actions import payload
from tests.tools.test_rights_cleared_media_collection import FakeSource, candidate
from tools.video.rights_cleared_media_collection import RightsClearedMediaCollection


ACTOR = Actor(tailscale_login="owner@example.com", tailscale_user_id="123")


def test_approval_runs_to_proposal_human_gate_without_later_work(
    tmp_path: Path,
) -> None:
    project, candidate, expected = build_topic_gate(tmp_path)

    execute_action(tmp_path, payload(candidate, expected), ACTOR)
    Coordinator(
        project.parent,
        FakeRunner(["success", "success", "success", "success", "success"]),
    ).process_next()

    state = build_mobile_state(project)
    assert state["automation"]["state"] == "awaiting_human"
    assert state["automation"]["label"] == "기획안 승인 대기"
    assert state["current_gate"]["stage"] == "proposal"
    assert not (project / "checkpoint_script.json").exists()
    assert not (project / "checkpoint_visual_plan.json").exists()
    assert not (project / "checkpoint_assets.json").exists()
    assert not (project / "checkpoint_publish.json").exists()


def test_failed_chain_retries_from_last_hash_bound_stage_without_rewriting_history(
    tmp_path: Path,
) -> None:
    project, candidate, expected = build_topic_gate(tmp_path)
    execute_action(tmp_path, payload(candidate, expected), ACTOR)
    Coordinator(
        project.parent,
        FakeRunner(["success", "success", "success", policy_failure("evidence_lock")]),
    ).process_next()
    original_path = next((project / "automation/jobs").glob("*.json"))
    original = load_job(original_path)
    original_bytes = original_path.read_bytes()

    execute_action(
        tmp_path,
        {
            "action": "retry_auto_dispatch",
            "project_id": project.name,
            "retry_job_id": original["job_id"],
            "expected_job_sha256": hashlib.sha256(original_bytes).hexdigest(),
            "idempotency_key": "integration-retry-0001",
            "reason": "정책 문제를 해소한 뒤 검증부터 다시 실행",
        },
        ACTOR,
    )
    retry_path = next(
        path
        for path in (project / "automation/jobs").glob("*.json")
        if path != original_path
    )
    runner = FakeRunner(["success", "success"])

    Coordinator(project.parent, runner).process_next()

    assert original_path.read_bytes() == original_bytes
    assert runner.calls == ["evidence_lock", "proposal"]
    retry = load_job(retry_path)
    assert retry["state"] == "awaiting_human"
    assert [item["stage"] for item in retry["stage_results"]] == [
            "research",
            "media_collection",
            "media_relevance_review",
            "evidence_lock",
        "proposal",
    ]


def test_pre_feature_approval_can_be_enqueued_once_without_rewriting_receipt(
    tmp_path: Path,
) -> None:
    project, candidate, expected = build_topic_gate(tmp_path)
    result = execute_action(tmp_path, payload(candidate, expected), ACTOR)
    job_path = project / f"automation/jobs/{result.receipt['receipt_id']}.json"
    job_path.unlink()
    transaction_path = project / f"approvals/transactions/{result.receipt['receipt_id']}.json"
    transaction = json.loads(transaction_path.read_text())
    transaction["targets"] = [
        target
        for target in transaction["targets"]
        if not target["path"].startswith("automation/jobs/")
    ]
    transaction_path.write_text(json.dumps(transaction), encoding="utf-8")
    receipt_path = project / f"approvals/receipts/{result.receipt['receipt_id']}.json"
    receipt_bytes = receipt_path.read_bytes()

    first = enqueue_approved_topic_job(
        tmp_path, project.name, result.receipt["receipt_id"]
    )
    second = enqueue_approved_topic_job(
        tmp_path, project.name, result.receipt["receipt_id"]
    )

    assert first is True
    assert second is False
    assert receipt_path.read_bytes() == receipt_bytes
    assert len(list((project / "automation/jobs").glob("*.json"))) == 1


def test_collection_integration_freezes_only_usable_media_and_embeds_manifest(
    tmp_path: Path, monkeypatch
) -> None:
    class FailedSource(FakeSource):
        name = "failed"

        def search(self, query, filters):
            del query, filters
            raise RuntimeError("temporary source failure")

    project = tmp_path / "INTEGRATION_MEDIA"
    project.mkdir()
    usable = FakeSource(
        [
            candidate(source_id="1001", license="CC BY 4.0"),
            candidate(source_id="1002", license="Permission required"),
            candidate(source_id="1003", license="CC0 1.0"),
        ],
        payload=b"same-rights-cleared-bytes" * 256,
    )
    monkeypatch.setattr(
        "tools.video.stock_sources.available_sources",
        lambda: [FailedSource([]), usable],
    )

    collected = RightsClearedMediaCollection().execute(
        {
            "project_id": project.name,
            "output_dir": str(project / "assets/source"),
            "queries": [{"query": "collapse archive", "kind": "image", "claim_ids": []}],
        }
    )

    assert collected.success is True
    manifest = collected.data["manifest"]
    assert manifest["collection_status"] == "partial"
    assert manifest["source_summary"]["accepted"] == 2
    assert manifest["source_summary"]["duplicates"] == 1
    assert manifest["source_summary"]["rejected_counts"] == {
        "permission_required": 1
    }
    assert usable.download_calls == ["fake_1001", "fake_1003"]
    assert len(list((project / "assets/source/images").iterdir())) == 1
    assert all("selected_for_edit" not in item for item in manifest["items"])

    artifact = project / "artifacts/media_collection_manifest.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(canonical_bytes(manifest))
    checkpoint = _checkpoint(
        project,
        "media_collection",
        "completed",
        {"media_collection_manifest": manifest},
    )
    progress = project / "automation/progress/media_collection.json"
    paths = [
        artifact.relative_to(project).as_posix(),
        progress.relative_to(project).as_posix(),
        checkpoint.relative_to(project).as_posix(),
    ]
    stage_result = StageResult(
        outcome="success",
        artifact_paths=paths,
        artifact_sha256={path: _sha256(project / path) for path in paths},
        source_commit="a" * 40,
        verdict="NOT_APPLICABLE",
        run_id="run_media",
        task_id="task_media",
        dispatch_id="dispatch_media",
    )

    Coordinator(project.parent, FakeRunner([]))._validate_success(
        project, "media_collection", stage_result
    )
    stored_checkpoint = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert stored_checkpoint["artifacts"]["media_collection_manifest"] == manifest
    for item in manifest["items"]:
        assert _sha256(project / item["local_path"]) == item["sha256"]
