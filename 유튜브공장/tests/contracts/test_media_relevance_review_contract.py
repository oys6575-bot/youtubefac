from __future__ import annotations

from copy import deepcopy

import jsonschema
import pytest

from schemas.artifacts import validate_artifact


def review_fixture(*, category: str = "unrelated", identity_evidence=None) -> dict:
    identity = list(identity_evidence or [])
    eligibility = {
        "event_direct": "eligible",
        "news_report": "eligible",
        "official_record": "eligible",
        "explanatory": "eligible",
        "generic_broll": "excluded",
        "unrelated": "excluded",
        "unknown": "held",
    }[category]
    return {
        "schema_version": "1.0.0",
        "project_id": "collapse-topic-pilot-2026-08-12",
        "review_status": "completed",
        "generated_at": "2026-08-13T00:00:00+00:00",
        "base_manifest_sha256": "a" * 64,
        "supplement_manifest": None,
        "topic_identity": {
            "canonical_name": "Rana Plaza collapse",
            "aliases": ["Rana Plaza", "Savar building collapse"],
            "locations": ["Savar", "Bangladesh"],
            "dates": ["2013-04-24"],
        },
        "decisions": [
            {
                "media_id": "MEDIA_ONE",
                "media_sha256": "b" * 64,
                "category": category,
                "eligibility": eligibility,
                "relevance_score": 8,
                "identity_evidence": identity,
                "mismatch_evidence": ["wrong event"] if category == "unrelated" else [],
                "visual_summary": "sample",
                "usefulness": "excluded from automatic candidates",
                "review_method": ["metadata"],
                "reviewed_at": "2026-08-13T00:00:00+00:00",
            }
        ],
        "coverage": [
            {
                "lane": "event_site",
                "status": "missing",
                "eligible_media_ids": [],
            }
        ],
        "counts": {
            "total": 1,
            "eligible": int(eligibility == "eligible"),
            "excluded": int(eligibility == "excluded"),
            "held": int(eligibility == "held"),
            "by_category": {category: 1},
        },
    }


def test_review_requires_manifest_binding() -> None:
    review = review_fixture()
    validate_artifact("media_relevance_review", review)
    broken = deepcopy(review)
    broken["base_manifest_sha256"] = "not-a-hash"
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("media_relevance_review", broken)


@pytest.mark.parametrize("category", ["event_direct", "news_report"])
def test_event_or_news_requires_identity_evidence(category: str) -> None:
    review = review_fixture(category=category, identity_evidence=[])
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("media_relevance_review", review)


def test_review_rejects_duplicate_media_decisions() -> None:
    review = review_fixture()
    review["decisions"].append(deepcopy(review["decisions"][0]))
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("media_relevance_review", review)

