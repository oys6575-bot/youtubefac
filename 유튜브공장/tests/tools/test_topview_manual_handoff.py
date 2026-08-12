from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from tools.base_tool import ToolStatus
from tools.tool_registry import ToolRegistry


ROOT = Path(__file__).resolve().parents[2]
VALID_PLAN = ROOT / "tests/fixtures/youtube_factory/visual_plan.valid.json"


def _tool_class():
    return importlib.import_module("tools.video.topview_manual_handoff").TopViewManualHandoff


def _project(tmp_path: Path, reference_path: str = "references/archive-frame.png") -> tuple[Path, Path]:
    project = tmp_path / "demo-project"
    artifact_dir = project / "artifacts"
    reference_dir = project / "references"
    artifact_dir.mkdir(parents=True)
    reference_dir.mkdir(parents=True)
    (reference_dir / "archive-frame.png").write_bytes(b"frozen-reference-image")

    plan = json.loads(VALID_PLAN.read_text(encoding="utf-8"))
    plan["sequences"][0]["shots"][1]["generation_brief"]["reference_paths"] = [
        reference_path
    ]
    plan["sequences"][0]["shots"][1]["cinematic_direction"][
        "reference_bindings"
    ][0]["path"] = reference_path
    plan_path = artifact_dir / "visual_plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    return project, plan_path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_job_pack_contains_only_manual_topview_shots_and_frozen_references(tmp_path: Path) -> None:
    project, plan_path = _project(tmp_path)

    result = _tool_class()().execute(
        {
            "project_dir": str(project),
            "visual_plan_path": str(plan_path),
            "batch_id": "BATCH_001",
        }
    )

    assert result.success is True, result.error
    job_path = Path(result.data["job_pack_path"])
    job = json.loads(job_path.read_text(encoding="utf-8"))
    assert job["integration_mode"] == "manual_ui"
    assert job["state"] == "awaiting_manual_external"
    assert job["schema_version"] == "1.1.0"
    assert job["capability_catalog_version"] == "2026-08-11"
    assert job["operator_policy"] == {
        "platform": "TopView web UI",
        "ui_only": True,
        "api_allowed": False,
        "mcp_allowed": False,
        "browser_automation_allowed": False,
        "budget_gate_required": True,
        "asset_selection_gate_required": True,
    }
    assert [item["shot_id"] for item in job["jobs"]] == ["SHOT_002"]
    topview_job = job["jobs"][0]
    assert topview_job["expected_filename"] == "SHOT_002__candidate_A.mp4"
    assert topview_job["ui_workspace"] == "BOARD"
    assert topview_job["task_mode"] == "IMAGE_TO_VIDEO"
    assert topview_job["model_selection"]["exact_ui_label_required"] is True
    assert topview_job["model_selection"]["allow_silent_substitution"] is False
    assert topview_job["budget"]["capture_cost_before_submit"] is True
    assert topview_job["budget"]["stop_before_overage"] is True
    assert topview_job["continuity"]["preserve_environment"] is True
    assert topview_job["evidence_policy"]["generated_text_allowed"] is False
    frozen = project / topview_job["reference_files"][0]["frozen_path"]
    assert frozen.read_bytes() == b"frozen-reference-image"
    assert topview_job["reference_files"][0]["sha256"] == _sha256(frozen)
    assert topview_job["reference_files"][0]["role"] == "ENVIRONMENT_REFERENCE"
    assert topview_job["reference_files"][0]["controls"] == [
        "workspace geometry",
        "material character",
        "light direction",
    ]
    assert "camera framing" in topview_job["reference_files"][0]["excludes"]
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan_shot = plan["sequences"][0]["shots"][1]
    assert topview_job["cinematic_direction"] == plan_shot["cinematic_direction"]
    instructions = Path(result.data["instructions_path"]).read_text(encoding="utf-8")
    assert "첫 프레임" in instructions
    assert "시간 비트" in instructions
    assert "레퍼런스 역할" in instructions
    assert job["automated_api_cost_usd"] == 0

    schema = json.loads(
        (ROOT / "schemas/artifacts/topview_job_pack.schema.json").read_text(encoding="utf-8")
    )
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(job)


def test_same_plan_and_batch_produce_identical_job_pack(tmp_path: Path) -> None:
    project, plan_path = _project(tmp_path)
    inputs = {
        "project_dir": str(project),
        "visual_plan_path": str(plan_path),
        "batch_id": "BATCH_001",
    }

    first = _tool_class()().execute(inputs)
    first_hash = _sha256(Path(first.data["job_pack_path"]))
    second = _tool_class()().execute(inputs)
    second_hash = _sha256(Path(second.data["job_pack_path"]))

    assert first.success is True
    assert second.success is True
    assert first_hash == second_hash


def test_reference_outside_project_is_rejected_before_outbox_creation(tmp_path: Path) -> None:
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"not-project-owned")
    project, plan_path = _project(tmp_path, "../outside.png")

    result = _tool_class()().execute(
        {
            "project_dir": str(project),
            "visual_plan_path": str(plan_path),
            "batch_id": "BATCH_001",
        }
    )

    assert result.success is False
    assert "outside project" in (result.error or "")
    assert not (project / "handoff/topview/outbox/BATCH_001").exists()


def test_missing_reference_role_binding_is_rejected_before_outbox_creation(
    tmp_path: Path,
) -> None:
    project, plan_path = _project(tmp_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["sequences"][0]["shots"][1]["cinematic_direction"][
        "reference_bindings"
    ] = []
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    result = _tool_class()().execute(
        {
            "project_dir": str(project),
            "visual_plan_path": str(plan_path),
            "batch_id": "BATCH_001",
        }
    )

    assert result.success is False
    assert "reference bindings" in (result.error or "")
    assert not (project / "handoff/topview/outbox/BATCH_001").exists()


def test_tool_is_local_zero_cost_and_registry_discoverable() -> None:
    tool = _tool_class()()
    assert tool.get_status() == ToolStatus.AVAILABLE
    assert tool.estimate_cost({}) == 0
    assert tool.get_info()["resource_profile"]["network_required"] is False
    assert tool.agent_skills == ["topview-manual-handoff"]

    registry = ToolRegistry()
    registry.discover()
    assert registry.get("topview_manual_handoff") is not None
