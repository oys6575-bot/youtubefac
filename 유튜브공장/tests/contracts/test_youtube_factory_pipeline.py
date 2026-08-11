from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from lib.checkpoint import CheckpointValidationError, write_checkpoint
from lib.pipeline_loader import get_stage_order, load_pipeline
from styles.playbook_loader import load_playbook
from tools.tool_registry import ToolRegistry


ROOT = Path(__file__).resolve().parents[2]


def test_pipeline_stage_order_places_manual_work_between_budget_and_asset_gate() -> None:
    manifest = load_pipeline("youtube-factory")

    assert get_stage_order(manifest) == [
        "research",
        "evidence_lock",
        "proposal",
        "script",
        "visual_plan",
        "animatic",
        "budget",
        "assets",
        "asset_selection",
        "edit",
        "compose",
        "final_review",
        "package",
        "title_thumbnail",
        "publish",
    ]
    assert manifest["metadata"]["topview_integration_mode"] == "manual_ui"
    assert manifest["extensions"]["custom_tools"] is True


def test_visual_plan_stage_is_wired_to_the_selective_technique_catalog() -> None:
    manifest = load_pipeline("youtube-factory")
    visual_stage = next(stage for stage in manifest["stages"] if stage["name"] == "visual_plan")

    assert manifest["metadata"]["visual_technique_registry"] == (
        "config/visual-technique-registry.yaml"
    )
    assert manifest["metadata"]["visual_technique_selection"] == {
        "minimum_recommended": 3,
        "maximum": 7,
        "provider_isolation_required": True,
        "on_demand_requires_explicit_selection": True,
    }
    assert "Selected technique IDs are recorded per sequence and per shot" in visual_stage[
        "review_focus"
    ]
    assert "Provider-specific technique exclusions are recorded" in visual_stage[
        "success_criteria"
    ]

    director = (
        ROOT / "skills/pipelines/youtube-factory/mk-visual-director.md"
    ).read_text(encoding="utf-8")
    for required_text in (
        "visual-technique-registry.yaml",
        "3–7",
        "provider-specific",
        "selected_ids",
        "technique_ids",
        "visual-techniques.py select",
    ):
        assert required_text in director


def test_visual_plan_stage_is_wired_to_the_audited_knowledge_vault() -> None:
    manifest = load_pipeline("youtube-factory")
    knowledge = manifest["metadata"]["knowledge_vault"]
    visual_stage = next(stage for stage in manifest["stages"] if stage["name"] == "visual_plan")

    assert knowledge["root"] == "knowledge"
    assert knowledge["audit_before_selection"] is True
    assert knowledge["pack_after_selection"] is True
    assert knowledge["per_entity_budget"] == 7
    assert knowledge["technique_budget"] == {"minimum": 3, "maximum": 7}
    assert manifest["metadata"]["topview_integration_mode"] == "manual_ui"
    assert "Knowledge-vault audit passes before technique selection" in visual_stage[
        "review_focus"
    ]
    assert any(
        "Bounded knowledge pack is recorded" in item
        for item in visual_stage["success_criteria"]
    )

    director = (
        ROOT / "skills/pipelines/youtube-factory/mk-visual-director.md"
    ).read_text(encoding="utf-8")
    for required_text in (
        "knowledge-vault.py audit",
        "knowledge-vault.py pack",
        "load_order",
        "3–7",
        "Human Gate",
        "TopView",
    ):
        assert required_text in director


def test_pipeline_keeps_all_required_human_gates() -> None:
    manifest = load_pipeline("youtube-factory")
    stages = {stage["name"]: stage for stage in manifest["stages"]}
    gated = {
        name for name, stage in stages.items() if stage["human_approval_default"] is True
    }

    assert gated == {
        "evidence_lock",
        "proposal",
        "script",
        "animatic",
        "budget",
        "asset_selection",
        "final_review",
        "title_thumbnail",
        "publish",
    }
    assert stages["assets"]["human_approval_default"] is False
    assert "topview_manual_handoff" in stages["assets"]["tools_available"]
    assert "topview_manual_ingest" in stages["assets"]["tools_available"]
    assert "asset_selection" in stages["edit"]["required_artifacts_in"]


def test_pipeline_director_files_and_local_manual_tools_are_available() -> None:
    manifest = load_pipeline("youtube-factory")
    missing = [
        skill
        for skill in manifest["required_skills"]
        if not (ROOT / "skills" / f"{skill}.md").is_file()
    ]
    assert missing == []

    registry = ToolRegistry()
    registry.discover()
    assert registry.get("topview_manual_handoff") is not None
    assert registry.get("topview_manual_ingest") is not None


def test_heritage_forge_playbook_and_visual_grammar_are_loadable() -> None:
    playbook = load_playbook("heritage-forge")
    grammar_path = ROOT / "config" / "visual-grammars" / "HERITAGE_FORGE.yaml"

    assert playbook["identity"]["name"] == "Heritage Forge"
    assert grammar_path.is_file()
    grammar = yaml.safe_load(grammar_path.read_text(encoding="utf-8"))
    assert grammar["identity"]["version"] == "1.0.1"
    assert grammar["routing"]["allowed_modes"] == [
        "REAL_INGEST",
        "TOPVIEW_HANDOFF",
        "LOCAL_LTX",
        "HYPERFRAMES",
    ]
    assert grammar["routing"]["topview"]["integration_mode"] == "manual_ui"


def test_asset_selection_checkpoint_cannot_complete_without_human_approval(
    tmp_path: Path,
) -> None:
    with pytest.raises(CheckpointValidationError, match="GATE VIOLATION"):
        write_checkpoint(
            tmp_path,
            "PROJECT_DEMO",
            "asset_selection",
            "completed",
            {},
            pipeline_type="youtube-factory",
            human_approved=False,
        )


def test_assets_stage_can_checkpoint_manual_external_wait_without_fake_approval(
    tmp_path: Path,
) -> None:
    checkpoint_path = write_checkpoint(
        tmp_path,
        "PROJECT_DEMO",
        "assets",
        "in_progress",
        {},
        pipeline_type="youtube-factory",
        metadata={
            "manual_external_state": "awaiting_manual_external",
            "next_action": "TopView UI 작업 후 inbox에 결과 배치",
        },
    )

    assert checkpoint_path.is_file()
