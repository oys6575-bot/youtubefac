"""Semantic validation for YouTube Factory VisualPlan artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
VISUAL_PLAN_SCHEMA = ROOT / "schemas" / "artifacts" / "visual_plan.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas" / "artifacts" / "evidence_registry.schema.json"
AI_ROUTES = {"TOPVIEW_HANDOFF", "LOCAL_LTX"}
AI_DISCLOSURE_LABELS = {"AI 재현", "AI 재현 + 설명 그래픽"}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_errors(instance: dict[str, Any], schema_path: Path, prefix: str) -> list[str]:
    validator = Draft202012Validator(
        _load_json(schema_path),
        format_checker=FormatChecker(),
    )
    errors: list[str] = []
    for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.path) or "$"
        errors.append(f"{prefix} schema {location}: {error.message}")
    return errors


def validate_visual_plan(
    plan: dict[str, Any], evidence_registry: dict[str, Any]
) -> list[str]:
    """Return deterministic contract violations without changing either artifact."""

    errors = _schema_errors(plan, VISUAL_PLAN_SCHEMA, "visual_plan")
    errors.extend(_schema_errors(evidence_registry, EVIDENCE_SCHEMA, "evidence_registry"))

    sources = {
        source.get("source_id"): source
        for source in evidence_registry.get("sources", [])
        if source.get("source_id")
    }
    claims = {
        claim.get("claim_id"): claim
        for claim in evidence_registry.get("claims", [])
        if claim.get("claim_id")
    }
    evidence_ids = set(sources) | set(claims)

    if plan.get("project_id") != evidence_registry.get("project_id"):
        errors.append("plan project_id must match evidence registry project_id")
    if plan.get("evidence_lock", {}).get("registry_version") != evidence_registry.get(
        "registry_version"
    ):
        errors.append("evidence_lock registry_version does not match evidence registry")

    for claim_id, claim in claims.items():
        for citation in claim.get("citations", []):
            source_id = citation.get("source_id")
            if source_id not in sources:
                errors.append(f"{claim_id}: citation source_id does not exist: {source_id}")

    seen_sequences: set[str] = set()
    seen_shots: set[str] = set()
    seen_overlays: set[str] = set()

    for sequence in plan.get("sequences", []):
        sequence_id = sequence.get("sequence_id", "UNKNOWN_SEQUENCE")
        if sequence_id in seen_sequences:
            errors.append(f"{sequence_id}: duplicate sequence_id")
        seen_sequences.add(sequence_id)

        for evidence_id in sequence.get("evidence_ids", []):
            if evidence_id not in evidence_ids:
                errors.append(f"{sequence_id}: unknown evidence_id {evidence_id}")

        planned_duration = sum(
            float(shot.get("duration_seconds", 0)) for shot in sequence.get("shots", [])
        )
        target_duration = float(sequence.get("target_duration_seconds", 0))
        if abs(planned_duration - target_duration) > 0.05:
            errors.append(
                f"{sequence_id}: shot durations {planned_duration:g}s do not equal "
                f"target {target_duration:g}s"
            )

        for shot in sequence.get("shots", []):
            shot_id = shot.get("shot_id", "UNKNOWN_SHOT")
            if shot_id in seen_shots:
                errors.append(f"{shot_id}: duplicate shot_id")
            seen_shots.add(shot_id)

            for evidence_id in shot.get("evidence_ids", []):
                if evidence_id not in evidence_ids:
                    errors.append(f"{shot_id}: unknown evidence_id {evidence_id}")

            route = shot.get("provider_route", {}).get("mode")
            representation = shot.get("representation")
            ai_required = route in AI_ROUTES or representation == "AI_RECONSTRUCTION"
            if ai_required and shot.get("contains_ai") is not True:
                errors.append(f"{shot_id}: AI route requires contains_ai=true")

            disclosure = shot.get("disclosure", {})
            if ai_required or shot.get("contains_ai") is True:
                if (
                    disclosure.get("required") is not True
                    or disclosure.get("label") not in AI_DISCLOSURE_LABELS
                ):
                    errors.append(f"{shot_id}: AI content requires disclosure")

            if route == "TOPVIEW_HANDOFF" and not shot.get("generation_brief"):
                errors.append(f"{shot_id}: TOPVIEW_HANDOFF requires generation_brief")

            factual_precision = shot.get("factual_precision")
            if factual_precision in {"high", "exact"} and not shot.get("evidence_ids"):
                errors.append(f"{shot_id}: precise factual shot requires evidence_ids")

            for overlay in shot.get("overlay", {}).get("items", []):
                overlay_id = overlay.get("overlay_id", "UNKNOWN_OVERLAY")
                if overlay_id in seen_overlays:
                    errors.append(f"{shot_id}/{overlay_id}: duplicate overlay_id")
                seen_overlays.add(overlay_id)

                source_id = overlay.get("source_id")
                if source_id is not None and source_id not in sources:
                    errors.append(f"{shot_id}/{overlay_id}: unknown source_id {source_id}")

                if overlay.get("exact_text_from_claims") is not True:
                    continue

                claim_id = overlay.get("claim_id")
                if not claim_id:
                    errors.append(f"{shot_id}/{overlay_id}: exact overlay requires claim_id")
                    continue
                claim = claims.get(claim_id)
                if claim is None:
                    errors.append(f"{shot_id}/{overlay_id}: unknown claim_id {claim_id}")
                    continue
                if claim.get("status") != "verified":
                    errors.append(f"{shot_id}/{overlay_id}: exact overlay claim must be verified")
                literal = overlay.get("literal")
                if literal is not None and literal != claim.get("text"):
                    errors.append(f"{shot_id}/{overlay_id}: literal must equal claim text")

    return errors


def assert_valid_visual_plan(
    plan: dict[str, Any], evidence_registry: dict[str, Any]
) -> None:
    """Raise one readable error when semantic or schema checks fail."""

    errors = validate_visual_plan(plan, evidence_registry)
    if errors:
        raise ValueError("Invalid VisualPlan:\n- " + "\n- ".join(errors))

