from __future__ import annotations

from copy import deepcopy

import pytest

from lib.orca_model_routing import RoutingContractError, load_routing, validate_routing


EXPECTED_ROLES = {
    "control",
    "research",
    "verification",
    "story_visual",
    "production",
    "qa",
}


def test_role_models_and_runtimes_are_exact() -> None:
    routing = load_routing()
    assert set(routing["roles"]) == EXPECTED_ROLES
    assert routing["roles"]["control"] == {
        "runtime": "codex",
        "model": "gpt-5.6-sol",
        "effort": "xhigh",
        "profile": None,
        "resource_lane": "cloud",
        "writes": ["coordination_records", "integration_commits"],
    }
    assert routing["roles"]["research"] == {
        "runtime": "hermes",
        "model": "qwen3.6-35b-a3b-mlx",
        "effort": None,
        "profile": "ytf-research",
        "resource_lane": "local_text",
        "writes": ["research/topic-candidates"],
    }
    assert routing["roles"]["verification"]["model"] == "gpt-5.6-sol"
    assert routing["roles"]["verification"]["effort"] == "high"
    assert routing["roles"]["story_visual"]["runtime"] == "claude"
    assert routing["roles"]["story_visual"]["model"] == "claude-opus-5"
    assert routing["roles"]["story_visual"]["effort"] == "max"
    assert routing["roles"]["production"]["profile"] == "ytf-production"
    assert routing["roles"]["qa"]["effort"] == "high"


def test_topview_and_provider_fallback_are_locked() -> None:
    routing = load_routing()
    assert routing["topview"] == {
        "mode": "manual_semi_automatic",
        "api_enabled": False,
        "automatic_dispatch": False,
        "result_ingest_requires_manifest": True,
    }
    assert routing["provider_policy"] == {
        "silent_fallback": False,
        "silent_model_switch": False,
        "paid_calls_require_gate": "budget_approval",
    }


def test_human_gates_cannot_be_auto_approved() -> None:
    routing = load_routing()
    assert set(routing["human_gates"]) == {
        "topic_approval",
        "animatic_approval",
        "budget_approval",
        "asset_selection",
        "final_edit_approval",
        "publish_approval",
    }
    for gate in routing["human_gates"].values():
        assert gate == {"authority": "user", "automatic_approval": False}


def test_local_text_and_media_lanes_are_mutually_exclusive() -> None:
    routing = load_routing()
    lanes = routing["resource_lanes"]
    assert lanes["local_text"]["max_concurrent"] == 1
    assert lanes["local_media"]["max_concurrent"] == 1
    assert ["local_text", "local_media"] in lanes["mutex"]
    assert lanes["cloud"]["parallel_allowed"] is True


def test_secret_allowlists_are_least_privilege() -> None:
    routing = load_routing()
    secrets = routing["secrets"]
    assert secrets["default_deny"] is True
    assert secrets["role_allowlists"] == {
        "control": [],
        "research": ["YOUTUBE_API_KEY"],
        "verification": [],
        "story_visual": [],
        "production": [
            "PEXELS_API_KEY",
            "PIXABAY_API_KEY",
            "UNSPLASH_ACCESS_KEY",
        ],
        "qa": [],
    }


def test_workspace_and_handoff_bind_every_role_to_exact_bytes() -> None:
    routing = load_routing()
    assert routing["workspace"] == {
        "repo_root_kind": "parent_git_repository",
        "factory_cwd_suffix": "유튜브공장",
        "canonical_projects_env": "OPENMONTAGE_PROJECTS_DIR",
        "canonical_projects_root": "유튜브공장/projects",
    }
    assert routing["handoff"] == {
        "required_fields": ["source_commit", "artifact_path", "artifact_sha256"],
        "verification_required_fields": [
            "verdict",
            "source_commit",
            "input_sha256",
            "verified_at",
            "source_urls",
        ],
        "merge_requires_exact_match": True,
    }


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (
            lambda data: data["topview"].__setitem__("api_enabled", True),
            "TopView",
        ),
        (
            lambda data: data["provider_policy"].__setitem__("silent_fallback", True),
            "fallback",
        ),
        (
            lambda data: data["human_gates"]["topic_approval"].__setitem__(
                "automatic_approval", True
            ),
            "Human Gate",
        ),
        (
            lambda data: data["secrets"]["role_allowlists"]["qa"].append(
                "YOUTUBE_API_KEY"
            ),
            "secret",
        ),
        (
            lambda data: data["resource_lanes"].__setitem__("mutex", []),
            "resource lane",
        ),
        (
            lambda data: data["workspace"].__setitem__(
                "factory_cwd_suffix", "."
            ),
            "workspace",
        ),
        (
            lambda data: data["handoff"].__setitem__(
                "merge_requires_exact_match", False
            ),
            "handoff",
        ),
    ],
)
def test_semantic_contract_rejects_unsafe_mutations(mutator, message: str) -> None:
    routing = deepcopy(load_routing())
    mutator(routing)
    with pytest.raises(RoutingContractError, match=message):
        validate_routing(routing)
