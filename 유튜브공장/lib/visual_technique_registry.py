"""Deterministic visual-technique catalog for the YouTube Factory.

The registry is knowledge routing, not provider routing. This module never downloads
source material, calls a model, spends credits, or changes approval state.
"""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
import yaml


FACTORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = FACTORY_ROOT / "config" / "visual-technique-registry.yaml"
DEFAULT_SCHEMA_PATH = FACTORY_ROOT / "schemas" / "visual-technique-registry.schema.json"

VALID_PROVIDER_SCOPES = {
    "GENERIC",
    "TOPVIEW_MANUAL",
    "HIGGSFIELD_MANUAL",
    "SEEDANCE_MANUAL",
    "LOCAL_LTX",
}
VALID_RENDER_RUNTIMES = {"ANY", "FFMPEG", "REMOTION", "HYPERFRAMES"}
VALID_PHASES = {
    "ALL",
    "research",
    "proposal",
    "script",
    "visual_plan",
    "animatic",
    "budget",
    "production",
    "edit",
    "compose",
    "qc",
}


class TechniqueRegistryError(ValueError):
    """Raised when a registry cannot be loaded or violates its contract."""


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _load_schema(path: Path = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TechniqueRegistryError(f"Cannot load technique schema: {path}: {exc}") from exc


def load_registry(path: Path | str = DEFAULT_REGISTRY_PATH) -> dict[str, Any]:
    """Load and structurally validate the canonical YAML registry."""

    registry_path = Path(path)
    try:
        payload = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise TechniqueRegistryError(
            f"Cannot load visual technique registry: {registry_path}: {exc}"
        ) from exc

    if not isinstance(payload, dict):
        raise TechniqueRegistryError("Visual technique registry root must be an object")

    schema = _load_schema()
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        summaries = []
        for error in errors[:12]:
            location = ".".join(str(part) for part in error.absolute_path) or "<root>"
            summaries.append(f"{location}: {error.message}")
        raise TechniqueRegistryError("Registry schema errors: " + "; ".join(summaries))
    return payload


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def audit_registry(
    registry: dict[str, Any] | None = None,
    *,
    root: Path = FACTORY_ROOT,
) -> list[str]:
    """Return semantic and isolation findings. An empty list means audit success."""

    registry = registry or load_registry()
    root = root.resolve()
    findings: list[str] = []

    policy = registry["policy"]
    if not (
        policy["minimum_recommended"]
        <= policy["default_limit"]
        <= policy["maximum_limit"]
    ):
        findings.append("policy limits must satisfy minimum <= default <= maximum")

    source_manifest_path = (root / registry["source_manifest"]).resolve()
    if not _inside(source_manifest_path, root):
        findings.append("source_manifest must remain inside the factory")
        manifest_ids: set[str] = set()
    elif not source_manifest_path.is_file():
        findings.append(f"source_manifest missing: {registry['source_manifest']}")
        manifest_ids = set()
    else:
        try:
            manifest = json.loads(source_manifest_path.read_text(encoding="utf-8"))
            manifest_ids = {item["id"] for item in manifest.get("sources", [])}
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            findings.append(f"source_manifest invalid: {exc}")
            manifest_ids = set()

    seen: set[str] = set()
    never_select = set(policy["never_select_statuses"])
    for item in registry["techniques"]:
        item_id = item["id"]
        if item_id in seen:
            findings.append(f"duplicate technique id: {item_id}")
        seen.add(item_id)

        status = item["status"]
        activation = item["activation"]
        if status == "ACTIVE" and not activation["default_allowed"]:
            findings.append(f"{item_id}: ACTIVE must be default_allowed")
        if status != "ACTIVE" and activation["default_allowed"]:
            findings.append(f"{item_id}: inactive status cannot be default_allowed")
        if status in never_select and item["selectable"]:
            findings.append(f"{item_id}: {status} cannot be selectable")
        if status == "ON_DEMAND" and not activation["requires_human_opt_in"]:
            findings.append(f"{item_id}: ON_DEMAND requires explicit opt-in")

        source = item["source"]
        source_path = source.get("path")
        if source_path:
            resolved = (root / source_path).resolve()
            if not _inside(resolved, root):
                findings.append(f"{item_id}: source path escapes factory: {source_path}")
            elif not resolved.is_file():
                findings.append(f"{item_id}: source path missing: {source_path}")

        manifest_id = source.get("manifest_id")
        if manifest_id and manifest_id not in manifest_ids:
            findings.append(f"{item_id}: unknown source manifest id: {manifest_id}")

        if item_id.startswith("provider.topview") and item["provider_scopes"] != [
            "TOPVIEW_MANUAL"
        ]:
            findings.append(f"{item_id}: TopView guidance must be TOPVIEW_MANUAL only")
        if item_id.startswith("provider.higgsfield") and item["provider_scopes"] != [
            "HIGGSFIELD_MANUAL"
        ]:
            findings.append(f"{item_id}: Higgsfield guidance must be isolated")
        if item_id.startswith("provider.seedance") and item["provider_scopes"] != [
            "SEEDANCE_MANUAL"
        ]:
            findings.append(f"{item_id}: Seedance guidance must be isolated")

    return findings


def _matched_intents(item: dict[str, Any], query_intents: set[str]) -> list[str]:
    item_terms = {_normalise(term) for term in item["intents"] + item["tags"]}
    return sorted(query_intents & item_terms)


def select_techniques(
    *,
    intents: Iterable[str],
    phase: str,
    provider_scope: str,
    render_runtime: str = "ANY",
    limit: int | None = None,
    include_on_demand: bool = False,
    registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Select a small route-safe set of techniques for one planning context.

    `include_on_demand` is an explicit selection-time opt-in. It does not override
    `selectable: false`, provider isolation, runtime/phase constraints, or the permanent
    exclusion of `REFERENCE_ONLY` and `BLOCKED` records.
    """

    registry = registry or load_registry()
    provider_scope = provider_scope.upper()
    render_runtime = render_runtime.upper()
    if provider_scope not in VALID_PROVIDER_SCOPES:
        raise TechniqueRegistryError(f"Unknown provider scope: {provider_scope}")
    if render_runtime not in VALID_RENDER_RUNTIMES:
        raise TechniqueRegistryError(f"Unknown render runtime: {render_runtime}")
    if phase not in VALID_PHASES - {"ALL"}:
        raise TechniqueRegistryError(f"Unknown production phase: {phase}")

    query_intents = {_normalise(intent) for intent in intents if _normalise(intent)}
    policy = registry["policy"]
    effective_limit = policy["default_limit"] if limit is None else int(limit)
    if not 1 <= effective_limit <= policy["maximum_limit"]:
        raise TechniqueRegistryError(
            f"limit must be between 1 and {policy['maximum_limit']}"
        )

    eligible_statuses = set(policy["normal_statuses"])
    if include_on_demand:
        eligible_statuses.update(policy["opt_in_statuses"])
    never_select = set(policy["never_select_statuses"])

    candidates: list[tuple[int, int, str, dict[str, Any]]] = []
    excluded: list[dict[str, str]] = []
    for item in registry["techniques"]:
        matched = _matched_intents(item, query_intents)
        if not matched:
            continue

        reason: str | None = None
        status = item["status"]
        if status in never_select:
            reason = f"status:{status}"
        elif status not in eligible_statuses:
            reason = f"status:{status}"
        elif not item["selectable"]:
            reason = "selectable:false"
        elif not (
            "GENERIC" in item["provider_scopes"]
            or provider_scope in item["provider_scopes"]
        ):
            reason = f"provider_scope:{provider_scope}"
        elif not (
            render_runtime == "ANY"
            or "ANY" in item["render_runtimes"]
            or render_runtime in item["render_runtimes"]
        ):
            reason = f"render_runtime:{render_runtime}"
        elif not ("ALL" in item["phases"] or phase in item["phases"]):
            reason = f"phase:{phase}"

        if reason:
            excluded.append({"id": item["id"], "reason": reason})
            continue

        selected_item = deepcopy(item)
        selected_item["matched_intents"] = matched
        candidates.append(
            (-len(matched), -int(item["priority"]), item["id"], selected_item)
        )

    candidates.sort(key=lambda row: (row[0], row[1], row[2]))
    selected = [row[3] for row in candidates[:effective_limit]]
    excluded.sort(key=lambda item: item["id"])

    return {
        "query": {
            "intents": sorted(query_intents),
            "phase": phase,
            "provider_scope": provider_scope,
            "render_runtime": render_runtime,
            "include_on_demand": include_on_demand,
            "limit": effective_limit,
        },
        "selected": selected,
        "excluded": excluded,
    }


def search_techniques(
    query: str,
    *,
    statuses: Iterable[str] | None = None,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Search active and dormant records without activating any of them."""

    registry = registry or load_registry()
    needle = _normalise(query)
    allowed = {status.upper() for status in statuses} if statuses else None
    matches: list[tuple[int, str, dict[str, Any]]] = []

    for item in registry["techniques"]:
        if allowed is not None and item["status"] not in allowed:
            continue
        fields = [
            item["id"],
            item["name"],
            item["description"],
            *item["intents"],
            *item["tags"],
        ]
        normalised_fields = [_normalise(field) for field in fields]
        score = sum(2 if field == needle else 1 for field in normalised_fields if needle in field)
        if needle and not score:
            continue
        result = deepcopy(item)
        result["search_score"] = score
        matches.append((-score, item["id"], result))

    matches.sort(key=lambda row: (row[0], row[1]))
    return [row[2] for row in matches]
