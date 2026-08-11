"""Create deterministic TopView job packs without calling or controlling TopView."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
from typing import Any

from schemas.artifacts import validate_artifact
from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolTier,
)


_ID = re.compile(r"^[A-Z][A-Z0-9_-]{2,63}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside(project_dir: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(project_dir)
        return True
    except ValueError:
        return False


class TopViewManualHandoff(BaseTool):
    name = "topview_manual_handoff"
    version = "1.1.0"
    tier = ToolTier.GENERATE
    capability = "video_generation"
    provider = "topview_manual"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies: list[str] = []
    install_instructions = "No provider credentials required. TopView is operated manually."
    capabilities = ["manual_job_pack", "reference_freeze", "operator_handoff"]
    supports = {
        "manual_ui": True,
        "network_calls": False,
        "browser_automation": False,
        "automatic_billing": False,
    }
    best_for = [
        "preparing approved cinematic reconstruction shots for manual TopView generation",
        "freezing prompt, settings, provenance, and filenames before external work",
    ]
    not_good_for = [
        "automatic generation",
        "automatic browser control",
        "bypassing the budget or asset-selection Human Gates",
    ]
    input_schema = {
        "type": "object",
        "required": ["project_dir", "visual_plan_path", "batch_id"],
        "properties": {
            "project_dir": {"type": "string"},
            "visual_plan_path": {"type": "string"},
            "batch_id": {"type": "string", "pattern": _ID.pattern},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "job_pack_path": {"type": "string"},
            "instructions_path": {"type": "string"},
            "batch_dir": {"type": "string"},
            "job_count": {"type": "integer"},
            "state": {"const": "awaiting_manual_external"},
        },
    }
    resource_profile = ResourceProfile(
        cpu_cores=1,
        ram_mb=128,
        vram_mb=0,
        disk_mb=100,
        network_required=False,
    )
    idempotency_key_fields = ["project_dir", "visual_plan_path", "batch_id"]
    side_effects = ["writes a manual job pack and frozen references inside the project"]
    agent_skills = ["topview-manual-handoff"]
    user_visible_verification = [
        "Open INSTRUCTIONS.md and confirm each TopView job matches the approved animatic",
        "Confirm all frozen references open before starting manual generation",
    ]

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    @staticmethod
    def _workspace_and_mode(
        reference_count: int,
        requirements: list[str],
        duration_seconds: float,
    ) -> tuple[str, str]:
        normalized = {item.strip().lower().replace("_", "-") for item in requirements}
        if "3d-shot-composer" in normalized or "spatial-continuity" in normalized:
            return "SHOT_COMPOSER_3D", "COMPOSITE_SCENE"
        if duration_seconds > 15 or "canvas" in normalized or "multi-scene" in normalized:
            workspace = "CANVAS"
        else:
            workspace = "BOARD"
        if "storyboard-only" in normalized:
            return "FILM_STUDIO", "STORYBOARD_ONLY"
        if "motion-control" in normalized:
            return workspace, "MOTION_CONTROL"
        if "video-edit" in normalized or "video-to-video" in normalized:
            return workspace, "VIDEO_EDIT"
        if "first-last-frame" in normalized:
            return workspace, "FIRST_LAST_FRAME"
        if "multi-reference" in normalized or "omni-reference" in normalized or reference_count > 1:
            return workspace, "MULTI_REFERENCE"
        if reference_count == 1:
            return workspace, "IMAGE_TO_VIDEO"
        return workspace, "TEXT_TO_VIDEO"

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        project_dir = Path(str(inputs.get("project_dir", ""))).expanduser().resolve()
        if not project_dir.is_dir():
            return ToolResult(success=False, error=f"project_dir not found: {project_dir}")

        batch_id = str(inputs.get("batch_id", ""))
        if not _ID.fullmatch(batch_id):
            return ToolResult(success=False, error=f"invalid batch_id: {batch_id}")

        plan_input = Path(str(inputs.get("visual_plan_path", ""))).expanduser()
        plan_path = (project_dir / plan_input).resolve() if not plan_input.is_absolute() else plan_input.resolve()
        if not _inside(project_dir, plan_path):
            return ToolResult(success=False, error="visual_plan_path is outside project")
        if not plan_path.is_file():
            return ToolResult(success=False, error=f"visual_plan_path not found: {plan_path}")

        try:
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            validate_artifact("visual_plan", plan)
        except Exception as exc:
            return ToolResult(success=False, error=f"invalid visual plan: {exc}")

        global_style = plan.get("global_style", {})
        prepared_jobs: list[dict[str, Any]] = []
        pending_copies: list[tuple[Path, str]] = []

        for sequence in plan.get("sequences", []):
            for shot in sequence.get("shots", []):
                if shot.get("provider_route", {}).get("mode") != "TOPVIEW_HANDOFF":
                    continue

                brief = shot["generation_brief"]
                route = shot["provider_route"]
                reference_files: list[dict[str, str]] = []
                for reference in brief.get("reference_paths", []):
                    source = (project_dir / reference).resolve()
                    if not _inside(project_dir, source):
                        return ToolResult(
                            success=False,
                            error=f"reference path is outside project: {reference}",
                        )
                    if not source.is_file():
                        return ToolResult(success=False, error=f"reference not found: {reference}")
                    checksum = _sha256(source)
                    frozen_name = f"{checksum[:16]}-{source.name}"
                    frozen_rel = Path("handoff/topview/outbox") / batch_id / "references" / frozen_name
                    reference_files.append(
                        {
                            "original_path": source.relative_to(project_dir).as_posix(),
                            "frozen_path": frozen_rel.as_posix(),
                            "sha256": checksum,
                            "role": "ENVIRONMENT_REFERENCE",
                        }
                    )
                    pending_copies.append((source, frozen_rel.as_posix()))

                requirements = route.get("model_requirements", [])
                workspace, task_mode = self._workspace_and_mode(
                    len(reference_files),
                    requirements,
                    float(shot["duration_seconds"]),
                )
                prepared_jobs.append(
                    {
                        "shot_id": shot["shot_id"],
                        "sequence_id": sequence["sequence_id"],
                        "purpose": sequence["purpose"],
                        "ui_workspace": workspace,
                        "task_mode": task_mode,
                        "prompt": shot["prompt_intent"],
                        "negative_prompt": brief["negative_prompt"],
                        "reference_files": reference_files,
                        "model_recommendation": brief["model_recommendation"],
                        "model_requirements": requirements,
                        "model_selection": {
                            "candidate_family": brief["model_recommendation"],
                            "exact_ui_label_required": True,
                            "allow_silent_substitution": False,
                            "live_capability_check_required": True,
                        },
                        "aspect_ratio": global_style.get("aspect_ratio", "16:9"),
                        "resolution": global_style.get("resolution", "1920x1080"),
                        "fps": global_style.get("fps", 30),
                        "duration_seconds": shot["duration_seconds"],
                        "native_audio_requested": "native-audio" in {
                            item.strip().lower().replace("_", "-") for item in requirements
                        },
                        "camera": shot.get("camera", {}),
                        "lighting": shot.get("lighting", {}),
                        "composition": shot.get("composition", ""),
                        "negative_space": shot.get("negative_space", ""),
                        "continuity": {
                            "bindings": shot.get("continuity_bindings", []),
                            "preserve_environment": True,
                            "preserve_character": "character-consistency" in {
                                item.strip().lower().replace("_", "-") for item in requirements
                            },
                            "preserve_camera_axis": True,
                        },
                        "multi_shot_plan": [],
                        "evidence_policy": {
                            "generated_text_allowed": False,
                            "exact_facts_added_in_composite": True,
                            "preserve_source_geometry_only": bool(reference_files),
                            "disclosure_added_in_composite": True,
                        },
                        "budget": {
                            "max_credits": route.get("estimated_credits"),
                            "max_attempts": 3,
                            "capture_cost_before_submit": True,
                            "stop_before_overage": True,
                        },
                        "disclosure_label": shot["disclosure"]["label"],
                        "expected_filename": f"{shot['shot_id']}__candidate_A.mp4",
                        "operator_notes": brief["operator_notes"],
                        "operator_record": {
                            "actual_model_display_name": None,
                            "credits_charged": None,
                            "generation_notes": "",
                        },
                    }
                )

        if not prepared_jobs:
            return ToolResult(success=False, error="visual plan has no TOPVIEW_HANDOFF shots")

        job_pack = {
            "schema_version": "1.1.0",
            "capability_catalog_version": "2026-08-11",
            "batch_id": batch_id,
            "project_id": plan["project_id"],
            "plan_id": plan["plan_id"],
            "plan_sha256": _sha256(plan_path),
            "created_from_plan_at": plan["generated_by"]["created_at"],
            "integration_mode": "manual_ui",
            "state": "awaiting_manual_external",
            "operator_required": True,
            "automated_api_cost_usd": 0,
            "operator_policy": {
                "platform": "TopView web UI",
                "ui_only": True,
                "api_allowed": False,
                "mcp_allowed": False,
                "browser_automation_allowed": False,
                "budget_gate_required": True,
                "asset_selection_gate_required": True,
            },
            "jobs": prepared_jobs,
        }
        try:
            validate_artifact("topview_job_pack", job_pack)
        except Exception as exc:
            return ToolResult(success=False, error=f"job pack failed validation: {exc}")

        batch_dir = project_dir / "handoff" / "topview" / "outbox" / batch_id
        job_path = batch_dir / "job.json"
        if job_path.is_file():
            try:
                existing = json.loads(job_path.read_text(encoding="utf-8"))
            except Exception as exc:
                return ToolResult(success=False, error=f"existing batch job is unreadable: {exc}")
            if existing.get("plan_sha256") != job_pack["plan_sha256"]:
                return ToolResult(success=False, error="batch_id already belongs to a different plan")

        for source, frozen_rel in pending_copies:
            target = project_dir / frozen_rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)

        batch_dir.mkdir(parents=True, exist_ok=True)
        job_path.write_text(
            json.dumps(job_pack, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        instructions_path = batch_dir / "INSTRUCTIONS.md"
        instructions_path.write_text(self._instructions(job_pack), encoding="utf-8")

        artifacts = [str(job_path), str(instructions_path)]
        artifacts.extend(str(project_dir / item[1]) for item in pending_copies)
        return ToolResult(
            success=True,
            data={
                "job_pack_path": str(job_path),
                "instructions_path": str(instructions_path),
                "batch_dir": str(batch_dir),
                "job_count": len(prepared_jobs),
                "state": "awaiting_manual_external",
            },
            artifacts=artifacts,
            cost_usd=0.0,
        )

    @staticmethod
    def _instructions(job_pack: dict[str, Any]) -> str:
        lines = [
            f"# TopView 수동 작업 — {job_pack['batch_id']}",
            "",
            "이 묶음은 자동 생성 요청이 아닙니다. 사용자가 TopView 웹 화면에서 직접 작업합니다.",
            "",
            "## 순서",
            "",
            "1. GATE_ANIMATIC·GATE_BUDGET 승인을 OpenMontage에서 확인합니다.",
            "2. 지정된 작업 공간과 모드를 열고 frozen reference를 역할별로 입력합니다.",
            "3. 화면에 보이는 정확한 모델명·해상도·길이·오디오·큐 모드를 확인합니다.",
            "4. 제출 전 설정 화면과 예상 크레딧을 캡처하고, 상한을 넘으면 멈춥니다.",
            "5. 후보를 비교하고 기대 파일명으로 다운로드합니다.",
            f"6. 결과와 operator-result.json을 `handoff/topview/inbox/{job_pack['batch_id']}/`에 넣습니다.",
            "7. 반입된 파일은 후보일 뿐입니다. Asset Selection Gate에서 사람이 선택합니다.",
            "",
            "## 숏 목록",
            "",
        ]
        for job in job_pack["jobs"]:
            lines.extend(
                [
                    f"### {job['shot_id']}",
                    "",
                    f"- 목적: {job['purpose']}",
                    f"- 작업 공간: `{job['ui_workspace']}`",
                    f"- 작업 모드: `{job['task_mode']}`",
                    f"- 파일명: `{job['expected_filename']}`",
                    f"- 길이: {job['duration_seconds']}초 / {job['aspect_ratio']} / {job['resolution']}",
                    f"- 모델 권장: {job['model_recommendation']}",
                    f"- 크레딧 상한: {job['budget']['max_credits']}",
                    f"- 최대 시도: {job['budget']['max_attempts']}회",
                    f"- 프롬프트: {job['prompt']}",
                    f"- 제외 프롬프트: {job['negative_prompt']}",
                    "- 사실 텍스트: 생성 화면에 넣지 않고 후단 합성에서만 추가",
                    f"- 공개 라벨: {job['disclosure_label']}",
                    f"- 작업 메모: {job['operator_notes']}",
                    "",
                ]
            )
        return "\n".join(lines).rstrip() + "\n"
