from __future__ import annotations

import json
from pathlib import Path

from backlot.mobile_state import build_mobile_state
from backlot.mobile_actions import Actor, execute_action
from tests.backlot.mobile_fixtures import build_topic_gate
from tests.backlot.test_mobile_actions import payload


def test_mobile_projection_has_full_stage_gate_candidates_and_roles(tmp_path: Path) -> None:
    project, _candidate, expected_hash = build_topic_gate(tmp_path)

    state = build_mobile_state(project)

    assert state["project"]["project_id"] == "MOBILE_TEST"
    assert state["source_of_truth"] == "openmontage"
    assert len(state["stages"]) == 19
    assert state["current_gate"] == {
        "stage": "topic_approval",
        "checkpoint_sha256": expected_hash,
        "status": "awaiting_human",
        "requires_two_step": False,
        "summary": state["current_gate"]["summary"],
    }
    assert len(state["topic_candidates"]) >= 10
    assert state["topic_candidates"][0]["rank"] == 1
    assert all(candidate["verification"] == "PASS" for candidate in state["topic_candidates"])
    assert {role["role"] for role in state["roles"]} == {
        "control", "research", "verification", "story_visual", "production", "qa"
    }
    assert next(role for role in state["roles"] if role["role"] == "story_visual")["runtime"] == "claude"
    assert state["providers"]["topview"]["mode"] == "manual_semi_automatic"
    assert state["providers"]["youtube"]["status"] == "not_checked"


def test_mobile_projection_uses_only_stored_provider_preflight(tmp_path: Path) -> None:
    project, _candidate, _expected = build_topic_gate(tmp_path)
    report = {
        "checked_at": "2026-08-12T12:00:00+00:00",
        "providers": {
            "youtube": {"status": "connected"},
            "pexels": {"status": "connected"},
        },
    }
    path = project / "system/provider-preflight.json"
    path.parent.mkdir()
    path.write_text(json.dumps(report), encoding="utf-8")

    state = build_mobile_state(project)

    assert state["providers"]["youtube"] == {
        "status": "connected", "checked_at": "2026-08-12T12:00:00+00:00"
    }
    assert state["providers"]["pixabay"]["status"] == "not_checked"
    assert state["providers"]["pixabay"]["checked_at"] is None


def test_missing_optional_files_degrade_to_unavailable(tmp_path: Path) -> None:
    project = tmp_path / "EMPTY_PROJECT"
    project.mkdir()
    (project / "project.json").write_text(
        json.dumps({"project_id": "EMPTY_PROJECT", "title": "Empty", "pipeline_type": "youtube-factory"}),
        encoding="utf-8",
    )

    state = build_mobile_state(project)

    assert state["current_gate"] is None
    assert state["topic_candidates"] == []
    assert state["data_quality"]["topic_candidates"] == "unavailable"


def test_mobile_projection_shows_durable_automation_state(tmp_path: Path) -> None:
    project, candidate, expected = build_topic_gate(tmp_path)
    execute_action(
        tmp_path,
        payload(candidate, expected),
        Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
        now="2026-08-12T12:00:00+00:00",
    )

    state = build_mobile_state(project)

    assert state["automation"]["state"] == "queued"
    assert state["automation"]["current_stage"] == "research"
    assert state["automation"]["label"] == "자료조사 시작 대기"
    assert state["automation"]["can_retry"] is False
    assert len(state["automation"]["job_sha256"]) == 64


def _set_collection_running(project: Path) -> None:
    job_path = next((project / "automation/jobs").glob("*.json"))
    job = json.loads(job_path.read_text(encoding="utf-8"))
    job["state"] = "running"
    job["current_stage"] = "media_collection"
    job["updated_at"] = "2026-08-12T12:05:00+00:00"
    job_path.write_text(json.dumps(job), encoding="utf-8")


def _write_collection_progress(project: Path) -> None:
    path = project / "automation/progress/media_collection.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "version": "1.0",
                "project_id": project.name,
                "state": "downloading",
                "current_source": "pexels",
                "current_query": "Rana Plaza exterior",
                "sources": {
                    "attempted": ["pexels", "pixabay"],
                    "completed": [],
                    "failed": [],
                },
                "counts": {
                    "discovered": 19,
                    "accepted": 7,
                    "downloaded": 6,
                    "duplicates": 1,
                    "rejected": 12,
                },
                "rejected_counts": {"unknown_rights": 8, "restricted_use": 4},
                "elapsed_seconds": 34.2,
                "updated_at": "2026-08-12T12:05:34+00:00",
                "error": None,
            }
        ),
        encoding="utf-8",
    )


def test_mobile_state_exposes_collection_activity(tmp_path: Path) -> None:
    project, candidate, expected = build_topic_gate(tmp_path)
    execute_action(
        tmp_path,
        payload(candidate, expected),
        Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
        now="2026-08-12T12:00:00+00:00",
    )
    _set_collection_running(project)
    _write_collection_progress(project)

    state = build_mobile_state(project)

    assert state["automation"]["current_stage"] == "media_collection"
    assert state["automation"]["label"] == "실제 자료 수집 실행 중"
    assert state["automation"]["media_collection"]["state"] == "downloading"
    assert state["automation"]["media_collection"]["counts"]["accepted"] == 7
    assert "api" not in json.dumps(state["automation"]["media_collection"]).lower()


def test_malformed_collection_progress_is_not_exposed(tmp_path: Path) -> None:
    project, candidate, expected = build_topic_gate(tmp_path)
    execute_action(
        tmp_path,
        payload(candidate, expected),
        Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
    )
    _set_collection_running(project)
    path = project / "automation/progress/media_collection.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")

    assert build_mobile_state(project)["automation"]["media_collection"] is None
