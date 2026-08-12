from __future__ import annotations

import json
from pathlib import Path

from lib.topic_scorecard import rank_candidates
from schemas.artifacts import validate_artifact


ROOT = Path(__file__).resolve().parents[2]
SHORTLIST = (
    ROOT
    / "research"
    / "topic-candidates"
    / "2026-08-12-collapse-topic-shortlist.json"
)


def test_shortlist_is_in_scope_source_backed_and_scoreable() -> None:
    payload = json.loads(SHORTLIST.read_text(encoding="utf-8"))
    validate_artifact("topic_shortlist", payload)
    candidates = payload["candidates"]
    assert len(candidates) >= 10
    assert len({item["id"] for item in candidates}) == len(candidates)

    forbidden = {
        "generation_model",
        "production_platform",
        "production_cost",
        "render_time",
        "archive_footage_quantity",
    }
    for item in candidates:
        assert item["provisional"] is True
        assert item["scope"] == {
            "human_made_structure": True,
            "physical_collapse": True,
            "scope_verified": True,
        }
        assert item["sources"]
        assert any(
            source["class"] == "official_or_primary" for source in item["sources"]
        )
        assert all(source["url"].startswith("http") for source in item["sources"])
        assert item["korean_youtube_landscape"]["query"]
        assert not forbidden & set(item)

    ranked = rank_candidates(candidates)
    assert len(ranked) == len(candidates)
    assert all(item["status"] != "UNASSESSED" for item in ranked)
    assert all(item["status"] != "OUT_OF_SCOPE" for item in ranked)
