from __future__ import annotations

from copy import deepcopy

import jsonschema
import pytest

from schemas.artifacts import validate_artifact


def sample_manifest() -> dict:
    return {
        "schema_version": "1.0.0",
        "project_id": "COLLAPSE_PILOT",
        "collection_status": "completed",
        "generated_at": "2026-08-12T14:00:00Z",
        "queries": [
            {
                "query_id": "Q001",
                "text": "Rana Plaza collapse exterior",
                "kind": "image",
                "claim_ids": ["CLAIM_COLLAPSE_01"],
            }
        ],
        "source_summary": {
            "attempted": ["pexels"],
            "completed": ["pexels"],
            "failed": [],
            "discovered": 1,
            "accepted": 1,
            "downloaded": 1,
            "duplicates": 0,
            "rejected_counts": {},
        },
        "items": [
            {
                "id": "MEDIA_PEXELS_1001",
                "media_type": "image",
                "local_path": "assets/source/images/pexels_1001.jpg",
                "sha256": "a" * 64,
                "source": "pexels",
                "source_url": "https://www.pexels.com/photo/1001/",
                "direct_url": None,
                "creator": "Example Photographer",
                "license": "Pexels License",
                "license_url": "https://www.pexels.com/license/",
                "public_domain_basis": None,
                "attribution_required": False,
                "attribution_text": "",
                "allowed_uses": ["display", "transform", "commercial"],
                "accessed_at": "2026-08-12T14:00:00Z",
                "claim_ids": ["CLAIM_COLLAPSE_01"],
                "technical": {
                    "format": "jpg",
                    "width": 1920,
                    "height": 1080,
                    "duration_seconds": 0,
                    "size_bytes": 4096,
                },
            }
        ],
    }


def test_manifest_accepts_only_complete_rights_cleared_local_items() -> None:
    validate_artifact("media_collection_manifest", sample_manifest())


def test_manifest_rejects_creative_selection_fields() -> None:
    value = sample_manifest()
    value["items"][0]["selected_for_edit"] = True

    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("media_collection_manifest", value)


def test_manifest_accepts_canonical_lowercase_project_id() -> None:
    value = sample_manifest()
    value["project_id"] = "collapse-topic-pilot-2026-08-12"

    validate_artifact("media_collection_manifest", value)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("license", ""),
        ("source_url", ""),
        ("local_path", "assets/source/../restricted.jpg"),
        ("sha256", "not-a-hash"),
    ],
)
def test_manifest_rejects_unusable_or_unbound_items(field: str, value: str) -> None:
    manifest = deepcopy(sample_manifest())
    manifest["items"][0][field] = value

    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("media_collection_manifest", manifest)
