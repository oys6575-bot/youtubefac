"""Restricted, crash-recoverable Human Gate actions for the mobile dashboard.

This module deliberately exposes decisions, not arbitrary filesystem or shell
operations.  The canonical project remains the source of truth.  A prepared
journal contains exact target bytes so recovery can only finish the decision
that was already validated; it cannot invent a new one.
"""

from __future__ import annotations

import base64
import fcntl
import hashlib
import json
import os
import uuid
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterator, Mapping

import jsonschema

from backlot.auto_dispatch import build_topic_job
from lib.checkpoint import _enforce_stage_prerequisites, validate_checkpoint
from lib.pipeline_loader import load_pipeline_readonly
from schemas.artifacts import validate_artifact


ROOT = Path(__file__).resolve().parents[1]
ACTION_SCHEMA = ROOT / "schemas/mobile-dashboard/action.schema.json"
RECEIPT_SCHEMA = ROOT / "schemas/mobile-dashboard/approval-receipt.schema.json"
WRITE_ACTIONS = frozenset(
    {"approve_topic", "approve_gate", "reject_gate", "request_revision", "request_stop"}
)
TWO_STEP_GATES = frozenset(
    {"budget", "asset_selection", "final_review", "title_thumbnail", "publish"}
)


class ActionError(ValueError):
    code = "action_error"


class ActionValidationError(ActionError):
    code = "invalid_action"


class ActionConflict(ActionError):
    code = "action_conflict"


@dataclass(frozen=True)
class Actor:
    tailscale_login: str
    tailscale_user_id: str


@dataclass(frozen=True)
class ActionResult:
    receipt: dict[str, Any]
    replayed: bool = False


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ActionValidationError(f"unreadable_json:{path.name}") from exc
    if not isinstance(value, dict):
        raise ActionValidationError(f"invalid_json_object:{path.name}")
    return value


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_action_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ActionValidationError("payload must be an object")
    value = dict(payload)
    try:
        jsonschema.Draft202012Validator(_load_schema(ACTION_SCHEMA)).validate(value)
    except jsonschema.ValidationError as exc:
        field = ".".join(str(part) for part in exc.absolute_path) or "payload"
        raise ActionValidationError(
            f"payload validation failed at {field}: {exc.message}"
        ) from exc
    return value


def _safe_project(projects_root: Path, project_id: str) -> Path:
    root = projects_root.resolve()
    project = (root / project_id).resolve()
    try:
        project.relative_to(root)
    except ValueError as exc:
        raise ActionValidationError("invalid project_id") from exc
    if project.name != project_id or not project.is_dir():
        raise ActionValidationError("unknown project_id")
    return project


def checkpoint_sha256(project_dir: Path, stage: str) -> str:
    path = project_dir / f"checkpoint_{stage}.json"
    if not path.is_file():
        raise ActionValidationError("checkpoint_not_found")
    return _sha256(path.read_bytes())


def _manifest_stage(stage: str) -> dict[str, Any]:
    manifest = load_pipeline_readonly("youtube-factory")
    for item in manifest.get("stages", []):
        if item.get("name") == stage:
            return item
    raise ActionValidationError("unknown_stage")


def _verified_topic(project: Path, candidate_id: str) -> tuple[dict, dict]:
    shortlist_path = project / "artifacts/topic_shortlist.json"
    verification_path = project / "artifacts/topic_verification.json"
    shortlist = _load_json(shortlist_path)
    verification = _load_json(verification_path)
    try:
        validate_artifact("topic_shortlist", shortlist)
        validate_artifact("topic_verification", verification)
    except Exception as exc:
        raise ActionValidationError("topic_evidence_invalid") from exc
    if verification.get("verdict") != "PASS":
        raise ActionValidationError("verification_not_pass")
    if verification.get("input_sha256") != _sha256(shortlist_path.read_bytes()):
        raise ActionValidationError("verification_shortlist_hash_mismatch")
    candidates = {item.get("id") for item in shortlist.get("candidates", [])}
    candidate_results = {
        item.get("id"): item.get("verdict")
        for item in verification.get("candidate_results", [])
        if isinstance(item, dict)
    }
    if candidate_id not in candidates or candidate_results.get(candidate_id) != "PASS":
        raise ActionValidationError("candidate_not_verified")
    return shortlist, verification


def _checkpoint_for_approval(
    project: Path,
    payload: dict[str, Any],
    now: str,
) -> tuple[dict[str, Any], list[tuple[str, bytes]]]:
    stage = payload["stage"]
    checkpoint_path = project / f"checkpoint_{stage}.json"
    checkpoint = _load_json(checkpoint_path)
    if checkpoint.get("project_id") != payload["project_id"] or checkpoint.get("stage") != stage:
        raise ActionValidationError("checkpoint_identity_mismatch")
    if checkpoint.get("pipeline_type") != "youtube-factory":
        raise ActionValidationError("wrong_pipeline")
    if checkpoint.get("status") != "awaiting_human" or not checkpoint.get(
        "human_approval_required"
    ):
        raise ActionValidationError("gate_not_awaiting_human")
    stage_definition = _manifest_stage(stage)
    if not stage_definition.get("human_approval_default"):
        raise ActionValidationError("stage_is_not_human_gate")
    if stage in TWO_STEP_GATES and payload.get("confirmation") != "CONFIRM":
        raise ActionValidationError("two_step_confirmation_required")
    try:
        validate_checkpoint(checkpoint)
    except Exception as exc:
        raise ActionValidationError("current_checkpoint_invalid") from exc
    artifacts = checkpoint.get("artifacts") or {}
    missing_produced = [name for name in stage_definition.get("produces", []) if name not in artifacts]
    if missing_produced:
        raise ActionValidationError("gate_artifacts_missing")
    try:
        _enforce_stage_prerequisites(
            project.parent,
            payload["project_id"],
            "youtube-factory",
            stage,
            "completed",
        )
    except Exception as exc:
        raise ActionValidationError("gate_prerequisites_invalid") from exc

    targets: list[tuple[str, bytes]] = []
    result = deepcopy(checkpoint)
    result["status"] = "completed"
    result["human_approval_required"] = True
    result["human_approved"] = True
    result["timestamp"] = now

    if payload["action"] == "approve_topic":
        if stage != "topic_approval":
            raise ActionValidationError("approve_topic_requires_topic_approval")
        shortlist, verification = _verified_topic(project, payload["selected_candidate_id"])
        selection_path = project / "artifacts/topic_selection.json"
        existing_selection = _load_json(selection_path)
        selection = deepcopy(existing_selection)
        selection.update(
            {
                "selection_status": "APPROVED",
                "selected_candidate_id": payload["selected_candidate_id"],
                "human_approved": True,
            }
        )
        if selection.get("shortlist_sha256") != _sha256(
            (project / "artifacts/topic_shortlist.json").read_bytes()
        ) or selection.get("verification_sha256") != _sha256(
            (project / "artifacts/topic_verification.json").read_bytes()
        ):
            raise ActionValidationError("topic_selection_hash_mismatch")
        try:
            validate_artifact("topic_selection", selection)
        except Exception as exc:
            raise ActionValidationError("topic_selection_invalid") from exc
        result.setdefault("artifacts", {})["topic_selection"] = selection
        targets.append(("artifacts/topic_selection.json", _json_bytes(selection)))
    elif payload["action"] != "approve_gate":
        raise ActionValidationError("action_does_not_approve_gate")

    try:
        validate_checkpoint(result)
    except Exception as exc:
        raise ActionValidationError("resulting_checkpoint_invalid") from exc
    targets.append((f"checkpoint_{stage}.json", _json_bytes(result)))
    return result, targets


def _request_target(payload: dict[str, Any], actor: Actor, receipt_id: str, now: str) -> tuple[str, bytes]:
    action = payload["action"]
    request = {
        "version": "1.0",
        "request_id": receipt_id,
        "project_id": payload["project_id"],
        "action": action,
        "stage": payload["stage"],
        "state": "requested",
        "reason": payload["reason"],
        "actor": {
            "tailscale_login": actor.tailscale_login,
            "tailscale_user_id": actor.tailscale_user_id,
        },
        "created_at": now,
    }
    directory = "stop_requests" if action == "request_stop" else "review_requests"
    return f"approvals/{directory}/{receipt_id}.json", _json_bytes(request)


def _validate_rejection(project: Path, payload: dict[str, Any]) -> None:
    checkpoint = _load_json(project / f"checkpoint_{payload['stage']}.json")
    if (
        checkpoint.get("project_id") != payload["project_id"]
        or checkpoint.get("stage") != payload["stage"]
        or checkpoint.get("status") != "awaiting_human"
        or not checkpoint.get("human_approval_required")
    ):
        raise ActionValidationError("gate_not_awaiting_human")
    stage_definition = _manifest_stage(payload["stage"])
    if not stage_definition.get("human_approval_default"):
        raise ActionValidationError("stage_is_not_human_gate")
    try:
        validate_checkpoint(checkpoint)
    except Exception as exc:
        raise ActionValidationError("current_checkpoint_invalid") from exc


def _safe_rel(project: Path, rel: str) -> Path:
    pure = PurePosixPath(rel)
    if pure.is_absolute() or ".." in pure.parts:
        raise ActionValidationError("unsafe_transaction_path")
    target = (project / Path(*pure.parts)).resolve()
    try:
        target.relative_to(project.resolve())
    except ValueError as exc:
        raise ActionValidationError("unsafe_transaction_path") from exc
    return target


def _fsync_directory(path: Path) -> None:
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with open(tmp, "xb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        _fsync_directory(path.parent)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


@contextmanager
def _project_lock(projects_root: Path, project: Path) -> Iterator[None]:
    # Keep the lock outside the canonical project.  A rejected stale request
    # must leave the project byte-for-byte unchanged, including no lock stub.
    lock_path = projects_root / ".mobile-dashboard-locks" / f"{project.name}.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _journal_target(rel: str, content: bytes) -> dict[str, str]:
    return {
        "path": rel,
        "sha256": _sha256(content),
        "content_base64": base64.b64encode(content).decode("ascii"),
    }


def _apply_journal(project: Path, journal: dict[str, Any], failpoint: str | None = None) -> None:
    for index, item in enumerate(journal["targets"]):
        content = base64.b64decode(item["content_base64"], validate=True)
        if _sha256(content) != item["sha256"]:
            raise ActionValidationError("journal_content_hash_mismatch")
        target = _safe_rel(project, item["path"])
        if not target.is_file() or _sha256(target.read_bytes()) != item["sha256"]:
            _atomic_write(target, content)
        if failpoint == f"after_target_{index}":
            raise RuntimeError(f"injected failure after target {index}")


def recover_transactions(project: Path) -> int:
    journal_dir = project / "approvals/transactions"
    if not journal_dir.is_dir():
        return 0
    recovered = 0
    for path in sorted(journal_dir.glob("*.json")):
        journal = _load_json(path)
        if journal.get("state") != "prepared":
            continue
        _apply_journal(project, journal)
        journal["state"] = "completed"
        _atomic_write(path, _json_bytes(journal))
        recovered += 1
    return recovered


def _existing_receipt(project: Path, idempotency_key: str) -> dict[str, Any] | None:
    key_hash = _sha256(idempotency_key.encode("utf-8"))
    index_path = project / f"approvals/idempotency/{key_hash}.json"
    if not index_path.is_file():
        return None
    index = _load_json(index_path)
    receipt_path = _safe_rel(project, index.get("receipt_path", ""))
    receipt = _load_json(receipt_path)
    if receipt.get("idempotency_key") != idempotency_key:
        raise ActionConflict("idempotency_key_collision")
    return receipt


def execute_action(
    projects_root: Path,
    raw_payload: Mapping[str, Any],
    actor: Actor,
    *,
    now: str | None = None,
    failpoint: str | None = None,
) -> ActionResult:
    payload = validate_action_payload(raw_payload)
    if not actor.tailscale_login or not actor.tailscale_user_id:
        raise ActionValidationError("actor_identity_required")
    project = _safe_project(Path(projects_root), payload["project_id"])
    timestamp = now or datetime.now(timezone.utc).isoformat()

    with _project_lock(Path(projects_root), project):
        recover_transactions(project)
        replay = _existing_receipt(project, payload["idempotency_key"])
        if replay is not None:
            return ActionResult(replay, replayed=True)

        current_hash = checkpoint_sha256(project, payload["stage"])
        if current_hash != payload["expected_checkpoint_sha256"]:
            raise ActionConflict("stale_checkpoint")

        receipt_id = str(uuid.uuid4())
        targets: list[tuple[str, bytes]] = []
        approved_checkpoint: dict[str, Any] | None = None
        if payload["action"] in {"approve_topic", "approve_gate"}:
            approved_checkpoint, approval_targets = _checkpoint_for_approval(
                project, payload, timestamp
            )
            old_checkpoint = (project / f"checkpoint_{payload['stage']}.json").read_bytes()
            history_name = f"history/checkpoint_{payload['stage']}_{_sha256(old_checkpoint)[:16]}.json"
            targets.append((history_name, old_checkpoint))
            targets.extend(approval_targets)
            resulting_hash = _sha256(approval_targets[-1][1])
        else:
            if payload["action"] == "reject_gate":
                _validate_rejection(project, payload)
            targets.append(_request_target(payload, actor, receipt_id, timestamp))
            resulting_hash = current_hash

        receipt: dict[str, Any] = {
            "version": "1.0",
            "receipt_id": receipt_id,
            "project_id": payload["project_id"],
            "action": payload["action"],
            "stage": payload["stage"],
            "expected_checkpoint_sha256": payload["expected_checkpoint_sha256"],
            "resulting_checkpoint_sha256": resulting_hash,
            "actor": {
                "tailscale_login": actor.tailscale_login,
                "tailscale_user_id": actor.tailscale_user_id,
            },
            "idempotency_key": payload["idempotency_key"],
            "created_at": timestamp,
        }
        if payload.get("selected_candidate_id"):
            receipt["selected_candidate_id"] = payload["selected_candidate_id"]
        if payload.get("reason"):
            receipt["reason"] = payload["reason"]
        try:
            jsonschema.Draft202012Validator(_load_schema(RECEIPT_SCHEMA)).validate(receipt)
        except jsonschema.ValidationError as exc:
            raise ActionValidationError("receipt_invalid") from exc

        receipt_rel = f"approvals/receipts/{receipt_id}.json"
        targets.append((receipt_rel, _json_bytes(receipt)))
        if payload["action"] == "approve_topic":
            assert approved_checkpoint is not None
            job = build_topic_job(
                project,
                receipt,
                resulting_hash,
                timestamp,
                topic_selection=approved_checkpoint["artifacts"]["topic_selection"],
            )
            targets.append(
                (f"automation/jobs/{receipt_id}.json", _json_bytes(job))
            )
        key_hash = _sha256(payload["idempotency_key"].encode("utf-8"))
        targets.append(
            (
                f"approvals/idempotency/{key_hash}.json",
                _json_bytes({"version": "1.0", "receipt_path": receipt_rel}),
            )
        )

        journal = {
            "version": "1.0",
            "transaction_id": receipt_id,
            "state": "prepared",
            "project_id": payload["project_id"],
            "created_at": timestamp,
            "targets": [_journal_target(rel, content) for rel, content in targets],
        }
        journal_path = project / f"approvals/transactions/{receipt_id}.json"
        _atomic_write(journal_path, _json_bytes(journal))
        if failpoint == "after_prepared":
            raise RuntimeError("injected failure after prepared journal")
        _apply_journal(project, journal, failpoint=failpoint)
        journal["state"] = "completed"
        _atomic_write(journal_path, _json_bytes(journal))
        return ActionResult(receipt)
