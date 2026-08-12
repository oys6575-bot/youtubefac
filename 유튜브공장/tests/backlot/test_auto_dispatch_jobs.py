from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from backlot.auto_dispatch import JobValidationError, load_job, validate_job
from backlot.mobile_actions import Actor, execute_action
from tests.backlot.mobile_fixtures import build_topic_gate
from tests.backlot.test_mobile_actions import payload


ACTOR = Actor(tailscale_login="owner@example.com", tailscale_user_id="123")


def test_topic_approval_atomically_creates_one_queued_job(tmp_path: Path) -> None:
    project, candidate_id, expected = build_topic_gate(tmp_path)

    result = execute_action(tmp_path, payload(candidate_id, expected), ACTOR)

    jobs = list((project / "automation/jobs").glob("*.json"))
    assert len(jobs) == 1
    job = load_job(jobs[0])
    assert job["job_id"] == result.receipt["receipt_id"]
    assert job["trigger_receipt_path"] == (
        f"approvals/receipts/{result.receipt['receipt_id']}.json"
    )
    assert job["trigger_checkpoint_sha256"] == result.receipt[
        "resulting_checkpoint_sha256"
    ]
    assert job["selected_candidate_id"] == candidate_id
    assert job["state"] == "queued"
    assert job["current_stage"] == "research"
    assert job["stages"] == [
        "research",
        "media_collection",
        "evidence_lock",
        "proposal",
    ]
    assert job["attempt"] == 0
    assert job["max_retries"] == 1
    assert job["stage_results"] == []
    assert job["last_error"] is None


def test_idempotent_replay_creates_no_second_job(tmp_path: Path) -> None:
    project, candidate_id, expected = build_topic_gate(tmp_path)
    action = payload(candidate_id, expected)

    first = execute_action(tmp_path, action, ACTOR)
    second = execute_action(tmp_path, action, ACTOR)

    assert second.replayed is True
    assert first.receipt == second.receipt
    assert len(list((project / "automation/jobs").glob("*.json"))) == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("command", "do something"),
        ("provider", "paid"),
        ("model", "arbitrary"),
        ("stages", ["research", "script"]),
        ("max_retries", 2),
    ],
)
def test_job_contract_rejects_unsafe_or_drifted_fields(
    tmp_path: Path, field: str, value: object
) -> None:
    project, candidate_id, expected = build_topic_gate(tmp_path)
    execute_action(tmp_path, payload(candidate_id, expected), ACTOR)
    job = json.loads(next((project / "automation/jobs").glob("*.json")).read_text())
    mutated = deepcopy(job)
    mutated[field] = value

    with pytest.raises(JobValidationError):
        validate_job(mutated)
