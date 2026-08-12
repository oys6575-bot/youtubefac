"""Read-only projection for the mobile production dashboard."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from backlot.auto_dispatch import JobValidationError, load_job
from backlot.state import load_board_state
from lib.topic_scorecard import rank_candidates


ROOT = Path(__file__).resolve().parents[1]
ROUTING_PATH = ROOT / "config/orca-model-routing.yaml"
TWO_STEP_GATES = frozenset(
    {"budget", "asset_selection", "final_review", "title_thumbnail", "publish"}
)
PROVIDER_NAMES = ("youtube", "pexels", "pixabay", "unsplash")


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return {}
    return value if isinstance(value, dict) else {}


def _raw_hash(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def _topic_artifacts(project: Path, board: dict[str, Any]) -> tuple[dict | None, dict | None]:
    shortlist = _read_json(project / "artifacts/topic_shortlist.json")
    verification = _read_json(project / "artifacts/topic_verification.json")
    if shortlist is None:
        candidate = board.get("artifacts", {}).get("topic_shortlist")
        shortlist = candidate if isinstance(candidate, dict) else None
    if verification is None:
        candidate = board.get("artifacts", {}).get("topic_verification")
        verification = candidate if isinstance(candidate, dict) else None
    return shortlist, verification


def _candidate_cards(shortlist: dict | None, verification: dict | None) -> list[dict[str, Any]]:
    if not shortlist or not isinstance(shortlist.get("candidates"), list):
        return []
    try:
        ranked = rank_candidates(shortlist["candidates"])
    except Exception:
        return []
    verdicts = {
        item.get("id"): item.get("verdict")
        for item in (verification or {}).get("candidate_results", [])
        if isinstance(item, dict)
    }
    return [
        {
            "id": item.get("id"),
            "rank": item.get("rank"),
            "title": item.get("title"),
            "location": item.get("location"),
            "collapse_date": item.get("collapse_date"),
            "question": item.get("one_line_question"),
            "score": item.get("total"),
            "score_status": item.get("status"),
            "verification": verdicts.get(item.get("id"), "NOT_VERIFIED"),
            "official_source_count": sum(
                1
                for source in item.get("sources", [])
                if isinstance(source, dict) and source.get("class") == "official_or_primary"
            ),
        }
        for item in ranked
    ]


def _gate_summary(stage: str, board: dict[str, Any], candidates: list[dict]) -> dict[str, Any]:
    if stage == "topic_approval":
        return {
            "title": "다음 다큐멘터리 주제를 선택하세요",
            "detail": f"독립 검증을 통과한 후보 {sum(c['verification'] == 'PASS' for c in candidates)}건",
        }
    if stage == "budget":
        cost = board.get("cost") or {}
        return {
            "title": "제작 예산을 확인하세요",
            "detail": f"예상·예약 비용 ${float(cost.get('total_reserved_usd') or 0):.2f}",
        }
    labels = {
        "evidence_lock": "사실과 출처를 고정하세요",
        "proposal": "영상 구성안을 승인하세요",
        "script": "최종 대본을 승인하세요",
        "animatic": "Animatic의 흐름과 타이밍을 확인하세요",
        "asset_selection": "편집에 사용할 에셋을 선택하세요",
        "final_review": "완성 영상을 검수하세요",
        "title_thumbnail": "제목과 썸네일을 승인하세요",
        "publish": "공개 범위와 게시 계획을 승인하세요",
    }
    return {"title": labels.get(stage, f"{stage} 단계를 확인하세요"), "detail": "승인은 실행 허용만 기록합니다."}


def _roles(project: Path) -> list[dict[str, Any]]:
    routing = _read_yaml(ROUTING_PATH)
    preflight = _read_json(project / "system/orca-preflight.json") or {}
    preflight_roles = preflight.get("roles") if isinstance(preflight.get("roles"), dict) else {}
    output = []
    for role, assignment in (routing.get("roles") or {}).items():
        if not isinstance(assignment, dict):
            continue
        stored = preflight_roles.get(role) if isinstance(preflight_roles.get(role), dict) else {}
        output.append(
            {
                "role": role,
                "runtime": assignment.get("runtime"),
                "model": assignment.get("model"),
                "resource_lane": assignment.get("resource_lane"),
                "status": stored.get("status", "assigned_not_checked"),
                "checked_at": stored.get("checked_at"),
            }
        )
    return output


def _providers(project: Path) -> dict[str, dict[str, Any]]:
    report = _read_json(project / "system/provider-preflight.json") or {}
    checked_at = report.get("checked_at")
    stored = report.get("providers") if isinstance(report.get("providers"), dict) else {}
    output: dict[str, dict[str, Any]] = {}
    for name in PROVIDER_NAMES:
        item = stored.get(name) if isinstance(stored.get(name), dict) else {}
        output[name] = {
            "status": item.get("status", "not_checked"),
            "checked_at": item.get("checked_at", checked_at if item else None),
        }
    routing = _read_yaml(ROUTING_PATH)
    topview = routing.get("topview") if isinstance(routing.get("topview"), dict) else {}
    output["topview"] = {
        "status": "manual",
        "checked_at": None,
        "mode": topview.get("mode", "manual_semi_automatic"),
        "api_enabled": bool(topview.get("api_enabled", False)),
    }
    return output


def _automation(project: Path) -> dict[str, Any] | None:
    jobs_dir = project / "automation/jobs"
    if not jobs_dir.is_dir():
        return None
    jobs: list[tuple[Path, dict[str, Any]]] = []
    for path in jobs_dir.glob("*.json"):
        try:
            jobs.append((path, load_job(path)))
        except JobValidationError:
            continue
    if not jobs:
        return None
    path, job = max(jobs, key=lambda item: (item[1]["created_at"], item[1]["job_id"]))
    stage_labels = {
        "research": "자료조사",
        "evidence_lock": "사실검증",
        "proposal": "기획안 작성",
    }
    state = job["state"]
    if state == "queued":
        label = f"{stage_labels[job['current_stage']]} 시작 대기"
    elif state == "running":
        label = f"{stage_labels[job['current_stage']]} 실행 중"
    elif state == "retrying":
        label = f"{stage_labels[job['current_stage']]} 재시도 중"
    elif state == "awaiting_human":
        label = "기획안 승인 대기"
    elif state == "failed":
        label = "실패 · 다시 실행 가능"
    else:
        label = "자동 작업 완료"
    return {
        "job_id": job["job_id"],
        "job_sha256": _raw_hash(path),
        "state": state,
        "current_stage": job["current_stage"],
        "label": label,
        "attempt": job["attempt"],
        "max_retries": job["max_retries"],
        "completed_stages": [item["stage"] for item in job["stage_results"]],
        "last_error": job["last_error"],
        "can_retry": state == "failed",
        "updated_at": job["updated_at"],
    }


def build_mobile_state(project_dir: Path) -> dict[str, Any]:
    """Derive a bounded mobile view without network/provider side effects."""
    project = Path(project_dir)
    board = load_board_state(project)
    shortlist, verification = _topic_artifacts(project, board)
    candidates = _candidate_cards(shortlist, verification)

    stages: list[dict[str, Any]] = []
    current_gate = None
    for item in board.get("stages", []):
        stage = item.get("name")
        checkpoint_hash = _raw_hash(project / f"checkpoint_{stage}.json") if stage else None
        card = {
            "name": stage,
            "status": item.get("status", "pending"),
            "gated": bool(item.get("gated")),
            "human_approved": item.get("human_approved"),
            "checkpoint_sha256": checkpoint_hash,
            "timestamp": item.get("timestamp"),
        }
        stages.append(card)
        if current_gate is None and card["status"] == "awaiting_human" and card["gated"]:
            current_gate = {
                "stage": stage,
                "checkpoint_sha256": checkpoint_hash,
                "status": "awaiting_human",
                "requires_two_step": stage in TWO_STEP_GATES,
                "summary": _gate_summary(stage, board, candidates),
            }

    last_activity = board.get("last_activity") or 0
    last_sync = (
        datetime.fromtimestamp(last_activity, tz=timezone.utc).isoformat()
        if last_activity
        else None
    )
    return {
        "version": "1.0",
        "source_of_truth": "openmontage",
        "project": {
            "project_id": board.get("project_id", project.name),
            "title": board.get("title", project.name),
            "pipeline_type": (board.get("pipeline") or {}).get("pipeline_type"),
            "last_sync": last_sync,
            "live": bool(board.get("live")),
        },
        "stages": stages,
        "current_gate": current_gate,
        "topic_candidates": candidates,
        "automation": _automation(project),
        "roles": _roles(project),
        "providers": _providers(project),
        "cost": board.get("cost") or {
            "total_spent_usd": 0,
            "total_reserved_usd": 0,
            "budget_remaining_usd": None,
        },
        "metrics": {
            "completed_stages": sum(item["status"] == "completed" for item in stages),
            "total_stages": len(stages),
            "approval_receipts": len(list((project / "approvals/receipts").glob("*.json")))
            if (project / "approvals/receipts").is_dir()
            else 0,
            "renders": len((board.get("media") or {}).get("renders", [])),
        },
        "data_quality": {
            "topic_candidates": "available" if candidates else "unavailable",
            "provider_status": "stored_preflight" if (project / "system/provider-preflight.json").is_file() else "not_checked",
            "orca_status": "stored_preflight" if (project / "system/orca-preflight.json").is_file() else "not_checked",
        },
    }
