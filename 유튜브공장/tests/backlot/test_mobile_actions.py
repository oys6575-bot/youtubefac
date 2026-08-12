from __future__ import annotations

import json
from pathlib import Path

import pytest

from backlot.mobile_actions import (
    ActionConflict,
    ActionValidationError,
    Actor,
    checkpoint_sha256,
    execute_action,
)
from tests.backlot.mobile_fixtures import build_topic_gate


def payload(candidate_id: str, checkpoint_hash: str, **updates: object) -> dict:
    value = {
        "action": "approve_topic",
        "project_id": "MOBILE_TEST",
        "stage": "topic_approval",
        "expected_checkpoint_sha256": checkpoint_hash,
        "idempotency_key": "019ff4c2-6ca0-7aa0-b100-891f1935c102",
        "selected_candidate_id": candidate_id,
    }
    value.update(updates)
    return value


def test_approve_topic_updates_canonical_state_and_writes_receipt(tmp_path: Path) -> None:
    project_dir, candidate_id, expected = build_topic_gate(tmp_path)

    result = execute_action(
        tmp_path,
        payload(candidate_id, expected),
        Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
        now="2026-08-12T10:20:00+00:00",
    )

    checkpoint = json.loads((project_dir / "checkpoint_topic_approval.json").read_text())
    selection = json.loads((project_dir / "artifacts/topic_selection.json").read_text())
    assert checkpoint["status"] == "completed"
    assert checkpoint["human_approved"] is True
    assert checkpoint["artifacts"]["topic_selection"] == selection
    assert selection["selection_status"] == "APPROVED"
    assert selection["selected_candidate_id"] == candidate_id
    assert result.receipt["resulting_checkpoint_sha256"] == checkpoint_sha256(
        project_dir, "topic_approval"
    )
    assert len(list((project_dir / "approvals/receipts").glob("*.json"))) == 1
    assert len(list((project_dir / "history").glob("checkpoint_topic_approval_*.json"))) == 1


def test_stale_checkpoint_is_rejected_without_writes(tmp_path: Path) -> None:
    project_dir, candidate_id, _expected = build_topic_gate(tmp_path)
    before = {p.relative_to(project_dir): p.read_bytes() for p in project_dir.rglob("*") if p.is_file()}

    with pytest.raises(ActionConflict, match="stale_checkpoint"):
        execute_action(
            tmp_path,
            payload(candidate_id, "0" * 64),
            Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
        )

    after = {p.relative_to(project_dir): p.read_bytes() for p in project_dir.rglob("*") if p.is_file()}
    assert after == before


@pytest.mark.parametrize("extra", [
    {"path": "/tmp/escape"},
    {"command": "rm -rf something"},
    {"provider": "paid-api"},
    {"status": "completed"},
    {"model": "arbitrary"},
])
def test_client_cannot_supply_implementation_fields(tmp_path: Path, extra: dict) -> None:
    _project_dir, candidate_id, expected = build_topic_gate(tmp_path)
    with pytest.raises(ActionValidationError, match="payload"):
        execute_action(
            tmp_path,
            payload(candidate_id, expected, **extra),
            Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
        )


def test_candidate_must_have_passed_exact_verification(tmp_path: Path) -> None:
    project_dir, candidate_id, expected = build_topic_gate(tmp_path)
    verification_path = project_dir / "artifacts/topic_verification.json"
    verification = json.loads(verification_path.read_text())
    verification["candidate_results"][0]["verdict"] = "FAIL"
    verification_path.write_text(json.dumps(verification), encoding="utf-8")

    with pytest.raises(ActionValidationError, match="candidate_not_verified"):
        execute_action(
            tmp_path,
            payload(candidate_id, expected),
            Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
        )


def test_project_traversal_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ActionValidationError, match="project_id"):
        execute_action(
            tmp_path,
            {
                "action": "approve_gate",
                "project_id": "../outside",
                "stage": "publish",
                "expected_checkpoint_sha256": "0" * 64,
                "idempotency_key": "safe-key-12345678",
            },
            Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
        )


def test_high_impact_gate_requires_server_side_typed_confirmation(tmp_path: Path) -> None:
    project = tmp_path / "MOBILE_BUDGET"
    project.mkdir()
    checkpoint = {
        "version": "1.0",
        "project_id": "MOBILE_BUDGET",
        "pipeline_type": "youtube-factory",
        "stage": "budget",
        "status": "awaiting_human",
        "timestamp": "2026-08-12T00:00:00+00:00",
        "checkpoint_policy": "guided",
        "human_approval_required": True,
        "human_approved": False,
        "artifacts": {},
    }
    path = project / "checkpoint_budget.json"
    path.write_text(json.dumps(checkpoint), encoding="utf-8")
    expected = checkpoint_sha256(project, "budget")

    with pytest.raises(ActionValidationError, match="two_step_confirmation_required"):
        execute_action(
            tmp_path,
            {
                "action": "approve_gate",
                "project_id": "MOBILE_BUDGET",
                "stage": "budget",
                "expected_checkpoint_sha256": expected,
                "idempotency_key": "budget-confirm-0001",
            },
            Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
        )
