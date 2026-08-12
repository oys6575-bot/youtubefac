from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from backlot.auto_dispatch import JobValidationError, load_job
from backlot.auto_dispatch_worker import Coordinator
from backlot.mobile_actions import Actor, execute_action
from backlot.orca_auto_dispatch import StageResult
from tests.backlot.mobile_fixtures import build_topic_gate, canonical_bytes
from tests.backlot.test_mobile_actions import payload
from tests.contracts.test_phase0_contracts import sample_artifact


ACTOR = Actor(tailscale_login="owner@example.com", tailscale_user_id="123")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _checkpoint(project: Path, stage: str, status: str, artifacts: dict) -> Path:
    value = {
        "version": "1.0",
        "project_id": project.name,
        "pipeline_type": "youtube-factory",
        "stage": stage,
        "status": status,
        "timestamp": "2026-08-12T00:00:00+00:00",
        "checkpoint_policy": "guided",
        "human_approval_required": stage == "proposal",
        "human_approved": False,
        "artifacts": artifacts,
    }
    path = project / f"checkpoint_{stage}.json"
    path.write_bytes(canonical_bytes(value))
    return path


def _write_stage_outputs(project: Path, stage: str) -> list[str]:
    artifacts = project / "artifacts"
    artifacts.mkdir(exist_ok=True)
    if stage == "research":
        brief = sample_artifact("research_brief")
        registry = {
            "schema_version": "1.0.0",
            "registry_version": "test-1",
            "project_id": project.name,
            "sources": [],
            "claims": [],
        }
        values = {
            "artifacts/research_brief.json": brief,
            "artifacts/evidence_registry.json": registry,
        }
        checkpoint_artifacts = {
            "research_brief": brief,
            "evidence_registry": registry,
        }
        checkpoint = _checkpoint(project, stage, "completed", checkpoint_artifacts)
    elif stage == "media_collection":
        source_file = project / "assets/source/images/pexels_1001.jpg"
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_bytes(b"rights-cleared-test-media" * 256)
        manifest = {
            "schema_version": "1.0.0",
            "project_id": project.name,
            "collection_status": "completed",
            "generated_at": "2026-08-12T00:00:00+00:00",
            "queries": [],
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
                    "sha256": _sha256(source_file),
                    "source": "pexels",
                    "source_url": "https://www.pexels.com/photo/1001/",
                    "direct_url": None,
                    "creator": "Test Photographer",
                    "license": "Pexels License",
                    "license_url": "https://www.pexels.com/license/",
                    "public_domain_basis": None,
                    "attribution_required": False,
                    "attribution_text": "",
                    "allowed_uses": ["display", "transform", "commercial"],
                    "accessed_at": "2026-08-12T00:00:00+00:00",
                    "claim_ids": [],
                    "technical": {
                        "format": "jpg",
                        "width": 1920,
                        "height": 1080,
                        "duration_seconds": 0,
                        "size_bytes": source_file.stat().st_size,
                    },
                }
            ],
        }
        progress = {
            "version": "1.0",
            "project_id": project.name,
            "state": "completed",
            "current_source": None,
            "current_query": None,
            "sources": {
                "attempted": ["pexels"],
                "completed": ["pexels"],
                "failed": [],
            },
            "counts": {
                "discovered": 1,
                "accepted": 1,
                "downloaded": 1,
                "duplicates": 0,
                "rejected": 0,
            },
            "rejected_counts": {},
            "elapsed_seconds": 1.25,
            "updated_at": "2026-08-12T00:00:00+00:00",
            "error": None,
        }
        values = {
            "artifacts/media_collection_manifest.json": manifest,
            "automation/progress/media_collection.json": progress,
        }
        checkpoint = _checkpoint(
            project,
            stage,
            "completed",
            {"media_collection_manifest": manifest},
        )
    elif stage == "media_relevance_review":
        manifest_path = artifacts / "media_collection_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        item = manifest["items"][0]
        review = {
            "schema_version": "1.0.0",
            "project_id": project.name,
            "review_status": "completed",
            "generated_at": "2026-08-12T00:00:00+00:00",
            "base_manifest_sha256": _sha256(manifest_path),
            "supplement_manifest": None,
            "topic_identity": {
                "canonical_name": "Rana Plaza collapse",
                "aliases": ["Rana Plaza"],
                "locations": ["Savar", "Bangladesh"],
                "dates": ["2013-04-24"],
            },
            "decisions": [{
                "media_id": item["id"],
                "media_sha256": item["sha256"],
                "category": "unknown",
                "eligibility": "held",
                "relevance_score": 0,
                "identity_evidence": [],
                "mismatch_evidence": [],
                "visual_summary": "",
                "usefulness": "identity not established",
                "review_method": ["metadata"],
                "reviewed_at": "2026-08-12T00:00:00+00:00",
            }],
            "coverage": [{
                "lane": "event_site", "status": "missing", "eligible_media_ids": []
            }],
            "counts": {
                "total": 1, "eligible": 0, "excluded": 0, "held": 1,
                "by_category": {"unknown": 1},
            },
        }
        progress = {
            "version": "1.0",
            "project_id": project.name,
            "state": "completed",
            "phase": "final_review",
            "counts": {
                "total": 1, "reviewed": 1, "eligible": 0, "excluded": 0, "held": 1
            },
            "updated_at": "2026-08-12T00:00:00+00:00",
            "error": None,
        }
        values = {
            "artifacts/media_relevance_review.json": review,
            "automation/progress/media_relevance_review.json": progress,
        }
        checkpoint = _checkpoint(
            project, stage, "completed", {"media_relevance_review": review}
        )
    elif stage == "evidence_lock":
        registry = json.loads((artifacts / "evidence_registry.json").read_text())
        decision = {"version": "1.0", "project_id": project.name, "decisions": []}
        values = {
            "artifacts/evidence_registry.json": registry,
            "artifacts/decision_log.json": decision,
        }
        checkpoint = _checkpoint(
            project,
            stage,
            "completed",
            {"evidence_registry": registry, "decision_log": decision},
        )
    else:
        proposal = sample_artifact("proposal_packet")
        proposal["approval"] = {"status": "pending"}
        decision = {"version": "1.0", "project_id": project.name, "decisions": []}
        values = {
            "artifacts/proposal_packet.json": proposal,
            "artifacts/decision_log.json": decision,
        }
        checkpoint = _checkpoint(
            project,
            stage,
            "awaiting_human",
            {"proposal_packet": proposal, "decision_log": decision},
        )
    for relative, value in values.items():
        path = project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_bytes(value))
    return [*values, checkpoint.relative_to(project).as_posix()]


def success(project: Path, stage: str) -> StageResult:
    paths = _write_stage_outputs(project, stage)
    return StageResult(
        outcome="success",
        artifact_paths=paths,
        artifact_sha256={path: _sha256(project / path) for path in paths},
        source_commit="a" * 40,
        verdict="PASS" if stage == "evidence_lock" else "NOT_APPLICABLE",
        run_id="run_test",
        task_id=f"task_{stage}",
        dispatch_id=f"dispatch_{stage}",
    )


def ordinary_failure(stage: str) -> StageResult:
    return StageResult.failure(stage, "ordinary", "temporary agent failure")


def policy_failure(stage: str) -> StageResult:
    return StageResult.failure(stage, "policy", "paid provider requested")


class FakeRunner:
    def __init__(self, results: list[object]) -> None:
        self.results = list(results)
        self.calls: list[str] = []

    def run_stage(self, project: Path, job: dict, stage: str) -> StageResult:
        self.calls.append(stage)
        result = self.results.pop(0)
        if result == "success":
            return success(project, stage)
        if isinstance(result, BaseException):
            raise result
        assert isinstance(result, StageResult)
        return result


@pytest.fixture
def project_with_job(tmp_path: Path) -> tuple[Path, Path]:
    project, candidate, expected = build_topic_gate(tmp_path)
    execute_action(tmp_path, payload(candidate, expected), ACTOR)
    job_path = next((project / "automation/jobs").glob("*.json"))
    return project, job_path


def test_worker_runs_five_stages_and_stops_at_proposal_gate(
    project_with_job: tuple[Path, Path],
) -> None:
    project, job_path = project_with_job
    runner = FakeRunner(["success", "success", "success", "success", "success"])

    assert Coordinator(project.parent, runner).process_next() is True

    job = load_job(job_path)
    assert job["state"] == "awaiting_human"
    assert [result["stage"] for result in job["stage_results"]] == [
        "research",
        "media_collection",
        "media_relevance_review",
        "evidence_lock",
        "proposal",
    ]
    proposal = json.loads((project / "checkpoint_proposal.json").read_text())
    assert proposal["status"] == "awaiting_human"
    assert proposal["human_approved"] is False
    assert not (project / "checkpoint_script.json").exists()


def test_worker_retries_one_ordinary_failure_only(
    project_with_job: tuple[Path, Path],
) -> None:
    project, job_path = project_with_job
    runner = FakeRunner(
        [ordinary_failure("research"), "success", "success", "success", "success", "success"]
    )

    Coordinator(project.parent, runner).process_next()

    assert runner.calls.count("research") == 2
    assert load_job(job_path)["state"] == "awaiting_human"


def test_policy_failure_is_not_retried(
    project_with_job: tuple[Path, Path],
) -> None:
    project, job_path = project_with_job
    runner = FakeRunner([policy_failure("research")])

    Coordinator(project.parent, runner).process_next()

    assert runner.calls == ["research"]
    assert load_job(job_path)["state"] == "failed"


def test_restart_skips_hash_bound_settled_stage(
    project_with_job: tuple[Path, Path],
) -> None:
    project, job_path = project_with_job
    crashing = FakeRunner(["success", KeyboardInterrupt()])
    with pytest.raises(KeyboardInterrupt):
        Coordinator(project.parent, crashing).process_next()
    assert [result["stage"] for result in load_job(job_path)["stage_results"]] == [
        "research"
    ]

    resumed = FakeRunner(["success", "success", "success", "success"])
    Coordinator(project.parent, resumed).process_next()

    assert resumed.calls == [
        "media_collection", "media_relevance_review", "evidence_lock", "proposal"
    ]
    assert load_job(job_path)["state"] == "awaiting_human"


def test_restart_fails_closed_when_settled_artifact_changed(
    project_with_job: tuple[Path, Path],
) -> None:
    project, job_path = project_with_job
    with pytest.raises(KeyboardInterrupt):
        Coordinator(project.parent, FakeRunner(["success", KeyboardInterrupt()])).process_next()
    job = load_job(job_path)
    snapshot = project / job["stage_results"][0]["artifact_paths"][0]
    snapshot.write_text("corrupt", encoding="utf-8")
    runner = FakeRunner(["success", "success"])

    Coordinator(project.parent, runner).process_next()

    assert runner.calls == []
    failed = load_job(job_path)
    assert failed["state"] == "failed"
    assert failed["last_error"]["class"] == "integrity"


def test_media_collection_rejects_changed_source_bytes(
    project_with_job: tuple[Path, Path],
) -> None:
    project, _ = project_with_job
    result = success(project, "media_collection")
    source = project / "assets/source/images/pexels_1001.jpg"
    source.write_bytes(b"tampered after manifest")

    with pytest.raises(JobValidationError, match="source media hash mismatch"):
        Coordinator(project.parent, FakeRunner([]))._validate_success(
            project, "media_collection", result
        )


def test_review_is_bound_to_exact_collection_manifest(
    project_with_job: tuple[Path, Path],
) -> None:
    project, _ = project_with_job
    success(project, "media_collection")
    result = success(project, "media_relevance_review")
    review_path = project / "artifacts/media_relevance_review.json"
    review = json.loads(review_path.read_text(encoding="utf-8"))
    review["base_manifest_sha256"] = "0" * 64
    review_path.write_bytes(canonical_bytes(review))
    result = StageResult(
        **{**result.__dict__, "artifact_sha256": {
            **result.artifact_sha256,
            "artifacts/media_relevance_review.json": _sha256(review_path),
        }}
    )
    with pytest.raises(JobValidationError, match="base manifest hash"):
        Coordinator(project.parent, FakeRunner([]))._validate_success(
            project, "media_relevance_review", result
        )
