"""Deterministic, provider-neutral topic scoring for physical collapse cases."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


FACTORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCORECARD_PATH = FACTORY_ROOT / "config" / "topic-selection-scorecard.yaml"

EXPECTED_CRITERIA = {
    "event_pull",
    "causal_depth",
    "belief_reversal",
    "evidence_verifiability",
    "narrative_expandability",
    "visual_explainability",
    "meaning_and_lessons",
    "korean_content_scarcity",
}


class ScorecardError(ValueError):
    """Raised when scorecard configuration or candidate input is invalid."""


def _require_mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ScorecardError(f"{label} must be an object")
    return value


def load_scorecard(path: Path | str = DEFAULT_SCORECARD_PATH) -> dict[str, Any]:
    """Load and audit the canonical topic scorecard configuration."""

    scorecard_path = Path(path)
    try:
        payload = yaml.safe_load(scorecard_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ScorecardError(f"Cannot load topic scorecard: {scorecard_path}: {exc}") from exc

    config = dict(_require_mapping(payload, "scorecard root"))
    criteria = _require_mapping(config.get("criteria"), "criteria")
    if set(criteria) != EXPECTED_CRITERIA:
        missing = sorted(EXPECTED_CRITERIA - set(criteria))
        extra = sorted(set(criteria) - EXPECTED_CRITERIA)
        raise ScorecardError(f"criteria mismatch; missing={missing}, extra={extra}")

    weights: list[int] = []
    for criterion_id, criterion in criteria.items():
        record = _require_mapping(criterion, f"criteria.{criterion_id}")
        weight = record.get("weight")
        if type(weight) is not int or weight <= 0 or weight % 5:
            raise ScorecardError(
                f"criteria.{criterion_id}.weight must be a positive multiple of 5"
            )
        weights.append(weight)
    if sum(weights) != 100:
        raise ScorecardError(f"criterion weights must total 100, got {sum(weights)}")

    raw_score = _require_mapping(config.get("raw_score"), "raw_score")
    if (raw_score.get("minimum"), raw_score.get("maximum")) != (0, 5):
        raise ScorecardError("raw_score range must be 0..5")
    if raw_score.get("unassessed") != "UNASSESSED":
        raise ScorecardError("raw_score.unassessed must be UNASSESSED")

    scope_gate = _require_mapping(config.get("scope_gate"), "scope_gate")
    if scope_gate.get("required_true") != [
        "human_made_structure",
        "physical_collapse",
    ]:
        raise ScorecardError("scope_gate.required_true does not match the approved scope")
    if scope_gate.get("verification_field") != "scope_verified":
        raise ScorecardError("scope_gate.verification_field must be scope_verified")

    thresholds = config.get("status_thresholds")
    if not isinstance(thresholds, list) or not thresholds:
        raise ScorecardError("status_thresholds must be a non-empty list")
    covered: dict[int, str] = {}
    for threshold in thresholds:
        record = _require_mapping(threshold, "status_threshold")
        minimum = record.get("minimum")
        maximum = record.get("maximum")
        status = record.get("status")
        if type(minimum) is not int or type(maximum) is not int or not isinstance(status, str):
            raise ScorecardError("status threshold requires integer bounds and a status")
        for value in range(minimum, maximum + 1):
            if value in covered:
                raise ScorecardError(f"overlapping status threshold at {value}")
            covered[value] = status
    if set(covered) != set(range(101)):
        raise ScorecardError("status thresholds must cover every total from 0 through 100")

    evidence_hold = _require_mapping(config.get("evidence_hold"), "evidence_hold")
    if evidence_hold.get("criterion") != "evidence_verifiability":
        raise ScorecardError("evidence hold must use evidence_verifiability")
    if evidence_hold.get("minimum_weighted_score") != 12:
        raise ScorecardError("evidence hold threshold must be 12")

    tie_break_order = config.get("tie_break_order")
    if tie_break_order != ["evidence_verifiability", "causal_depth", "event_pull"]:
        raise ScorecardError("tie_break_order does not match the approved order")
    return config


def _scope_status(candidate: Mapping[str, Any], config: Mapping[str, Any]) -> str | None:
    scope = _require_mapping(candidate.get("scope"), "candidate.scope")
    scope_gate = _require_mapping(config["scope_gate"], "scope_gate")
    for field in scope_gate["required_true"]:
        value = scope.get(field)
        if value is None:
            return "UNASSESSED"
        if type(value) is not bool:
            raise ScorecardError(f"candidate.scope.{field} must be boolean")
        if value is False:
            return "OUT_OF_SCOPE"

    verification_field = scope_gate["verification_field"]
    verified = scope.get(verification_field)
    if verified is None or verified is False:
        return "UNASSESSED"
    if type(verified) is not bool:
        raise ScorecardError(f"candidate.scope.{verification_field} must be boolean")
    return None


def score_candidate(
    candidate: Mapping[str, Any],
    scorecard: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a copy of one candidate with weighted scores, total, and status."""

    config = dict(scorecard) if scorecard is not None else load_scorecard()
    item = deepcopy(dict(candidate))
    candidate_id = item.get("id")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ScorecardError("candidate.id must be a non-empty string")

    scope_status = _scope_status(item, config)
    if scope_status is not None:
        item["weighted_scores"] = {}
        item["total"] = None
        item["status"] = scope_status
        return item

    scores = _require_mapping(item.get("scores"), "candidate.scores")
    criteria = _require_mapping(config["criteria"], "criteria")
    if set(scores) != set(criteria):
        missing = sorted(set(criteria) - set(scores))
        extra = sorted(set(scores) - set(criteria))
        raise ScorecardError(
            f"candidate.scores mismatch; missing={missing}, extra={extra}"
        )

    unassessed_token = config["raw_score"]["unassessed"]
    weighted_scores: dict[str, int | None] = {}
    has_unassessed = False
    for criterion_id, criterion in criteria.items():
        raw_value = scores[criterion_id]
        if raw_value == unassessed_token:
            weighted_scores[criterion_id] = None
            has_unassessed = True
            continue
        if type(raw_value) is not int or not 0 <= raw_value <= 5:
            raise ScorecardError(f"candidate.scores.{criterion_id} must be 0..5 or UNASSESSED")
        weighted_scores[criterion_id] = raw_value * criterion["weight"] // 5

    item["weighted_scores"] = weighted_scores
    if has_unassessed:
        item["total"] = None
        item["status"] = "UNASSESSED"
        return item

    total = sum(value for value in weighted_scores.values() if value is not None)
    status = next(
        threshold["status"]
        for threshold in config["status_thresholds"]
        if threshold["minimum"] <= total <= threshold["maximum"]
    )
    evidence_hold = config["evidence_hold"]
    evidence_score = weighted_scores[evidence_hold["criterion"]]
    if evidence_score is not None and evidence_score < evidence_hold["minimum_weighted_score"]:
        status = evidence_hold["status"]

    item["total"] = total
    item["status"] = status
    return item


def rank_candidates(
    candidates: Iterable[Mapping[str, Any]],
    scorecard: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Score and rank candidates while preserving exact ties as shared ranks."""

    config = dict(scorecard) if scorecard is not None else load_scorecard()
    scored = [score_candidate(candidate, config) for candidate in candidates]
    tie_break_order = config["tie_break_order"]

    def comparison(item: Mapping[str, Any]) -> tuple[int, ...]:
        total = item["total"] if item["total"] is not None else -1
        weighted = item["weighted_scores"]
        tie_values = [
            weighted.get(criterion_id)
            if weighted.get(criterion_id) is not None
            else -1
            for criterion_id in tie_break_order
        ]
        return (total, *tie_values)

    scored.sort(key=lambda item: (*(-value for value in comparison(item)), item["id"]))
    previous_key: tuple[int, ...] | None = None
    previous_rank = 0
    for index, item in enumerate(scored, start=1):
        current_key = comparison(item)
        if current_key != previous_key:
            previous_rank = index
        item["rank"] = previous_rank
        previous_key = current_key
    return scored
