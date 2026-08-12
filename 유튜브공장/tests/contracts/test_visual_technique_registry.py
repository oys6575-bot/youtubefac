from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "config" / "visual-technique-registry.yaml"
SCHEMA_PATH = ROOT / "schemas" / "visual-technique-registry.schema.json"
SOURCE_MANIFEST_PATH = ROOT / "vendor" / "creative-sources" / "manifest.json"


def _module():
    return importlib.import_module("lib.visual_technique_registry")


def test_registry_schema_compiles_and_registry_passes_semantic_audit() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)

    registry = _module().load_registry(REGISTRY_PATH)
    assert registry["schema_version"] == "1.0.0"
    assert _module().audit_registry(registry, root=ROOT) == []


def test_every_active_local_source_is_real_and_factory_local() -> None:
    registry = _module().load_registry(REGISTRY_PATH)

    active_local = [
        item
        for item in registry["techniques"]
        if item["status"] == "ACTIVE" and item["source"]["type"] == "local_skill"
    ]
    assert active_local

    root_resolved = ROOT.resolve()
    for item in active_local:
        path = (ROOT / item["source"]["path"]).resolve()
        assert path.is_relative_to(root_resolved), item["id"]
        assert path.is_file(), item["id"]


def test_documentary_scene_selects_three_to_seven_relevant_methods_deterministically() -> None:
    kwargs = {
        "intents": [
            "material_macro",
            "process_geography",
            "photo_to_motion",
            "variable_camera_speed",
            "semantic_transition",
        ],
        "phase": "visual_plan",
        "provider_scope": "TOPVIEW_MANUAL",
        "render_runtime": "HYPERFRAMES",
    }

    first = _module().select_techniques(**kwargs)
    second = _module().select_techniques(**kwargs)
    selected_ids = [item["id"] for item in first["selected"]]

    assert first == second
    assert 3 <= len(selected_ids) <= 7
    assert {
        "camera.material_macro_parallax",
        "camera.variable_velocity_push",
        "continuity.process_geography",
        "transition.semantic_match_cut",
    }.issubset(set(selected_ids))
    assert all(item["matched_intents"] for item in first["selected"])


def test_topview_scope_never_leaks_other_provider_specific_guidance() -> None:
    result = _module().select_techniques(
        intents=[
            "camera_motion",
            "first_last_frame",
            "multi_reference",
            "provider_prompting",
        ],
        phase="production",
        provider_scope="TOPVIEW_MANUAL",
        render_runtime="ANY",
        include_on_demand=True,
    )

    selected = result["selected"]
    selected_ids = {item["id"] for item in selected}
    assert "provider.topview.first_last_frame_bridge" in selected_ids
    assert "provider.topview.multi_reference_continuity" in selected_ids
    assert not any(item_id.startswith("provider.higgsfield") for item_id in selected_ids)
    assert not any(item_id.startswith("provider.seedance") for item_id in selected_ids)
    assert all(
        set(item["provider_scopes"]) & {"GENERIC", "TOPVIEW_MANUAL"}
        for item in selected
    )


@pytest.mark.parametrize(
    ("intent", "technique_id"),
    [
        ("opening_frame", "direction.opening_frame_intent"),
        ("spatial_blocking", "continuity.explicit_spatial_blocking"),
        ("behavioral_performance", "direction.behavioral_performance_beats"),
        ("optical_result", "camera.observable_optical_result"),
        ("physical_causality", "direction.physical_causality"),
        ("reference_role", "continuity.reference_role_binding"),
    ],
)
def test_generic_cinematic_principles_are_route_safe(
    intent: str, technique_id: str
) -> None:
    result = _module().select_techniques(
        intents=[intent],
        phase="visual_plan",
        provider_scope="TOPVIEW_MANUAL",
        render_runtime="ANY",
    )

    selected = {item["id"]: item for item in result["selected"]}
    assert technique_id in selected
    assert selected[technique_id]["provider_scopes"] == ["GENERIC"]


def test_on_demand_library_is_discoverable_but_not_silently_selected() -> None:
    matches = _module().search_techniques("continuity bible")
    assert any(
        item["id"] == "library.nolanx.long_form_continuity"
        and item["status"] == "ON_DEMAND"
        for item in matches
    )

    default_result = _module().select_techniques(
        intents=["continuity_bible"],
        phase="visual_plan",
        provider_scope="GENERIC",
        render_runtime="ANY",
    )
    assert "library.nolanx.long_form_continuity" not in {
        item["id"] for item in default_result["selected"]
    }


def test_reference_only_and_blocked_sources_cannot_be_selected() -> None:
    result = _module().select_techniques(
        intents=["noncommercial_research", "training_dataset", "camera_motion"],
        phase="research",
        provider_scope="GENERIC",
        render_runtime="ANY",
        include_on_demand=True,
    )

    forbidden = {"REFERENCE_ONLY", "BLOCKED"}
    assert not forbidden & {item["status"] for item in result["selected"]}
    assert any(
        item["id"] == "research.hf.av_skills"
        and item["reason"] == "status:BLOCKED"
        for item in result["excluded"]
    )


def test_external_sources_are_revision_locked_without_large_payloads() -> None:
    manifest = json.loads(SOURCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    records = {item["id"]: item for item in manifest["sources"]}

    assert manifest["policy"]["large_payloads_in_git"] is False
    assert manifest["policy"]["auto_activation"] is False
    assert records["github.directorskills"]["revision"] == (
        "57d2ef52de61b926bdcac13fe27d07c17bc36516"
    )
    assert records["github.nolanx"]["license"] == "MIT"
    assert records["github.x_cut"]["license"] == "AGPL-3.0"
    assert records["hf.reolyy_edit_intent"]["revision"] == (
        "b54440bfc0232eac1a6a99e2b0c27a19a7e255b2"
    )
    assert records["hf.av_skills"]["activation_status"] == "BLOCKED"
    assert all(len(item["revision"]) == 40 for item in manifest["sources"])
