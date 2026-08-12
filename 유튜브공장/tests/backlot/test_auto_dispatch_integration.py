from __future__ import annotations

import hashlib
import json
from pathlib import Path

from backlot.auto_dispatch import load_job
from backlot.auto_dispatch_worker import Coordinator
from backlot.mobile_actions import Actor, enqueue_approved_topic_job, execute_action
from backlot.mobile_state import build_mobile_state
from tests.backlot.mobile_fixtures import build_topic_gate
from tests.backlot.test_auto_dispatch_worker import FakeRunner, policy_failure
from tests.backlot.test_mobile_actions import payload


ACTOR = Actor(tailscale_login="owner@example.com", tailscale_user_id="123")


def test_approval_runs_to_proposal_human_gate_without_later_work(
    tmp_path: Path,
) -> None:
    project, candidate, expected = build_topic_gate(tmp_path)

    execute_action(tmp_path, payload(candidate, expected), ACTOR)
    Coordinator(
        project.parent,
        FakeRunner(["success", "success", "success", "success"]),
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
        FakeRunner(["success", "success", policy_failure("evidence_lock")]),
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
