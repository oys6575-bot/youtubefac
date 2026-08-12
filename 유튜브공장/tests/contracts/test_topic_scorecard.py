from __future__ import annotations

from copy import deepcopy

import pytest

from lib.topic_scorecard import (
    ScorecardError,
    load_scorecard,
    rank_candidates,
    score_candidate,
)


def candidate(candidate_id: str = "case-a") -> dict:
    return {
        "id": candidate_id,
        "scope": {
            "human_made_structure": True,
            "physical_collapse": True,
            "scope_verified": True,
        },
        "scores": {
            "event_pull": 5,
            "causal_depth": 5,
            "belief_reversal": 5,
            "evidence_verifiability": 5,
            "narrative_expandability": 5,
            "visual_explainability": 5,
            "meaning_and_lessons": 5,
            "korean_content_scarcity": 5,
        },
    }


def test_scorecard_weights_total_one_hundred() -> None:
    config = load_scorecard()
    assert sum(item["weight"] for item in config["criteria"].values()) == 100


def test_perfect_candidate_is_priority_with_literal_weighted_scores() -> None:
    result = score_candidate(candidate())
    assert result["weighted_scores"] == {
        "event_pull": 15,
        "causal_depth": 20,
        "belief_reversal": 15,
        "evidence_verifiability": 20,
        "narrative_expandability": 10,
        "visual_explainability": 10,
        "meaning_and_lessons": 5,
        "korean_content_scarcity": 5,
    }
    assert result["total"] == 100
    assert result["status"] == "PRIORITY"


def test_low_evidence_overrides_high_total() -> None:
    item = candidate()
    item["scores"]["evidence_verifiability"] = 2
    result = score_candidate(item)
    assert result["weighted_scores"]["evidence_verifiability"] == 8
    assert result["status"] == "HOLD_NEEDS_EVIDENCE"


def test_unassessed_score_prevents_final_total() -> None:
    item = candidate()
    item["scores"]["belief_reversal"] = "UNASSESSED"
    result = score_candidate(item)
    assert result["total"] is None
    assert result["status"] == "UNASSESSED"


def test_scope_gate_precedes_scoring() -> None:
    item = candidate()
    item["scope"]["physical_collapse"] = False
    result = score_candidate(item)
    assert result["total"] is None
    assert result["status"] == "OUT_OF_SCOPE"


def test_unverified_scope_prevents_scoring() -> None:
    item = candidate()
    item["scope"]["scope_verified"] = False
    result = score_candidate(item)
    assert result["total"] is None
    assert result["status"] == "UNASSESSED"


def test_scores_outside_zero_to_five_are_rejected() -> None:
    item = candidate()
    item["scores"]["event_pull"] = 6
    with pytest.raises(ScorecardError, match="event_pull"):
        score_candidate(item)


def test_full_tie_keeps_shared_rank() -> None:
    first = candidate("case-a")
    second = deepcopy(first)
    second["id"] = "case-b"
    ranked = rank_candidates([second, first])
    assert [item["id"] for item in ranked] == ["case-a", "case-b"]
    assert [item["rank"] for item in ranked] == [1, 1]
