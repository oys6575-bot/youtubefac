from __future__ import annotations

from tools.video.media_archive_supplement import (
    ARCHIVE_SOURCE_ALLOWLIST,
    build_supplement_queries,
    collect_archive_supplement,
)


def identity() -> dict:
    return {
        "canonical_name": "Rana Plaza collapse",
        "aliases": ["Rana Plaza"],
        "locations": ["Savar", "Bangladesh"],
        "dates": ["2013-04-24"],
    }


def test_archive_queries_are_exact_event_and_only_fill_missing_lanes() -> None:
    specs = build_supplement_queries(
        identity(), missing={"news_newspaper", "official_record"}
    )
    assert {row["lane"] for row in specs} == {"news_newspaper", "official_record"}
    assert all("Rana Plaza" in row["query"] for row in specs)


def test_supplement_uses_only_archive_allowlist() -> None:
    assert ARCHIVE_SOURCE_ALLOWLIST == (
        "archive_org",
        "wikimedia",
        "nara",
        "loc",
        "pond5_pd",
    )


def test_no_missing_lanes_returns_empty_manifest_without_calling_collector(tmp_path) -> None:
    class Never:
        def execute(self, _inputs):  # pragma: no cover - proves no call
            raise AssertionError("collector should not run")

    result = collect_archive_supplement(
        project_id="pilot",
        output_dir=tmp_path / "assets/source",
        topic_identity=identity(),
        missing_lanes=set(),
        collector=Never(),
        available_source_names=ARCHIVE_SOURCE_ALLOWLIST,
        generated_at="2026-08-13T00:00:00+00:00",
    )
    assert result["items"] == []
    assert result["source_summary"]["attempted"] == []


def test_collector_receives_exact_queries_and_only_available_allowlisted_sources(tmp_path) -> None:
    class Result:
        success = True
        data = {"manifest": {"items": ["sentinel"]}}

    class Collector:
        def __init__(self):
            self.inputs = None

        def execute(self, inputs):
            self.inputs = inputs
            return Result()

    collector = Collector()
    result = collect_archive_supplement(
        project_id="pilot",
        output_dir=tmp_path / "assets/source",
        topic_identity=identity(),
        missing_lanes={"news_newspaper"},
        collector=collector,
        available_source_names=("wikimedia", "pexels", "archive_org"),
    )
    assert result == {"items": ["sentinel"]}
    assert collector.inputs["sources"] == ["archive_org", "wikimedia"]
    assert all("Rana Plaza" in row["query"] for row in collector.inputs["queries"])
    assert collector.inputs["progress_path"].endswith(
        "automation/progress/media_archive_supplement.json"
    )
    assert "Rana Plaza" in collector.inputs["required_identity_phrases"]
