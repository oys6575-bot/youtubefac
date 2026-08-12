from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from backlot.mobile_actions import ActionValidationError, Actor, execute_action
from tests.backlot.mobile_fixtures import build_topic_gate
from tests.backlot.test_mobile_actions import payload


ACTOR = Actor(tailscale_login="owner@example.com", tailscale_user_id="123")


def test_four_concurrent_retries_create_exactly_one_receipt(tmp_path: Path) -> None:
    project, candidate_id, expected = build_topic_gate(tmp_path)
    action = payload(candidate_id, expected)

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda _: execute_action(tmp_path, action, ACTOR), range(4)))

    receipt_ids = {result.receipt["receipt_id"] for result in results}
    assert len(receipt_ids) == 1
    assert sum(not result.replayed for result in results) == 1
    assert len(list((project / "approvals/receipts").glob("*.json"))) == 1
    assert len(list((project / "history").glob("checkpoint_topic_approval_*.json"))) == 1
    assert len(list((project / "approvals/idempotency").glob("*.json"))) == 1


@pytest.mark.parametrize(
    "failpoint",
    [
        "after_prepared",
        "after_target_0",
        "after_target_1",
        "after_target_2",
        "after_target_3",
        "after_target_4",
        "after_target_5",
    ],
)
def test_prepared_transaction_recovers_to_one_complete_decision(
    tmp_path: Path, failpoint: str
) -> None:
    project, candidate_id, expected = build_topic_gate(tmp_path)
    action = payload(candidate_id, expected)

    with pytest.raises(RuntimeError, match="injected failure"):
        execute_action(tmp_path, action, ACTOR, failpoint=failpoint)

    recovered = execute_action(tmp_path, action, ACTOR)
    checkpoint = json.loads((project / "checkpoint_topic_approval.json").read_text())
    selection = json.loads((project / "artifacts/topic_selection.json").read_text())
    journals = [json.loads(path.read_text()) for path in (project / "approvals/transactions").glob("*.json")]

    assert recovered.replayed is True
    assert checkpoint["status"] == "completed"
    assert checkpoint["artifacts"]["topic_selection"] == selection
    assert len(list((project / "approvals/receipts").glob("*.json"))) == 1
    assert len(list((project / "history").glob("checkpoint_topic_approval_*.json"))) == 1
    assert len(list((project / "automation/jobs").glob("*.json"))) == 1
    assert len(journals) == 1
    assert journals[0]["state"] == "completed"


def test_rejection_records_request_but_does_not_change_checkpoint(tmp_path: Path) -> None:
    project, _candidate_id, expected = build_topic_gate(tmp_path)
    action = {
        "action": "reject_gate",
        "project_id": "MOBILE_TEST",
        "stage": "topic_approval",
        "expected_checkpoint_sha256": expected,
        "idempotency_key": "reject-019ff4c2-0001",
        "reason": "공식 자료를 한 건 더 확인해 주세요.",
    }
    before = (project / "checkpoint_topic_approval.json").read_bytes()

    result = execute_action(tmp_path, action, ACTOR)

    assert (project / "checkpoint_topic_approval.json").read_bytes() == before
    requests = list((project / "approvals/review_requests").glob("*.json"))
    assert len(requests) == 1
    assert json.loads(requests[0].read_text())["state"] == "requested"
    assert result.receipt["resulting_checkpoint_sha256"] == expected


def test_rejection_cannot_target_a_gate_that_is_already_completed(tmp_path: Path) -> None:
    project, candidate_id, expected = build_topic_gate(tmp_path)
    execute_action(tmp_path, payload(candidate_id, expected), ACTOR)
    completed_hash = __import__("hashlib").sha256(
        (project / "checkpoint_topic_approval.json").read_bytes()
    ).hexdigest()

    with pytest.raises(ActionValidationError, match="gate_not_awaiting_human"):
        execute_action(
            tmp_path,
            {
                "action": "reject_gate",
                "project_id": "MOBILE_TEST",
                "stage": "topic_approval",
                "expected_checkpoint_sha256": completed_hash,
                "idempotency_key": "late-reject-019ff4c2",
                "reason": "이미 끝난 승인을 뒤늦게 거부",
            },
            ACTOR,
        )
