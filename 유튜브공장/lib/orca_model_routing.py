"""Strict role, model, gate, resource, and secret routing for Orca."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError


FACTORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROUTING_PATH = FACTORY_ROOT / "config" / "orca-model-routing.yaml"
DEFAULT_SCHEMA_PATH = (
    FACTORY_ROOT
    / "schemas"
    / "orchestration"
    / "orca-model-routing.schema.json"
)

EXPECTED_ROLES = {
    "control": {
        "runtime": "codex",
        "model": "gpt-5.6-sol",
        "effort": "max",
        "profile": None,
        "resource_lane": "cloud",
        "writes": ["coordination_records", "integration_commits"],
    },
    "research": {
        "runtime": "hermes",
        "model": "qwen3.6-35b-a3b-mlx",
        "effort": None,
        "profile": "ytf-research",
        "resource_lane": "local_text",
        "writes": ["research/topic-candidates"],
    },
    "verification": {
        "runtime": "codex",
        "model": "gpt-5.6-sol",
        "effort": "high",
        "profile": None,
        "resource_lane": "cloud",
        "writes": ["reviews"],
    },
    "story_visual": {
        "runtime": "claude",
        "model": "claude-opus-5",
        "effort": "max",
        "profile": None,
        "resource_lane": "cloud",
        "writes": ["scripts", "visual-plans", "animatics"],
    },
    "production": {
        "runtime": "hermes",
        "model": "qwen3.6-35b-a3b-mlx",
        "effort": None,
        "profile": "ytf-production",
        "resource_lane": "local_text",
        "writes": ["production-packets", "asset-ledgers"],
    },
    "qa": {
        "runtime": "codex",
        "model": "gpt-5.6-sol",
        "effort": "high",
        "profile": None,
        "resource_lane": "cloud",
        "writes": ["reviews"],
    },
}

EXPECTED_GATES = {
    gate: {"authority": "user", "automatic_approval": False}
    for gate in (
        "topic_approval",
        "animatic_approval",
        "budget_approval",
        "asset_selection",
        "final_edit_approval",
        "publish_approval",
    )
}

EXPECTED_SECRET_ALLOWLISTS = {
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

EXPECTED_WORKSPACE = {
    "repo_root_kind": "parent_git_repository",
    "factory_cwd_suffix": "유튜브공장",
    "canonical_projects_env": "OPENMONTAGE_PROJECTS_DIR",
    "canonical_projects_root": "유튜브공장/projects",
}

EXPECTED_HANDOFF = {
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


class RoutingContractError(ValueError):
    """Raised when routing can violate the approved deployment design."""


def _load_schema(path: Path = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, SchemaError) as exc:
        raise RoutingContractError(f"Cannot load routing schema: {path}: {exc}") from exc
    return schema


def _schema_validate(data: Mapping[str, Any]) -> None:
    validator = Draft202012Validator(_load_schema())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.path) or "root"
        section = location.split(".", 1)[0]
        label = {
            "topview": "TopView",
            "human_gates": "Human Gate",
            "resource_lanes": "resource lane",
            "secrets": "secret",
            "workspace": "workspace",
            "handoff": "handoff",
        }.get(section, section)
        raise RoutingContractError(
            f"{label} schema violation at {location}: {error.message}"
        )


def validate_routing(data: Mapping[str, Any]) -> dict[str, Any]:
    """Validate schema plus the safety invariants that JSON Schema cannot express."""

    if not isinstance(data, Mapping):
        raise RoutingContractError("routing root must be an object")
    payload = dict(data)
    _schema_validate(payload)

    if payload["roles"] != EXPECTED_ROLES:
        raise RoutingContractError("role model, runtime, effort, or write ownership drift")

    if payload["workspace"] != EXPECTED_WORKSPACE:
        raise RoutingContractError("workspace root or canonical projects path drift")

    if payload["handoff"] != EXPECTED_HANDOFF:
        raise RoutingContractError("handoff is not bound to exact commit and artifact bytes")

    expected_topview = {
        "mode": "manual_semi_automatic",
        "api_enabled": False,
        "automatic_dispatch": False,
        "result_ingest_requires_manifest": True,
    }
    if payload["topview"] != expected_topview:
        raise RoutingContractError("TopView must remain manual and manifest-gated")

    expected_provider_policy = {
        "silent_fallback": False,
        "silent_model_switch": False,
        "paid_calls_require_gate": "budget_approval",
    }
    if payload["provider_policy"] != expected_provider_policy:
        raise RoutingContractError("provider fallback and model switching must be explicit")

    if payload["human_gates"] != EXPECTED_GATES:
        raise RoutingContractError("Human Gate authority or automatic approval drift")

    lanes = payload["resource_lanes"]
    if ["local_text", "local_media"] not in lanes["mutex"]:
        raise RoutingContractError("resource lane mutex must protect local memory")

    secrets = payload["secrets"]
    if not secrets["default_deny"] or secrets["role_allowlists"] != EXPECTED_SECRET_ALLOWLISTS:
        raise RoutingContractError("secret allowlists violate least privilege")

    if payload["local_models"]["silent_switch"]:
        raise RoutingContractError("local model switch cannot be silent")
    return payload


def load_routing(path: Path | str = DEFAULT_ROUTING_PATH) -> dict[str, Any]:
    """Load and strictly validate the canonical Orca routing contract."""

    routing_path = Path(path)
    try:
        payload = yaml.safe_load(routing_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RoutingContractError(f"Cannot load routing: {routing_path}: {exc}") from exc
    return validate_routing(payload)
