"""Strict durable job contract for post-approval automatic work."""

from __future__ import annotations

import json
import os
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
JOB_SCHEMA = ROOT / "schemas/mobile-dashboard/auto-dispatch-job.schema.json"
AUTO_STAGES = ["research", "media_collection", "evidence_lock", "proposal"]
LEGACY_AUTO_STAGES = ["research", "evidence_lock", "proposal"]
MUTABLE_FIELDS = frozenset(
    {
        "state",
        "current_stage",
        "attempt",
        "updated_at",
        "stage_results",
        "last_error",
        "run_id",
        "lease",
    }
)


class JobValidationError(ValueError):
    """Raised when an automatic job violates the fixed safety contract."""


class JobConflict(JobValidationError):
    """Raised when a state transition races with another worker."""


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _schema() -> dict[str, Any]:
    return json.loads(JOB_SCHEMA.read_text(encoding="utf-8"))


def validate_job(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise JobValidationError("job must be an object")
    payload = deepcopy(dict(value))
    try:
        jsonschema.Draft202012Validator(
            _schema(), format_checker=jsonschema.FormatChecker()
        ).validate(payload)
    except jsonschema.ValidationError as exc:
        field = ".".join(str(part) for part in exc.absolute_path) or "job"
        raise JobValidationError(f"job validation failed at {field}: {exc.message}") from exc
    if payload["trigger_receipt_path"] != (
        f"approvals/receipts/{payload['job_id']}.json"
    ):
        raise JobValidationError("trigger receipt must match job_id")
    stages = payload["stages"]
    result_stages = [item["stage"] for item in payload["stage_results"]]
    if result_stages != stages[: len(result_stages)]:
        raise JobValidationError("settled stage order drift")
    if stages == LEGACY_AUTO_STAGES and payload["state"] not in {
        "failed",
        "awaiting_human",
        "completed",
    }:
        raise JobValidationError(
            "legacy automatic job is historical and cannot be reactivated"
        )
    return payload


def build_topic_job(
    project: Path,
    receipt: Mapping[str, Any],
    resulting_checkpoint_sha256: str,
    now: str,
    *,
    topic_selection: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive a queued job only from the validated approval and topic state."""

    if receipt.get("action") != "approve_topic" or receipt.get("stage") != "topic_approval":
        raise JobValidationError("job trigger must be an approve_topic receipt")
    if receipt.get("resulting_checkpoint_sha256") != resulting_checkpoint_sha256:
        raise JobValidationError("trigger checkpoint hash mismatch")
    selection = dict(topic_selection) if topic_selection is not None else json.loads(
        (project / "artifacts/topic_selection.json").read_text(encoding="utf-8")
    )
    selected_candidate_id = receipt.get("selected_candidate_id")
    if (
        selection.get("selection_status") != "APPROVED"
        or selection.get("human_approved") is not True
        or selection.get("selected_candidate_id") != selected_candidate_id
    ):
        raise JobValidationError("approved topic selection does not match receipt")
    job = {
        "version": "1.0",
        "job_id": receipt["receipt_id"],
        "project_id": receipt["project_id"],
        "trigger_receipt_path": f"approvals/receipts/{receipt['receipt_id']}.json",
        "trigger_checkpoint_sha256": resulting_checkpoint_sha256,
        "trigger_action": "approve_topic",
        "selected_candidate_id": selected_candidate_id,
        "state": "queued",
        "current_stage": "research",
        "stages": AUTO_STAGES,
        "attempt": 0,
        "max_retries": 1,
        "created_at": now,
        "updated_at": now,
        "stage_results": [],
        "last_error": None,
    }
    return validate_job(job)


def build_retry_job(
    original: Mapping[str, Any],
    receipt: Mapping[str, Any],
    now: str,
) -> dict[str, Any]:
    """Create a new immutable retry chain entry without rewriting history."""

    source = validate_job(original)
    if source["state"] != "failed":
        raise JobValidationError("only failed jobs can be retried")
    if receipt.get("action") != "retry_auto_dispatch":
        raise JobValidationError("retry job requires a retry receipt")
    if receipt.get("retry_job_id") != source["job_id"]:
        raise JobValidationError("retry receipt does not match original job")
    settled = deepcopy(source["stage_results"])
    if [item["stage"] for item in settled] != AUTO_STAGES[: len(settled)]:
        raise JobValidationError(
            "legacy retry can migrate only a settled prefix through research"
        )
    if len(settled) >= len(AUTO_STAGES):
        raise JobValidationError("completed automatic workflow cannot be retried")
    job = {
        "version": "1.0",
        "job_id": receipt["receipt_id"],
        "project_id": source["project_id"],
        "trigger_receipt_path": f"approvals/receipts/{receipt['receipt_id']}.json",
        "trigger_checkpoint_sha256": source["trigger_checkpoint_sha256"],
        "trigger_action": "retry_auto_dispatch",
        "selected_candidate_id": source["selected_candidate_id"],
        "state": "queued",
        "current_stage": AUTO_STAGES[len(settled)],
        "stages": AUTO_STAGES,
        "attempt": 0,
        "max_retries": 1,
        "created_at": now,
        "updated_at": now,
        "stage_results": settled,
        "last_error": None,
        "retry_of": source["job_id"],
    }
    return validate_job(job)


def load_job(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise JobValidationError(f"unreadable job: {path}") from exc
    return validate_job(value)


def _atomic_write(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with open(temporary, "xb") as handle:
            handle.write(_json_bytes(value))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def write_job_state(
    path: Path,
    expected_state: str,
    updates: Mapping[str, Any],
) -> dict[str, Any]:
    unknown = set(updates) - MUTABLE_FIELDS
    if unknown:
        raise JobValidationError(f"immutable job fields: {sorted(unknown)}")
    current = load_job(path)
    if current["state"] != expected_state:
        raise JobConflict(
            f"job state changed: expected {expected_state}, found {current['state']}"
        )
    result = deepcopy(current)
    result.update(deepcopy(dict(updates)))
    result = validate_job(result)
    _atomic_write(path, result)
    return result
