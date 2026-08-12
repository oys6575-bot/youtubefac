from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

from lib.checkpoint import init_project, write_checkpoint


ROOT = Path(__file__).resolve().parents[2]
SHORTLIST_SOURCE = (
    ROOT / "research/topic-candidates/2026-08-12-collapse-topic-shortlist.json"
)


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build_topic_gate(projects_root: Path, project_id: str = "MOBILE_TEST") -> tuple[Path, str, str]:
    project_dir = init_project(
        project_id,
        title="모바일 승인 테스트",
        pipeline_type="youtube-factory",
        pipeline_dir=projects_root,
    )
    shortlist = deepcopy(json.loads(SHORTLIST_SOURCE.read_text(encoding="utf-8")))
    shortlist["project_id"] = project_id
    shortlist_bytes = canonical_bytes(shortlist)
    shortlist_hash = sha256_bytes(shortlist_bytes)

    verification = {
        "version": "1.0",
        "project_id": project_id,
        "verdict": "PASS",
        "source_commit": "a" * 40,
        "input_path": "artifacts/topic_shortlist.json",
        "input_sha256": shortlist_hash,
        "verified_at": "2026-08-12T00:00:00+00:00",
        "source_urls": ["https://www.ntsb.gov/"],
        "candidate_results": [
            {"id": item["id"], "verdict": "PASS", "notes": "fixture verified"}
            for item in shortlist["candidates"]
        ],
        "findings": [],
        "verifier": {"runtime": "codex", "model": "gpt-5.6-sol"},
    }
    verification_bytes = canonical_bytes(verification)
    verification_hash = sha256_bytes(verification_bytes)
    selection = {
        "version": "1.0",
        "project_id": project_id,
        "shortlist_sha256": shortlist_hash,
        "verification_sha256": verification_hash,
        "selection_status": "PENDING",
        "selected_candidate_id": None,
        "human_approved": False,
    }

    artifacts_dir = project_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    (artifacts_dir / "topic_shortlist.json").write_bytes(shortlist_bytes)
    (artifacts_dir / "topic_verification.json").write_bytes(verification_bytes)
    (artifacts_dir / "topic_selection.json").write_bytes(canonical_bytes(selection))

    write_checkpoint(
        projects_root,
        project_id,
        "topic_search",
        "completed",
        {"topic_shortlist": shortlist},
        pipeline_type="youtube-factory",
    )
    write_checkpoint(
        projects_root,
        project_id,
        "topic_verification",
        "completed",
        {"topic_verification": verification},
        pipeline_type="youtube-factory",
    )
    checkpoint = write_checkpoint(
        projects_root,
        project_id,
        "topic_approval",
        "awaiting_human",
        {"topic_selection": selection},
        pipeline_type="youtube-factory",
        human_approval_required=True,
    )
    candidate_id = shortlist["candidates"][0]["id"]
    return project_dir, candidate_id, sha256_bytes(checkpoint.read_bytes())

