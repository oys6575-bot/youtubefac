from __future__ import annotations

import json
from pathlib import Path

from backlot.mobile_state import build_mobile_state
from backlot.mobile_actions import Actor, execute_action
from lib.checkpoint import init_project, write_checkpoint
from tests.backlot.mobile_fixtures import build_topic_gate
from tests.backlot.test_mobile_actions import payload


def test_mobile_projection_has_full_stage_gate_candidates_and_roles(tmp_path: Path) -> None:
    project, _candidate, expected_hash = build_topic_gate(tmp_path)

    state = build_mobile_state(project)

    assert state["project"]["project_id"] == "MOBILE_TEST"
    assert state["source_of_truth"] == "openmontage"
    assert len(state["stages"]) == 20
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


def test_dashboard_asset_library_defaults_to_reviewed_recommended_items(tmp_path: Path) -> None:
    from tests.lib.test_reviewed_media_inventory import build_project

    project = build_project(tmp_path)
    (project / "project.json").write_text(json.dumps({
        "project_id": "pilot", "title": "Pilot", "pipeline_type": "youtube-factory"
    }), encoding="utf-8")
    library = build_mobile_state(project)["asset_library"]
    assert library["default_filter"] == "recommended"
    assert library["counts"] == {"recommended": 4, "excluded": 3, "held": 1}
    assert sum(item["recommended"] for item in library["items"]) == 4


def test_manual_collection_is_visible_without_rewriting_terminal_job(
    tmp_path: Path,
) -> None:
    project, candidate, expected = build_topic_gate(tmp_path)
    execute_action(
        tmp_path,
        payload(candidate, expected),
        Actor(tailscale_login="owner@example.com", tailscale_user_id="123"),
    )
    job_path = next((project / "automation/jobs").glob("*.json"))
    job = json.loads(job_path.read_text(encoding="utf-8"))
    job["state"] = "awaiting_human"
    job["current_stage"] = "proposal"
    job_path.write_text(json.dumps(job), encoding="utf-8")
    _write_collection_progress(project)

    automation = build_mobile_state(project)["automation"]

    assert automation["current_stage"] == "proposal"
    assert automation["active_stage"] == "media_collection"
    assert automation["label"] == "실제 자료 수집 실행 중"


def test_newer_media_collection_suppresses_stale_proposal_gate(tmp_path: Path) -> None:
    project = init_project(
        "STALE_GATE",
        title="오래된 승인 제거",
        pipeline_type="youtube-factory",
        pipeline_dir=tmp_path,
    )
    (project / "checkpoint_proposal.json").write_text(
        json.dumps(
            {
                "stage": "proposal",
                "status": "awaiting_human",
                "timestamp": "2026-08-12T14:09:20+00:00",
                "human_approved": False,
                "artifacts": {},
            }
        ),
        encoding="utf-8",
    )
    (project / "checkpoint_media_collection.json").write_text(
        json.dumps(
            {
                "stage": "media_collection",
                "status": "completed",
                "timestamp": "2026-08-12T14:49:37+00:00",
                "human_approved": False,
                "artifacts": {},
            }
        ),
        encoding="utf-8",
    )

    state = build_mobile_state(project)

    assert state["current_gate"] is None
    assert state["current_work"]["stage"] == "proposal_refresh"
    assert state["current_work"]["status"] == "in_progress"
    assert "새 기획안" in state["current_work"]["detail"]


def test_mobile_projection_exposes_media_previews_without_private_metadata(
    tmp_path: Path,
) -> None:
    project = init_project(
        "MEDIA_LIBRARY",
        title="에셋 자료함",
        pipeline_type="youtube-factory",
        pipeline_dir=tmp_path,
    )
    artifacts = project / "artifacts"
    artifacts.mkdir(exist_ok=True)
    manifest = {
        "schema_version": "1.0.0",
        "project_id": project.name,
        "collection_status": "completed",
        "queries": [
            {
                "query_id": "Q001",
                "text": "building collapse rescue workers rubble",
                "kind": "image",
                "claim_ids": ["CLAIM_RESCUE"],
            }
        ],
        "source_summary": {
            "attempted": ["pexels"],
            "completed": ["pexels"],
            "failed": [],
            "discovered": 2,
            "accepted": 2,
            "downloaded": 2,
            "duplicates": 0,
            "rejected_counts": {},
        },
        "items": [
            {
                "id": "MEDIA_IMAGE_1",
                "media_type": "image",
                "local_path": "assets/source/images/rescue.jpeg",
                "source_url": "https://private.example/image",
                "direct_url": "https://signed.example/secret",
                "license": "internal-only",
                "claim_ids": ["CLAIM_RESCUE"],
                "technical": {
                    "width": 1920,
                    "height": 1080,
                    "duration_seconds": 0,
                    "size_bytes": 2048,
                },
            },
            {
                "id": "MEDIA_VIDEO_1",
                "media_type": "video",
                "local_path": "assets/source/video/rescue.mp4",
                "source_url": "https://private.example/video",
                "direct_url": None,
                "license": "internal-only",
                "claim_ids": ["CLAIM_RESCUE"],
                "technical": {
                    "width": 1280,
                    "height": 720,
                    "duration_seconds": 12,
                    "size_bytes": 4096,
                },
            },
        ],
    }
    (artifacts / "media_collection_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    library = build_mobile_state(project)["asset_library"]

    assert library["summary"] == {
        "total": 2,
        "images": 1,
        "videos": 1,
        "audio": 0,
    }
    assert library["items"][0] == {
        "id": "MEDIA_IMAGE_1",
        "media_type": "image",
        "label": "building collapse rescue workers rubble",
        "media_url": "/api/mobile/project/MEDIA_LIBRARY/media/MEDIA_IMAGE_1",
        "preview_url": "/api/mobile/project/MEDIA_LIBRARY/preview/MEDIA_IMAGE_1",
        "width": 1920,
        "height": 1080,
        "duration_seconds": 0.0,
        "category": "unknown",
        "eligibility": "held",
        "recommended": False,
        "review_reason": "automatic relevance review is missing or no longer matches these bytes",
    }
    serialized = json.dumps(library)
    assert "local_path" not in serialized
    assert "private.example" not in serialized
    assert "signed.example" not in serialized
    assert "license" not in serialized


def test_mobile_projection_separates_script_and_visual_prompts(tmp_path: Path) -> None:
    project = init_project(
        "SCRIPT_VIEW",
        title="대본 화면",
        pipeline_type="youtube-factory",
        pipeline_dir=tmp_path,
    )
    artifacts = project / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "script.json").write_text(
        json.dumps(
            {
                "version": "1.0",
                "title": "균열이 나타난 날",
                "total_duration_seconds": 20,
                "sections": [
                    {
                        "id": "S01",
                        "label": "도입",
                        "text": "건물에는 이미 균열이 나타났습니다.",
                        "start_seconds": 0,
                        "end_seconds": 8,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (artifacts / "visual_plan.json").write_text(
        json.dumps(
            {
                "sequences": [
                    {
                        "sequence_id": "SEQ01",
                        "purpose": "경고 제시",
                        "pacing_profile": "accelerating",
                        "shots": [
                            {
                                "shot_id": "SHOT01",
                                "representation": "REAL",
                                "prompt_intent": "균열을 따라 천천히 이동한 뒤 급정지",
                                "provider_route": "REAL_INGEST",
                                "duration_seconds": 5,
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    script_view = build_mobile_state(project)["script_view"]

    assert script_view["title"] == "균열이 나타난 날"
    assert script_view["sections"][0]["text"] == "건물에는 이미 균열이 나타났습니다."
    assert script_view["visual_prompts"][0] == {
        "sequence_id": "SEQ01",
        "sequence_purpose": "경고 제시",
        "pacing_profile": "accelerating",
        "shot_id": "SHOT01",
        "representation": "REAL",
        "prompt": "균열을 따라 천천히 이동한 뒤 급정지",
        "provider_route": "REAL_INGEST",
        "duration_seconds": 5.0,
    }
