from __future__ import annotations

from pathlib import Path

import pytest

from schemas.artifacts import validate_artifact
from tools.video.stock_sources.base import Candidate


class FakeSource:
    name = "fake"

    def __init__(self, candidates: list[Candidate], payload: bytes | None = None):
        self.candidates = candidates
        self.payload = payload or (b"rights-cleared-media" * 256)
        self.download_calls: list[str] = []

    def is_available(self) -> bool:
        return True

    def search(self, query, filters):
        del query, filters
        return list(self.candidates)

    def download(self, candidate: Candidate, out_path: Path) -> Path:
        self.download_calls.append(candidate.clip_id)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(self.payload)
        return out_path


def candidate(
    *,
    source_id: str = "1001",
    license: str = "CC BY 4.0",
    source_url: str = "https://example.test/item/1001",
    download_url: str = "https://example.test/files/1001.jpg",
    source_tags: str = "collapse exterior",
) -> Candidate:
    return Candidate(
        source="fake",
        source_id=source_id,
        source_url=source_url,
        download_url=download_url,
        kind="image",
        width=1920,
        height=1080,
        creator="Archive Photographer",
        license=license,
        source_tags=source_tags,
    )


def run_collection(tmp_path: Path, monkeypatch, source: FakeSource):
    from tools.video.rights_cleared_media_collection import (
        RightsClearedMediaCollection,
    )

    monkeypatch.setattr(
        "tools.video.stock_sources.available_sources", lambda: [source]
    )
    return RightsClearedMediaCollection().execute(
        {
            "project_id": "COLLAPSE_PILOT",
            "output_dir": str(tmp_path / "assets/source"),
            "queries": [
                {
                    "query": "Rana Plaza collapse exterior",
                    "kind": "image",
                    "claim_ids": ["CLAIM_COLLAPSE_01"],
                }
            ],
            "max_items_per_query": 5,
        }
    )


@pytest.mark.parametrize(
    ("license_text", "reason"),
    [
        ("", "unknown_rights"),
        ("Permission required", "permission_required"),
        ("Editorial use only", "restricted_use"),
        ("CC BY-NC 4.0", "noncommercial"),
        ("CC BY-ND 4.0", "no_derivatives"),
        ("Wikimedia Commons (verify per-file license)", "unknown_rights"),
    ],
)
def test_unusable_rights_are_rejected_before_download(
    tmp_path: Path,
    monkeypatch,
    license_text: str,
    reason: str,
) -> None:
    source = FakeSource([candidate(license=license_text)])

    result = run_collection(tmp_path, monkeypatch, source)

    assert result.success is True
    assert result.data["accepted"] == 0
    assert result.data["rejected_counts"] == {reason: 1}
    assert source.download_calls == []
    assert list((tmp_path / "assets/source").rglob("*.jpg")) == []


def test_watermarked_candidate_is_rejected_before_download(
    tmp_path: Path, monkeypatch
) -> None:
    source = FakeSource(
        [candidate(license="CC BY 4.0", source_tags="watermarked preview")]
    )

    result = run_collection(tmp_path, monkeypatch, source)

    assert result.data["rejected_counts"] == {"preview_or_watermark": 1}
    assert source.download_calls == []


def test_explicit_reusable_license_downloads_and_validates_manifest(
    tmp_path: Path, monkeypatch
) -> None:
    source = FakeSource([candidate(license="CC BY 4.0")])

    result = run_collection(tmp_path, monkeypatch, source)

    assert result.success is True
    assert result.data["accepted"] == 1
    assert result.data["downloaded"] == 1
    assert source.download_calls == ["fake_1001"]
    manifest = result.data["manifest"]
    validate_artifact("media_collection_manifest", manifest)
    item = manifest["items"][0]
    assert item["local_path"].startswith("assets/source/images/")
    assert (tmp_path / item["local_path"]).is_file()
    assert item["allowed_uses"] == ["display", "transform", "commercial"]
    assert "selected_for_edit" not in item


def test_retry_reuses_existing_file_without_duplicate_bytes(
    tmp_path: Path, monkeypatch
) -> None:
    source = FakeSource([candidate(license="Pexels License")])

    first = run_collection(tmp_path, monkeypatch, source)
    second = run_collection(tmp_path, monkeypatch, source)

    assert first.data["accepted"] == 1
    assert second.data["accepted"] == 1
    assert second.data["downloaded"] == 0
    assert second.data["duplicates"] == 1
    assert source.download_calls == ["fake_1001"]
    assert len(list((tmp_path / "assets/source/images").iterdir())) == 1


def test_one_source_failure_preserves_other_source_success(
    tmp_path: Path, monkeypatch
) -> None:
    class FailedSource(FakeSource):
        name = "failed"

        def search(self, query, filters):
            del query, filters
            raise RuntimeError("source unavailable")

    accepted = FakeSource([candidate(license="CC0 1.0")])
    failed = FailedSource([])
    from tools.video.rights_cleared_media_collection import (
        RightsClearedMediaCollection,
    )

    monkeypatch.setattr(
        "tools.video.stock_sources.available_sources", lambda: [failed, accepted]
    )
    result = RightsClearedMediaCollection().execute(
        {
            "project_id": "COLLAPSE_PILOT",
            "output_dir": str(tmp_path / "assets/source"),
            "queries": [
                {
                    "query": "collapse exterior",
                    "kind": "image",
                    "claim_ids": [],
                }
            ],
        }
    )

    assert result.success is True
    assert result.data["accepted"] == 1
    assert result.data["source_errors"][0]["source"] == "failed"
    assert result.data["manifest"]["collection_status"] == "partial"
