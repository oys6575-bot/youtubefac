from __future__ import annotations

from copy import deepcopy
import importlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from schemas.artifacts import ARTIFACT_NAMES


FACTORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = FACTORY_ROOT / "tests" / "fixtures" / "youtube_factory"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _validator_module():
    return importlib.import_module("lib.visual_plan_validator")


def _bridge_module():
    return importlib.import_module("lib.visual_plan_bridge")


def test_factory_schemas_compile_and_accept_valid_fixture() -> None:
    evidence_schema = json.loads(
        (FACTORY_ROOT / "schemas/artifacts/evidence_registry.schema.json").read_text(
            encoding="utf-8"
        )
    )
    visual_schema = json.loads(
        (FACTORY_ROOT / "schemas/artifacts/visual_plan.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator.check_schema(evidence_schema)
    Draft202012Validator.check_schema(visual_schema)

    Draft202012Validator(
        evidence_schema, format_checker=FormatChecker()
    ).validate(_load("evidence_registry.valid.json"))
    Draft202012Validator(
        visual_schema, format_checker=FormatChecker()
    ).validate(_load("visual_plan.valid.json"))

    sequence = _load("visual_plan.valid.json")["sequences"][0]
    assert 3 <= len(sequence["technique_selection"]["selected_ids"]) <= 7
    assert all(shot["technique_ids"] for shot in sequence["shots"])


def test_route_contract_is_manual_topview_and_has_no_api_route() -> None:
    schema = json.loads(
        (FACTORY_ROOT / "schemas/artifacts/visual_plan.schema.json").read_text(
            encoding="utf-8"
        )
    )
    route_enum = schema["$defs"]["shot"]["properties"]["provider_route"]["properties"][
        "mode"
    ]["enum"]

    assert route_enum == [
        "REAL_INGEST",
        "TOPVIEW_HANDOFF",
        "LOCAL_LTX",
        "HYPERFRAMES",
    ]


def test_exact_overlay_rejects_literal_that_differs_from_verified_claim() -> None:
    plan = _load("visual_plan.valid.json")
    plan["sequences"][0]["shots"][0]["overlay"]["items"][0]["literal"] = "1991년 7월 18일"

    errors = _validator_module().validate_visual_plan(
        plan, _load("evidence_registry.valid.json")
    )

    assert "SHOT_001/OVL_DATE: literal must equal claim text" in errors


def test_ai_route_rejects_contains_ai_and_disclosure_contradictions() -> None:
    plan = _load("visual_plan.valid.json")
    shot = plan["sequences"][0]["shots"][1]
    shot["contains_ai"] = False
    shot["disclosure"] = {"required": False, "label": None}

    errors = _validator_module().validate_visual_plan(
        plan, _load("evidence_registry.valid.json")
    )

    assert "SHOT_002: AI route requires contains_ai=true" in errors
    assert "SHOT_002: AI content requires disclosure" in errors


def test_shot_techniques_must_be_selected_at_sequence_level() -> None:
    plan = _load("visual_plan.valid.json")
    plan["sequences"][0]["shots"][0]["technique_ids"].append(
        "camera.static_evidence_hold"
    )

    errors = _validator_module().validate_visual_plan(
        plan, _load("evidence_registry.valid.json")
    )

    assert (
        "SHOT_001: technique_id camera.static_evidence_hold is not selected for SEQ_INTRO"
        in errors
    )


def test_blocked_or_unknown_techniques_cannot_enter_visual_plan() -> None:
    plan = _load("visual_plan.valid.json")
    selection = plan["sequences"][0]["technique_selection"]
    selection["selected_ids"][0] = "research.hf.av_skills"
    plan["sequences"][0]["shots"][0]["technique_ids"][0] = "research.hf.av_skills"

    errors = _validator_module().validate_visual_plan(
        plan, _load("evidence_registry.valid.json")
    )

    assert "SEQ_INTRO: technique research.hf.av_skills has forbidden status BLOCKED" in errors


def test_bridge_preserves_order_timing_and_route_metadata() -> None:
    plan = _load("visual_plan.valid.json")

    scene_plan = _bridge_module().compile_scene_plan(plan)

    assert [scene["id"] for scene in scene_plan["scenes"]] == ["SHOT_001", "SHOT_002"]
    assert [(scene["start_seconds"], scene["end_seconds"]) for scene in scene_plan["scenes"]] == [
        (0.0, 3.0),
        (3.0, 7.0),
    ]
    assert scene_plan["metadata"]["production_routes"] == {
        "SHOT_001": "HYPERFRAMES",
        "SHOT_002": "TOPVIEW_HANDOFF",
    }

    scene_schema = json.loads(
        (FACTORY_ROOT / "schemas/artifacts/scene_plan.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(scene_schema).validate(scene_plan)


def test_gate_support_artifacts_compile_without_duplicating_approval_state() -> None:
    cases = {
        "animatic_review.schema.json": {
            "schema_version": "1.0.0",
            "project_id": "PROJECT_DEMO",
            "plan_id": "PLAN_DEMO",
            "state": "ready_for_gate",
            "animatic": {
                "path": "renders/animatic.mp4",
                "sha256": "1" * 64,
                "duration_seconds": 7,
            },
            "findings": [],
            "gate_ref": {
                "gate": "GATE_ANIMATIC",
                "checkpoint_path": "checkpoints/animatic.json",
            },
        },
        "budget_approval.schema.json": {
            "schema_version": "1.0.0",
            "project_id": "PROJECT_DEMO",
            "plan_id": "PLAN_DEMO",
            "state": "ready_for_gate",
            "currency": "USD",
            "estimated_cost": 0,
            "route_estimates": [
                {
                    "route": "TOPVIEW_HANDOFF",
                    "shot_count": 1,
                    "estimated_credits": 40,
                    "estimated_cost": 0,
                    "note": "실제 결제는 TopView UI에서 사용자가 판단한다.",
                }
            ],
            "gate_ref": {
                "gate": "GATE_BUDGET",
                "checkpoint_path": "checkpoints/budget.json",
            },
        },
        "asset_selection.schema.json": {
            "schema_version": "1.0.0",
            "project_id": "PROJECT_DEMO",
            "state": "ready_for_gate",
            "candidates": [
                {
                    "asset_id": "ASSET_SHOT_002_A",
                    "shot_id": "SHOT_002",
                    "path": "assets/candidates/shot_002_a.mp4",
                    "sha256": "2" * 64,
                }
            ],
            "selected_asset_ids": ["ASSET_SHOT_002_A"],
            "gate_ref": {
                "gate": "GATE_ASSET_SELECTION",
                "checkpoint_path": "checkpoints/asset_selection.json",
            },
        },
    }

    for schema_name, fixture in cases.items():
        schema = json.loads(
            (FACTORY_ROOT / "schemas/artifacts" / schema_name).read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(fixture)
        assert "approved" not in fixture


def test_factory_artifacts_are_registered_for_checkpoint_validation() -> None:
    assert {
        "evidence_registry",
        "visual_plan",
        "animatic_review",
        "budget_approval",
        "asset_selection",
        "topview_job_pack",
        "topview_operator_result",
    }.issubset(set(ARTIFACT_NAMES))
