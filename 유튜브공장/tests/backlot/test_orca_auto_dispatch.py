from __future__ import annotations

import json
from pathlib import Path

import pytest

from backlot.orca_auto_dispatch import OrcaAdapterError, OrcaRunner, StageResult


def test_message_payload_decodes_orca_json_string() -> None:
    message = {
        "payload": json.dumps(
            {
                "taskId": "task_current",
                "dispatchId": "ctx_current",
                "outcome": "succeeded",
            }
        )
    }

    assert OrcaRunner._message_payload(message) == {
        "taskId": "task_current",
        "dispatchId": "ctx_current",
        "outcome": "succeeded",
    }


def test_wait_skips_and_acknowledges_stale_worker_done() -> None:
    runner = OrcaRunner.__new__(OrcaRunner)
    runner.stage_timeout = 5
    calls: list[list[str]] = []
    deliveries = iter(
        [
            {
                "result": {
                    "deliveryId": "delivery_old",
                    "messages": [
                        {
                            "type": "worker_done",
                            "body": "old attempt",
                            "payload": json.dumps(
                                {"taskId": "task_old", "dispatchId": "ctx_old"}
                            ),
                        }
                    ],
                }
            },
            {
                "result": {
                    "deliveryId": "delivery_current",
                    "messages": [
                        {
                            "type": "worker_done",
                            "body": "current attempt",
                            "payload": json.dumps(
                                {
                                    "taskId": "task_current",
                                    "dispatchId": "ctx_current",
                                    "outcome": "succeeded",
                                }
                            ),
                        }
                    ],
                }
            },
        ]
    )

    def fake_run_json(args, *, timeout=None):
        del timeout
        calls.append(list(args))
        return next(deliveries)

    runner._run_json = fake_run_json

    assert runner._wait_for_worker(
        "run_current", "term_sender", "task_current", "ctx_current"
    ) == ("succeeded", "current attempt")
    assert ["--ack", "delivery_old"] == calls[1][3:5]

def test_stage_result_file_cannot_self_assert_orca_provenance(tmp_path: Path) -> None:
    path = tmp_path / "result.json"
    path.write_text(
        json.dumps(
            {
                "outcome": "success",
                "artifact_paths": [],
                "artifact_sha256": {},
                "source_commit": "a" * 40,
                "verdict": "NOT_APPLICABLE",
                "run_id": "invented",
                "task_id": "invented",
                "dispatch_id": "invented",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(OrcaAdapterError, match="contract violation"):
        OrcaRunner._load_result(path)


def test_stage_result_rejects_artifact_path_mapping(tmp_path: Path) -> None:
    path = tmp_path / "result.json"
    path.write_text(
        json.dumps(
            {
                "outcome": "success",
                "artifact_paths": {"artifacts/research_brief.json": "wrong"},
                "artifact_sha256": {"artifacts/research_brief.json": "b" * 64},
                "source_commit": "a" * 40,
                "verdict": "NOT_APPLICABLE",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(OrcaAdapterError, match="contract violation"):
        OrcaRunner._load_result(path)


def test_research_prompt_spells_out_canonical_checkpoint_contract(tmp_path: Path) -> None:
    runner = OrcaRunner.__new__(OrcaRunner)
    runner.factory_root = tmp_path
    runner.routing = {
        "roles": {
            "research": {
                "runtime": "hermes",
                "model": "local",
                "effort": "high",
                "profile": "ytf-research",
            }
        }
    }
    project = tmp_path / "projects/P1"

    prompt = runner._task_prompt(
        project,
        {"job_id": "job-1", "selected_candidate_id": "rana-plaza"},
        "research",
        project / "automation/stage-results/job-1/research-attempt-0.json",
    )

    assert "checkpoint_research.json" in prompt
    assert "lib.checkpoint.validate_checkpoint" in prompt
    assert "embed the exact full JSON object" in prompt
    assert "verdict='NOT_APPLICABLE'" in prompt


def test_collection_prompt_uses_production_role_and_forbids_gemini(tmp_path: Path) -> None:
    runner = OrcaRunner.__new__(OrcaRunner)
    runner.factory_root = tmp_path
    runner.routing = {
        "roles": {
            "production": {
                "runtime": "hermes",
                "model": "local",
                "effort": None,
                "profile": "ytf-production",
            }
        }
    }
    project = tmp_path / "projects/P1"

    prompt = runner._task_prompt(
        project,
        {"job_id": "job-1", "selected_candidate_id": "rana-plaza"},
        "media_collection",
        project / "automation/stage-results/job-1/media-collection-attempt-0.json",
    )

    assert "media-collection-director.md" in prompt
    assert "artifacts/media_collection_manifest.json" in prompt
    assert "checkpoint_media_collection.json" in prompt
    assert "assets/source/**" in prompt
    assert "no Gemini" in prompt


def test_transport_provenance_is_bound_by_coordinator(tmp_path: Path) -> None:
    path = tmp_path / "result.json"
    path.write_text(
        json.dumps(
            {
                "outcome": "success",
                "artifact_paths": ["artifacts/research_brief.json"],
                "artifact_sha256": {"artifacts/research_brief.json": "b" * 64},
                "source_commit": "a" * 40,
                "verdict": "NOT_APPLICABLE",
            }
        ),
        encoding="utf-8",
    )

    result = OrcaRunner._bind_provenance(
        OrcaRunner._load_result(path),
        run_id="run_actual",
        task_id="task_actual",
        dispatch_id="ctx_actual",
    )

    assert result == StageResult(
        outcome="success",
        artifact_paths=["artifacts/research_brief.json"],
        artifact_sha256={"artifacts/research_brief.json": "b" * 64},
        source_commit="a" * 40,
        verdict="NOT_APPLICABLE",
        run_id="run_actual",
        task_id="task_actual",
        dispatch_id="ctx_actual",
    )
