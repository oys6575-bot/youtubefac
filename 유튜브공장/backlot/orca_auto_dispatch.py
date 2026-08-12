"""Typed Orca adapter for the bounded post-topic-approval workflow."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from lib.orca_model_routing import load_routing


@dataclass(frozen=True)
class StageResult:
    outcome: str
    artifact_paths: list[str] = field(default_factory=list)
    artifact_sha256: dict[str, str] = field(default_factory=dict)
    source_commit: str = ""
    verdict: str = "NOT_APPLICABLE"
    run_id: str = ""
    task_id: str = ""
    dispatch_id: str = ""
    error_class: str | None = None
    error: str | None = None

    @classmethod
    def failure(
        cls,
        stage: str,
        error_class: str,
        message: str,
        *,
        run_id: str = "",
        task_id: str = "",
        dispatch_id: str = "",
    ) -> "StageResult":
        del stage
        return cls(
            outcome="failure",
            run_id=run_id,
            task_id=task_id,
            dispatch_id=dispatch_id,
            error_class=error_class,
            error=message,
        )


class OrcaAdapterError(RuntimeError):
    """Typed command or orchestration failure."""


class OrcaRunner:
    """Create one Orca Run and sequential supervised stage workers."""

    def __init__(
        self,
        factory_root: Path,
        routing_path: Path,
        *,
        command_timeout: int = 60,
        stage_timeout: int = 3600,
    ) -> None:
        self.factory_root = factory_root.resolve()
        self.repo_root = self.factory_root.parent.resolve()
        self.routing = load_routing(routing_path)
        self.command_timeout = command_timeout
        self.stage_timeout = stage_timeout
        self.orca_cli = os.environ.get("ORCA_CLI", "orca")
        self._senders: dict[str, str] = {}
        self._runs: dict[str, str] = {}

    def _run_json(self, args: Sequence[str], *, timeout: int | None = None) -> dict[str, Any]:
        completed = subprocess.run(
            list(args),
            cwd=self.factory_root,
            text=True,
            capture_output=True,
            timeout=timeout or self.command_timeout,
            check=False,
        )
        if completed.returncode != 0:
            raise OrcaAdapterError(
                f"command failed ({completed.returncode}): {' '.join(args[:3])}: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise OrcaAdapterError("Orca returned non-JSON output") from exc
        if not payload.get("ok"):
            error = payload.get("error") or {}
            raise OrcaAdapterError(str(error.get("message") or error or "Orca command failed"))
        return payload

    @staticmethod
    def _nested(value: Mapping[str, Any], *path: str) -> Any:
        current: Any = value
        for part in path:
            if not isinstance(current, Mapping):
                return None
            current = current.get(part)
        return current

    @staticmethod
    def _find_identifier(value: Any, keys: set[str]) -> str | None:
        if isinstance(value, Mapping):
            for key, item in value.items():
                if key in keys and isinstance(item, str) and item:
                    return item
            for item in value.values():
                found = OrcaRunner._find_identifier(item, keys)
                if found:
                    return found
        elif isinstance(value, list):
            for item in value:
                found = OrcaRunner._find_identifier(item, keys)
                if found:
                    return found
        return None

    def _ensure_sender(self, job_id: str) -> str:
        cached = self._senders.get(job_id)
        if cached:
            return cached
        title = f"YTF Coordinator {job_id[:8]}"
        listed = self._run_json(
            [
                self.orca_cli,
                "terminal",
                "list",
                "--worktree",
                f"path:{self.repo_root}",
                "--limit",
                "100",
                "--json",
            ]
        )
        terminals = self._nested(listed, "result", "terminals") or []
        for terminal in terminals:
            if (
                terminal.get("title") == title
                and terminal.get("connected") is True
                and terminal.get("writable") is True
            ):
                self._senders[job_id] = terminal["handle"]
                return terminal["handle"]
        created = self._run_json(
            [
                self.orca_cli,
                "terminal",
                "create",
                "--worktree",
                f"path:{self.repo_root}",
                "--title",
                title,
                "--command",
                "zsh -l",
                "--json",
            ]
        )
        handle = self._find_identifier(created.get("result"), {"handle", "terminalHandle"})
        if not handle:
            raise OrcaAdapterError("Orca did not return a coordinator terminal handle")
        self._senders[job_id] = handle
        return handle

    def _ensure_run(self, job: Mapping[str, Any], sender: str) -> str:
        job_id = str(job["job_id"])
        existing = str(job.get("run_id") or self._runs.get(job_id) or "")
        if existing:
            self._runs[job_id] = existing
            return existing
        created = self._run_json(
            [
                self.orca_cli,
                "orchestration",
                "run-create",
                "--objective",
                f"Auto production after topic approval: {job['project_id']}:{job_id}",
                "--from",
                sender,
                "--json",
            ]
        )
        run_id = self._nested(created, "result", "run", "id")
        if not isinstance(run_id, str) or not run_id:
            raise OrcaAdapterError("Orca did not return a Run ID")
        self._runs[job_id] = run_id
        return run_id

    def _task_prompt(
        self,
        project: Path,
        job: Mapping[str, Any],
        stage: str,
        result_path: Path,
    ) -> str:
        role = {
            "research": "research",
            "media_collection": "production",
            "evidence_lock": "verification",
            "proposal": "story_visual",
        }[stage]
        configured = self.routing["roles"][role]
        stage_contracts = {
            "research": {
                "paths": [
                    "artifacts/research_brief.json",
                    "artifacts/evidence_registry.json",
                    "checkpoint_research.json",
                ],
                "artifacts": ["research_brief", "evidence_registry"],
                "status": "completed",
                "approval_required": "false",
                "verdict": "NOT_APPLICABLE",
            },
            "media_collection": {
                "paths": [
                    "artifacts/media_collection_manifest.json",
                    "automation/progress/media_collection.json",
                    "checkpoint_media_collection.json",
                ],
                "artifacts": ["media_collection_manifest"],
                "status": "completed",
                "approval_required": "false",
                "verdict": "NOT_APPLICABLE",
            },
            "evidence_lock": {
                "paths": [
                    "artifacts/evidence_registry.json",
                    "artifacts/decision_log.json",
                    "checkpoint_evidence_lock.json",
                ],
                "artifacts": ["evidence_registry", "decision_log"],
                "status": "completed",
                "approval_required": "false",
                "verdict": "PASS",
            },
            "proposal": {
                "paths": [
                    "artifacts/proposal_packet.json",
                    "artifacts/decision_log.json",
                    "checkpoint_proposal.json",
                ],
                "artifacts": ["proposal_packet", "decision_log"],
                "status": "awaiting_human",
                "approval_required": "true",
                "verdict": "NOT_APPLICABLE",
            },
        }
        contract = stage_contracts[stage]
        output_paths = "\n".join(f"- {path}" for path in contract["paths"])
        artifact_names = ", ".join(contract["artifacts"])
        collection_rules = ""
        if stage == "media_collection":
            collection_rules = """
Read skills/pipelines/youtube-factory/media-collection-director.md before collecting. Use the rights_cleared_media_collection tool and only the configured Pexels, Pixabay, Unsplash, explicit public-domain, CC0, CC BY, or CC BY-SA paths. Use no Gemini. Reject permission-required, purchase-only, restricted/editorial-only, unknown-rights, watermarked, preview-only, or inaccessible-original candidates before download. Frozen accepted bytes may additionally be written only under assets/source/**. Those media byte paths are bound inside media_collection_manifest.json and must not be added to the stage result artifact_paths list. Do not perform creative shot selection at this stage.
"""
        return f"""You are the {role} worker for the YouTube Factory canonical project.

PROJECT: {project}
FACTORY: {self.factory_root}
JOB_ID: {job['job_id']}
STAGE: {stage}
SELECTED_CANDIDATE: {job['selected_candidate_id']}
MODEL CONTRACT: runtime={configured['runtime']} model={configured['model']} effort={configured['effort']} profile={configured['profile']}

Read AGENT_GUIDE.md, config/orca-model-routing.yaml, pipeline_defs/youtube-factory.yaml, and the relevant director skill before acting. Work only on STAGE in the canonical ignored project directory. Use official/primary evidence first. Validate all produced artifacts against local JSON Schemas and write the canonical checkpoint.

Hard boundaries: no paid API, no TopView dispatch, no asset generation, no script, no visual plan, no render, no upload, no publish, no provider/model fallback, and no fabricated Human Gate approval. Evidence lock must independently verify exact research bytes and return PASS or fail. Proposal must end with checkpoint_proposal.json status awaiting_human, human_approval_required true, human_approved false.
{collection_rules}

The complete allowed output path set for this stage is exactly:
{output_paths}

The checkpoint must satisfy schemas/checkpoints/checkpoint.schema.json and lib.checkpoint.validate_checkpoint. It must use pipeline_type='youtube-factory', stage='{stage}', status='{contract['status']}', checkpoint_policy='guided', human_approval_required={contract['approval_required']}, and human_approved=false. Under checkpoint.artifacts, embed the exact full JSON object for each canonical artifact ({artifact_names}); do not substitute path/SHA pointer objects. Do not add fields rejected by the checkpoint schema.

After validating every artifact with schemas.artifacts.validate_artifact and the checkpoint with lib.checkpoint.validate_checkpoint, write JSON to {result_path} with exactly: outcome='success'; artifact_paths as a JSON array containing every allowed output path above exactly once; artifact_sha256 as a map keyed by those same paths; source_commit as 40 lowercase hex; and verdict='{contract['verdict']}'. Do not add run_id, task_id, or dispatch_id; the Coordinator binds those trusted transport identifiers itself. The result file must be written last. Then report worker_done exactly once. On any policy or integrity issue, do not write a success result; report failure/escalation.
"""

    def _create_task(self, run_id: str, sender: str, stage: str, prompt: str) -> str:
        created = self._run_json(
            [
                self.orca_cli,
                "orchestration",
                "task-create",
                "--spec",
                prompt,
                "--task-title",
                f"YouTube Factory {stage}",
                "--display-name",
                f"Auto {stage}",
                "--run",
                run_id,
                "--from",
                sender,
                "--json",
            ]
        )
        task_id = self._find_identifier(created.get("result"), {"taskId", "task_id", "id"})
        if not task_id:
            raise OrcaAdapterError("Orca did not return a Task ID")
        return task_id

    def _start_worker(
        self,
        run_id: str,
        sender: str,
        task_id: str,
        stage: str,
        attempt: int,
    ) -> str:
        role_name = {
            "evidence_lock": "verification",
            "proposal": "story_visual",
        }.get(stage)
        hermes_stage = {
            "research": ("research", "ytf-research"),
            "media_collection": ("production", "ytf-production"),
        }.get(stage)
        if hermes_stage is not None:
            role_label, profile = hermes_stage
            terminal = self._run_json(
                [
                    self.orca_cli,
                    "terminal",
                    "create",
                    "--worktree",
                    f"path:{self.repo_root}",
                    "--title",
                    f"YTF {role_label} {task_id}",
                    "--command",
                    (
                        f"cd {shlex.quote(str(self.factory_root))} && "
                        f"exec {profile} --no-restore-cwd"
                    ),
                    "--json",
                ]
            )
            handle = self._find_identifier(
                terminal.get("result"), {"handle", "terminalHandle"}
            )
            if not handle:
                raise OrcaAdapterError("Orca did not return the Hermes terminal")
            self._run_json(
                [
                    self.orca_cli,
                    "terminal",
                    "wait",
                    "--terminal",
                    handle,
                    "--for",
                    "tui-idle",
                    "--timeout-ms",
                    "120000",
                    "--json",
                ],
                timeout=130,
            )
            dispatched = self._run_json(
                [
                    self.orca_cli,
                    "orchestration",
                    "dispatch",
                    "--task",
                    task_id,
                    "--to",
                    handle,
                    "--from",
                    sender,
                    "--run",
                    run_id,
                    "--inject",
                    "--json",
                ]
            )
        else:
            role = self.routing["roles"][str(role_name)]
            args = [
                self.orca_cli,
                "orchestration",
                "worker-start",
                "--task",
                task_id,
                "--worktree",
                f"path:{self.repo_root}",
                "--agent",
                role["runtime"],
                "--model",
                role["model"],
                "--effort",
                role["effort"],
                "--display-name",
                f"YTF {stage} attempt {attempt + 1}",
                "--run",
                run_id,
                "--from",
                sender,
                "--timeout-ms",
                "120000",
                "--json",
            ]
            dispatched = self._run_json(args, timeout=130)
        dispatch_id = self._find_identifier(
            dispatched.get("result"), {"dispatchId", "dispatch_id", "id"}
        )
        if not dispatch_id:
            raise OrcaAdapterError("Orca did not return a Dispatch ID")
        return dispatch_id

    @staticmethod
    def _messages(delivery: Mapping[str, Any]) -> tuple[str | None, list[Mapping[str, Any]]]:
        result = delivery.get("result") if isinstance(delivery.get("result"), Mapping) else {}
        delivery_id = OrcaRunner._find_identifier(result, {"deliveryId", "delivery_id"})
        messages = result.get("messages") or result.get("items") or []
        return delivery_id, [item for item in messages if isinstance(item, Mapping)]

    @staticmethod
    def _message_payload(message: Mapping[str, Any]) -> Mapping[str, Any]:
        payload = message.get("payload")
        if isinstance(payload, Mapping):
            return payload
        if isinstance(payload, str):
            try:
                decoded = json.loads(payload)
            except json.JSONDecodeError:
                return {}
            if isinstance(decoded, Mapping):
                return decoded
        return {}

    def _wait_for_worker(
        self, run_id: str, sender: str, task_id: str, dispatch_id: str
    ) -> tuple[str, str]:
        deadline = time.monotonic() + self.stage_timeout
        ack: str | None = None
        while time.monotonic() < deadline:
            args = ["orca", "orchestration", "check"]
            if ack:
                args.extend(["--ack", ack])
            args.extend(
                [
                    "--terminal",
                    sender,
                    "--run",
                    run_id,
                    "--wait",
                    "--types",
                    "worker_done,escalation,question",
                    "--timeout-ms",
                    "60000",
                    "--json",
                ]
            )
            delivery = self._run_json(args, timeout=70)
            ack, messages = self._messages(delivery)
            for message in messages:
                kind = str(message.get("type") or message.get("messageType") or "")
                payload = self._message_payload(message)
                message_task = str(message.get("task_id") or message.get("taskId") or payload.get("taskId") or "")
                message_dispatch = str(message.get("dispatch_id") or message.get("dispatchId") or payload.get("dispatchId") or "")
                if message_task and message_task != task_id:
                    continue
                if message_dispatch and message_dispatch != dispatch_id:
                    continue
                if kind == "worker_done":
                    outcome = str(message.get("outcome") or payload.get("outcome") or "succeeded")
                    return outcome, str(message.get("body") or "")
                if kind in {"escalation", "question"}:
                    return "blocked", str(message.get("body") or kind)
        return "timeout", "worker did not settle before the stage timeout"

    @staticmethod
    def _load_result(path: Path) -> StageResult:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise OrcaAdapterError(f"missing or invalid stage result: {path}") from exc
        allowed = {
            "outcome",
            "artifact_paths",
            "artifact_sha256",
            "source_commit",
            "verdict",
        }
        if not isinstance(value, dict) or set(value) != allowed or value.get("outcome") != "success":
            raise OrcaAdapterError("stage result contract violation")
        paths = value.get("artifact_paths")
        hashes = value.get("artifact_sha256")
        if (
            not isinstance(paths, list)
            or not all(isinstance(item, str) and item for item in paths)
            or len(paths) != len(set(paths))
            or not isinstance(hashes, dict)
            or not all(
                isinstance(key, str) and isinstance(item, str)
                for key, item in hashes.items()
            )
        ):
            raise OrcaAdapterError("stage result contract violation")
        return StageResult(**value)

    @staticmethod
    def _bind_provenance(
        result: StageResult,
        *,
        run_id: str,
        task_id: str,
        dispatch_id: str,
    ) -> StageResult:
        return replace(
            result,
            run_id=run_id,
            task_id=task_id,
            dispatch_id=dispatch_id,
        )

    def run_stage(self, project: Path, job: dict[str, Any], stage: str) -> StageResult:
        run_id = task_id = dispatch_id = ""
        try:
            sender = self._ensure_sender(job["job_id"])
            run_id = self._ensure_run(job, sender)
            attempt = int(job.get("attempt", 0))
            result_path = (
                project
                / "automation/stage-results"
                / job["job_id"]
                / f"{stage}-attempt-{attempt}.json"
            )
            result_path.parent.mkdir(parents=True, exist_ok=True)
            prompt = self._task_prompt(project, job, stage, result_path)
            task_id = self._create_task(run_id, sender, stage, prompt)
            dispatch_id = self._start_worker(
                run_id, sender, task_id, stage, attempt
            )
            outcome, detail = self._wait_for_worker(
                run_id, sender, task_id, dispatch_id
            )
            if outcome != "succeeded":
                error_class = "policy" if outcome == "blocked" else "ordinary"
                return StageResult.failure(
                    stage,
                    error_class,
                    detail or outcome,
                    run_id=run_id,
                    task_id=task_id,
                    dispatch_id=dispatch_id,
                )
            result = self._load_result(result_path)
            return self._bind_provenance(
                result,
                run_id=run_id,
                task_id=task_id,
                dispatch_id=dispatch_id,
            )
        except (OSError, subprocess.SubprocessError, OrcaAdapterError) as exc:
            return StageResult.failure(
                stage,
                "ordinary",
                str(exc),
                run_id=run_id,
                task_id=task_id,
                dispatch_id=dispatch_id,
            )
        finally:
            if dispatch_id:
                try:
                    self._run_json(
                        [
                            self.orca_cli,
                            "orchestration",
                            "worker-release",
                            "--dispatch",
                            dispatch_id,
                            "--json",
                        ]
                    )
                except OrcaAdapterError:
                    pass
