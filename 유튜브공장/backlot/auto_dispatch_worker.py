"""Crash-recoverable single-project Coordinator for automatic topic work."""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import shutil
import socket
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterator, Protocol

import jsonschema

from backlot.auto_dispatch import JobValidationError, load_job, write_job_state
from backlot.orca_auto_dispatch import StageResult
from lib.checkpoint import validate_checkpoint
from schemas.artifacts import validate_artifact


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_SCHEMA = ROOT / "schemas/mobile-dashboard/approval-receipt.schema.json"
COLLECTION_PROGRESS_SCHEMA = (
    ROOT / "schemas/mobile-dashboard/media-collection-progress.schema.json"
)
STAGES = ["research", "media_collection", "evidence_lock", "proposal"]
STAGE_FILES = {
    "research": {
        "artifacts/research_brief.json": "research_brief",
        "artifacts/evidence_registry.json": "evidence_registry",
        "checkpoint_research.json": None,
    },
    "media_collection": {
        "artifacts/media_collection_manifest.json": "media_collection_manifest",
        "automation/progress/media_collection.json": None,
        "checkpoint_media_collection.json": None,
    },
    "evidence_lock": {
        "artifacts/evidence_registry.json": "evidence_registry",
        "artifacts/decision_log.json": "decision_log",
        "checkpoint_evidence_lock.json": None,
    },
    "proposal": {
        "artifacts/proposal_packet.json": "proposal_packet",
        "artifacts/decision_log.json": "decision_log",
        "checkpoint_proposal.json": None,
    },
}


class StageRunner(Protocol):
    def run_stage(
        self, project: Path, job: dict[str, Any], stage: str
    ) -> StageResult: ...


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise JobValidationError(f"unreadable JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise JobValidationError(f"JSON object required: {path.name}")
    return value


def _safe_path(project: Path, relative: str) -> Path:
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise JobValidationError("unsafe artifact path")
    target = (project / Path(*pure.parts)).resolve()
    try:
        target.relative_to(project.resolve())
    except ValueError as exc:
        raise JobValidationError("unsafe artifact path") from exc
    return target


@contextmanager
def _project_lock(projects_root: Path, project_id: str) -> Iterator[None]:
    path = projects_root / ".auto-dispatch-locks" / f"{project_id}.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class Coordinator:
    def __init__(self, projects_root: Path, runner: StageRunner) -> None:
        self.projects_root = projects_root.resolve()
        self.runner = runner
        self.worker_id = str(uuid.uuid4())

    def _candidate_jobs(self) -> list[Path]:
        return sorted(self.projects_root.glob("*/automation/jobs/*.json"))

    @staticmethod
    def _lease_is_live(job: dict[str, Any]) -> bool:
        lease = job.get("lease")
        if not isinstance(lease, dict):
            return False
        if lease.get("host") != socket.gethostname():
            return True
        pid = int(lease.get("pid") or 0)
        if pid == os.getpid():
            return False
        try:
            os.kill(pid, 0)
        except (OSError, ValueError):
            return False
        return True

    def _claim(self, path: Path, job: dict[str, Any]) -> dict[str, Any] | None:
        if job["state"] not in {"queued", "running", "retrying"}:
            return None
        if job["state"] in {"running", "retrying"} and self._lease_is_live(job):
            return None
        timestamp = _now()
        return write_job_state(
            path,
            job["state"],
            {
                "state": "running" if job["state"] != "retrying" else "retrying",
                "updated_at": timestamp,
                "lease": {
                    "worker_id": self.worker_id,
                    "host": socket.gethostname(),
                    "pid": os.getpid(),
                    "claimed_at": timestamp,
                    "heartbeat_at": timestamp,
                },
            },
        )

    def _validate_trigger(self, project: Path, job: dict[str, Any]) -> None:
        receipt_path = _safe_path(project, job["trigger_receipt_path"])
        receipt = _json(receipt_path)
        schema = json.loads(RECEIPT_SCHEMA.read_text(encoding="utf-8"))
        try:
            jsonschema.Draft202012Validator(
                schema, format_checker=jsonschema.FormatChecker()
            ).validate(receipt)
        except jsonschema.ValidationError as exc:
            raise JobValidationError("trigger receipt is invalid") from exc
        receipt_matches = (
            receipt.get("receipt_id") == job["job_id"]
            and receipt.get("project_id") == job["project_id"]
            and receipt.get("selected_candidate_id") == job["selected_candidate_id"]
            and receipt.get("resulting_checkpoint_sha256")
            == job["trigger_checkpoint_sha256"]
            and receipt.get("action") == job["trigger_action"]
        )
        if job["trigger_action"] == "approve_topic":
            receipt_matches = receipt_matches and receipt.get("stage") == "topic_approval"
        else:
            receipt_matches = (
                receipt_matches
                and receipt.get("retry_job_id") == job.get("retry_of")
                and isinstance(job.get("retry_of"), str)
            )
            original_path = project / f"automation/jobs/{job.get('retry_of')}.json"
            original = load_job(original_path)
            receipt_matches = (
                receipt_matches
                and original["project_id"] == job["project_id"]
                and original["selected_candidate_id"] == job["selected_candidate_id"]
                and original["trigger_checkpoint_sha256"]
                == job["trigger_checkpoint_sha256"]
                and original["stage_results"] == job["stage_results"]
            )
        if not receipt_matches:
            raise JobValidationError("trigger receipt does not match job")
        checkpoint_path = project / "checkpoint_topic_approval.json"
        if _sha256(checkpoint_path) != job["trigger_checkpoint_sha256"]:
            raise JobValidationError("topic approval checkpoint hash changed")
        checkpoint = _json(checkpoint_path)
        validate_checkpoint(checkpoint)
        if (
            checkpoint.get("status") != "completed"
            or checkpoint.get("human_approved") is not True
        ):
            raise JobValidationError("topic approval is not completed")
        selection_path = project / "artifacts/topic_selection.json"
        selection = _json(selection_path)
        validate_artifact("topic_selection", selection)
        if (
            selection.get("selection_status") != "APPROVED"
            or selection.get("human_approved") is not True
            or selection.get("selected_candidate_id") != job["selected_candidate_id"]
            or checkpoint.get("artifacts", {}).get("topic_selection") != selection
        ):
            raise JobValidationError("canonical topic selection does not match job")

    def _validate_settled_results(self, project: Path, job: dict[str, Any]) -> None:
        results = job["stage_results"]
        if [item["stage"] for item in results] != STAGES[: len(results)]:
            raise JobValidationError("settled stage order drift")
        for result in results:
            if set(result["artifact_paths"]) != set(result["artifact_sha256"]):
                raise JobValidationError("settled artifact binding mismatch")
            for relative in result["artifact_paths"]:
                path = _safe_path(project, relative)
                if not path.is_file() or _sha256(path) != result["artifact_sha256"][relative]:
                    raise JobValidationError("settled artifact hash mismatch")
            if result["stage"] == "media_collection":
                manifest_path = next(
                    (
                        _safe_path(project, relative)
                        for relative in result["artifact_paths"]
                        if relative.endswith("/artifacts/media_collection_manifest.json")
                    ),
                    None,
                )
                if manifest_path is None:
                    raise JobValidationError("settled media manifest is missing")
                self._validate_media_collection_assets(project, _json(manifest_path))

    @staticmethod
    def _validate_media_collection_assets(
        project: Path, manifest: dict[str, Any]
    ) -> None:
        source_root = (project / "assets/source").resolve()
        seen: set[str] = set()
        for item in manifest.get("items", []):
            relative = item.get("local_path")
            if not isinstance(relative, str) or relative in seen:
                raise JobValidationError("source media path is invalid or duplicated")
            seen.add(relative)
            path = _safe_path(project, relative)
            try:
                path.relative_to(source_root)
            except ValueError as exc:
                raise JobValidationError("source media escaped assets/source") from exc
            if not path.is_file():
                raise JobValidationError("source media file is missing")
            if _sha256(path) != item.get("sha256"):
                raise JobValidationError("source media hash mismatch")
            technical = item.get("technical")
            if not isinstance(technical, dict) or technical.get("size_bytes") != path.stat().st_size:
                raise JobValidationError("source media size mismatch")

    def _validate_success(
        self, project: Path, stage: str, result: StageResult
    ) -> None:
        required = STAGE_FILES[stage]
        if result.outcome != "success":
            raise JobValidationError("stage did not succeed")
        if set(result.artifact_paths) != set(required):
            raise JobValidationError("stage returned unexpected artifact paths")
        if set(result.artifact_sha256) != set(required):
            raise JobValidationError("stage artifact hashes are incomplete")
        if len(result.source_commit) != 40 or any(
            char not in "0123456789abcdef" for char in result.source_commit
        ):
            raise JobValidationError("stage source commit is invalid")
        if stage == "evidence_lock" and result.verdict != "PASS":
            raise JobValidationError("independent evidence verdict is not PASS")
        if stage != "evidence_lock" and result.verdict != "NOT_APPLICABLE":
            raise JobValidationError("unexpected stage verdict")
        loaded_artifacts: dict[str, dict[str, Any]] = {}
        for relative, artifact_name in required.items():
            path = _safe_path(project, relative)
            if not path.is_file() or _sha256(path) != result.artifact_sha256[relative]:
                raise JobValidationError("returned artifact hash mismatch")
            if artifact_name:
                value = _json(path)
                validate_artifact(artifact_name, value)
                loaded_artifacts[artifact_name] = value
            elif relative == "automation/progress/media_collection.json":
                progress = _json(path)
                schema = json.loads(
                    COLLECTION_PROGRESS_SCHEMA.read_text(encoding="utf-8")
                )
                try:
                    jsonschema.Draft202012Validator(
                        schema, format_checker=jsonschema.FormatChecker()
                    ).validate(progress)
                except jsonschema.ValidationError as exc:
                    raise JobValidationError(
                        "media collection progress is invalid"
                    ) from exc
        if stage == "media_collection":
            self._validate_media_collection_assets(
                project, loaded_artifacts["media_collection_manifest"]
            )
        checkpoint = _json(project / f"checkpoint_{stage}.json")
        validate_checkpoint(checkpoint)
        expected_status = "awaiting_human" if stage == "proposal" else "completed"
        if checkpoint.get("stage") != stage or checkpoint.get("status") != expected_status:
            raise JobValidationError("stage checkpoint status mismatch")
        if checkpoint.get("human_approved") is not False:
            raise JobValidationError("automatic stage fabricated human approval")
        if stage == "proposal":
            if checkpoint.get("human_approval_required") is not True:
                raise JobValidationError("proposal checkpoint must wait for the user")
        elif checkpoint.get("human_approval_required") is not False:
            raise JobValidationError("machine stage unexpectedly requires Human Gate")
        for name, value in loaded_artifacts.items():
            if checkpoint.get("artifacts", {}).get(name) != value:
                raise JobValidationError("checkpoint artifact bytes are not canonical")

    def _snapshot_success(
        self,
        project: Path,
        job: dict[str, Any],
        stage: str,
        result: StageResult,
    ) -> dict[str, Any]:
        destination_root = project / "automation/artifacts" / job["job_id"] / stage
        paths: list[str] = []
        hashes: dict[str, str] = {}
        for relative in result.artifact_paths:
            source = _safe_path(project, relative)
            destination = destination_root / Path(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_name(f".{destination.name}.{uuid.uuid4().hex}.tmp")
            shutil.copyfile(source, temporary)
            os.replace(temporary, destination)
            snapshot_relative = destination.relative_to(project).as_posix()
            paths.append(snapshot_relative)
            hashes[snapshot_relative] = _sha256(destination)
        return {
            "stage": stage,
            "outcome": "success",
            "artifact_paths": paths,
            "artifact_sha256": hashes,
            "source_commit": result.source_commit,
            "verdict": result.verdict,
            "run_id": result.run_id,
            "task_id": result.task_id,
            "dispatch_id": result.dispatch_id,
            "settled_at": _now(),
        }

    @staticmethod
    def _error(stage: str, error_class: str, message: str) -> dict[str, str]:
        return {
            "stage": stage,
            "class": error_class,
            "message": message[:2000] or "unknown failure",
            "timestamp": _now(),
        }

    def _fail(
        self,
        path: Path,
        job: dict[str, Any],
        stage: str,
        error_class: str,
        message: str,
    ) -> dict[str, Any]:
        return write_job_state(
            path,
            job["state"],
            {
                "state": "failed",
                "updated_at": _now(),
                "last_error": self._error(stage, error_class, message),
                "lease": None,
            },
        )

    def _run_claimed(self, path: Path, project: Path, job: dict[str, Any]) -> None:
        try:
            self._validate_trigger(project, job)
            self._validate_settled_results(project, job)
        except Exception as exc:
            self._fail(path, job, job["current_stage"], "integrity", str(exc))
            return
        while len(job["stage_results"]) < len(STAGES):
            stage = STAGES[len(job["stage_results"])]
            if job["current_stage"] != stage:
                self._fail(path, job, stage, "integrity", "current stage drift")
                return
            result = self.runner.run_stage(project, job, stage)
            updates: dict[str, Any] = {}
            if result.run_id and not job.get("run_id"):
                updates["run_id"] = result.run_id
            if updates:
                updates["updated_at"] = _now()
                job = write_job_state(path, job["state"], updates)
            if result.outcome != "success":
                error_class = result.error_class or "ordinary"
                error = result.error or "stage failed"
                if error_class == "ordinary" and job["attempt"] < job["max_retries"]:
                    job = write_job_state(
                        path,
                        job["state"],
                        {
                            "state": "retrying",
                            "attempt": job["attempt"] + 1,
                            "updated_at": _now(),
                            "last_error": self._error(stage, error_class, error),
                        },
                    )
                    continue
                self._fail(path, job, stage, error_class, error)
                return
            try:
                self._validate_success(project, stage, result)
                settled = self._snapshot_success(project, job, stage, result)
            except Exception as exc:
                self._fail(path, job, stage, "integrity", str(exc))
                return
            results = [*job["stage_results"], settled]
            if stage == "proposal":
                write_job_state(
                    path,
                    job["state"],
                    {
                        "state": "awaiting_human",
                        "current_stage": "proposal",
                        "attempt": 0,
                        "updated_at": _now(),
                        "stage_results": results,
                        "last_error": None,
                        "lease": None,
                    },
                )
                return
            job = write_job_state(
                path,
                job["state"],
                {
                    "state": "running",
                    "current_stage": STAGES[len(results)],
                    "attempt": 0,
                    "updated_at": _now(),
                    "stage_results": results,
                    "last_error": None,
                },
            )

    def process_next(self) -> bool:
        for path in self._candidate_jobs():
            try:
                job = load_job(path)
            except JobValidationError:
                continue
            project = path.parents[2]
            with _project_lock(self.projects_root, project.name):
                job = load_job(path)
                claimed = self._claim(path, job)
                if claimed is None:
                    continue
                self._run_claimed(path, project, claimed)
                return True
        return False
