from __future__ import annotations

from tools.video.media_relevance_review import review_manifest, review_one


NOW = "2026-08-13T00:00:00+00:00"


def rana_plaza_identity() -> dict:
    return {
        "canonical_name": "Rana Plaza collapse",
        "aliases": ["Rana Plaza", "Savar building collapse"],
        "locations": ["Savar", "Bangladesh"],
        "dates": ["2013-04-24", "24 April 2013"],
    }


def item(media_id: str, source_url: str, **extra) -> dict:
    value = {
        "id": media_id,
        "sha256": (media_id.lower().encode().hex() + "0" * 64)[:64],
        "source": "fixture",
        "source_url": source_url,
        "direct_url": None,
        "creator": "",
        "media_type": "image",
        "claim_ids": ["CLAIM_WARNING_CRACKS"],
    }
    value.update(extra)
    return value


def test_query_claim_cannot_promote_ukraine_war_ruins() -> None:
    decision = review_one(
        item("MEDIA_BAD", "https://pexels.com/video/war-in-ukraine-1/"),
        rana_plaza_identity(),
        reviewed_at=NOW,
    )
    assert decision["category"] == "unrelated"
    assert decision["eligibility"] == "excluded"
    assert "CLAIM_WARNING_CRACKS" not in decision["identity_evidence"]


def test_exact_rana_plaza_news_metadata_is_news_report() -> None:
    decision = review_one(
        item(
            "MEDIA_NEWS",
            "https://archive.org/details/rana-plaza-news-report-2013",
            title="Rana Plaza collapse news report, Savar, 24 April 2013",
        ),
        rana_plaza_identity(),
        reviewed_at=NOW,
    )
    assert decision["category"] == "news_report"
    assert decision["eligibility"] == "eligible"
    assert decision["identity_evidence"]


def test_wikimedia_savar_filename_is_direct_event_evidence() -> None:
    decision = review_one(
        item(
            "MEDIA_COMMONS",
            "https://commons.wikimedia.org/wiki/File:2013_savar_building_collapse_aftermath.jpg",
        ),
        rana_plaza_identity(),
        reviewed_at=NOW,
    )
    assert decision["category"] == "event_direct"
    assert decision["eligibility"] == "eligible"


def test_ambiguous_item_fails_closed_without_visual_evidence() -> None:
    decision = review_one(
        item("MEDIA_AMBIGUOUS", "https://example.test/asset/1", claim_ids=[]),
        rana_plaza_identity(),
        reviewed_at=NOW,
    )
    assert decision["category"] == "unknown"
    assert decision["eligibility"] == "held"


def test_generic_crack_and_sewing_broll_are_excluded_by_default() -> None:
    crack = review_one(
        item("MEDIA_CRACK", "https://pexels.com/photo/crack-on-concrete-wall-1"),
        rana_plaza_identity(),
        reviewed_at=NOW,
    )
    sewing = review_one(
        item("MEDIA_SEW", "https://pexels.com/video/person-sewing-clothing-2"),
        rana_plaza_identity(),
        reviewed_at=NOW,
    )
    assert crack["category"] == "generic_broll"
    assert sewing["category"] == "generic_broll"
    assert crack["eligibility"] == sewing["eligibility"] == "excluded"


def test_review_manifest_is_stable_and_aggregates_coverage() -> None:
    manifest = {
        "schema_version": "1.0.0",
        "project_id": "collapse-topic-pilot-2026-08-12",
        "items": [
            item(
                "MEDIA_NEWS",
                "https://archive.org/details/rana-plaza-news-report-2013",
                title="Rana Plaza news broadcast",
            ),
            item("MEDIA_BAD", "https://pexels.com/video/syria-earthquake-1"),
        ],
    }
    result = review_manifest(
        manifest,
        "a" * 64,
        rana_plaza_identity(),
        generated_at=NOW,
    )
    assert [row["media_id"] for row in result["decisions"]] == ["MEDIA_BAD", "MEDIA_NEWS"]
    assert result["counts"] == {
        "total": 2,
        "eligible": 1,
        "excluded": 1,
        "held": 0,
        "by_category": {"news_report": 1, "unrelated": 1},
    }
    news = next(row for row in result["coverage"] if row["lane"] == "news_newspaper")
    assert news["status"] == "covered"
    assert news["eligible_media_ids"] == ["MEDIA_NEWS"]
