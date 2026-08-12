"""Read-only projection for the mobile production dashboard."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml
import jsonschema

from backlot.auto_dispatch import JobValidationError, load_job
from backlot.state import load_board_state
from lib.topic_scorecard import rank_candidates


ROOT = Path(__file__).resolve().parents[1]
ROUTING_PATH = ROOT / "config/orca-model-routing.yaml"
COLLECTION_PROGRESS_SCHEMA = (
    ROOT / "schemas/mobile-dashboard/media-collection-progress.schema.json"
)
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


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _stale_gate(stage: str, stages: list[dict[str, Any]]) -> bool:
    """Return true when a newer upstream rerun invalidates a pending gate."""
    if stage != "proposal":
        return False
    by_name = {item.get("name"): item for item in stages}
    proposal_time = _timestamp((by_name.get("proposal") or {}).get("timestamp"))
    collection_time = _timestamp(
        (by_name.get("media_collection") or {}).get("timestamp")
    )
    return bool(proposal_time and collection_time and collection_time > proposal_time)


def _script_view(project: Path) -> dict[str, Any]:
    script = _read_json(project / "artifacts/script.json") or {}
    plan = _read_json(project / "artifacts/visual_plan.json") or {}
    sections = []
    for section in script.get("sections", []):
        if not isinstance(section, dict):
            continue
        sections.append(
            {
                "id": section.get("id"),
                "label": section.get("label") or section.get("id"),
                "text": section.get("text", ""),
                "start_seconds": float(section.get("start_seconds") or 0),
                "end_seconds": float(section.get("end_seconds") or 0),
            }
        )
    prompts = []
    for sequence in plan.get("sequences", []):
        if not isinstance(sequence, dict):
            continue
        for shot in sequence.get("shots", []):
            if not isinstance(shot, dict):
                continue
            prompts.append(
                {
                    "sequence_id": sequence.get("sequence_id"),
                    "sequence_purpose": sequence.get("purpose"),
                    "pacing_profile": sequence.get("pacing_profile"),
                    "shot_id": shot.get("shot_id"),
                    "representation": shot.get("representation"),
                    "prompt": shot.get("prompt_intent", ""),
                    "provider_route": shot.get("provider_route"),
                    "duration_seconds": float(shot.get("duration_seconds") or 0),
                }
            )
    return {
        "status": "available" if sections else "preparing",
        "title": script.get("title"),
        "total_duration_seconds": float(script.get("total_duration_seconds") or 0),
        "sections": sections,
        "visual_prompts": prompts,
    }


def _asset_label(item: dict[str, Any], queries: list[dict[str, Any]]) -> str:
    claims = set(item.get("claim_ids") or [])
    for query in queries:
        if isinstance(query, dict) and claims.intersection(query.get("claim_ids") or []):
            text = query.get("text")
            if isinstance(text, str) and text:
                return text
    return str(item.get("id") or "에셋")


def _asset_library(project: Path, project_id: str) -> dict[str, Any]:
    manifest = _read_json(project / "artifacts/media_collection_manifest.json") or {}
    queries = [item for item in manifest.get("queries", []) if isinstance(item, dict)]
    items = []
    counts = {"image": 0, "video": 0, "audio": 0}
    for item in manifest.get("items", []):
        if not isinstance(item, dict):
            continue
        media_type = item.get("media_type")
        asset_id = item.get("id")
        if media_type not in counts or not isinstance(asset_id, str) or not asset_id:
            continue
        technical = item.get("technical") if isinstance(item.get("technical"), dict) else {}
        encoded_project = quote(project_id, safe="")
        encoded_asset = quote(asset_id, safe="")
        counts[media_type] += 1
        items.append(
            {
                "id": asset_id,
                "media_type": media_type,
                "label": _asset_label(item, queries),
                "media_url": f"/api/mobile/project/{encoded_project}/media/{encoded_asset}",
                "preview_url": f"/api/mobile/project/{encoded_project}/preview/{encoded_asset}",
                "width": int(technical.get("width") or 0),
                "height": int(technical.get("height") or 0),
                "duration_seconds": float(technical.get("duration_seconds") or 0),
            }
        )
    return {
        "status": manifest.get("collection_status", "preparing"),
        "summary": {
            "total": len(items),
            "images": counts["image"],
            "videos": counts["video"],
            "audio": counts["audio"],
        },
        "items": items,
    }


def _edit_view(project: Path) -> dict[str, Any]:
    edit = _read_json(project / "artifacts/edit_decisions.json") or {}
    cuts = []
    for cut in edit.get("cuts", []):
        if not isinstance(cut, dict):
            continue
        cuts.append(
            {
                "id": cut.get("id"),
                "in_seconds": float(cut.get("in_seconds") or 0),
                "out_seconds": float(cut.get("out_seconds") or 0),
                "reason": cut.get("reason"),
            }
        )
    return {
        "status": "in_progress" if cuts else "not_started",
        "render_runtime": edit.get("render_runtime"),
        "cuts": cuts,
        "gaps": list((edit.get("metadata") or {}).get("asset_gaps") or [])
        if isinstance(edit.get("metadata"), dict)
        else [],
    }


def _review_and_final_views(project: Path, project_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    review = _read_json(project / "artifacts/final_review.json") or {}
    report = _read_json(project / "artifacts/render_report.json") or {}
    outputs = [item for item in report.get("outputs", []) if isinstance(item, dict)]
    review_view = {
        "status": review.get("status", "not_ready"),
        "checks": review.get("checks") if isinstance(review.get("checks"), dict) else {},
        "issues": list(review.get("issues_found") or []),
        "recommended_action": review.get("recommended_action"),
        "has_preview": bool(outputs),
        "preview_url": f"/api/mobile/project/{quote(project_id, safe='')}/render/latest" if outputs else None,
    }
    passed = review.get("status") == "pass" and bool(outputs)
    final_view = {
        "status": "ready" if passed else "not_ready",
        "video_url": f"/api/mobile/project/{quote(project_id, safe='')}/render/final" if passed else None,
        "download_url": f"/api/mobile/project/{quote(project_id, safe='')}/render/final?download=1" if passed else None,
        "output": {
            "format": outputs[0].get("format"),
            "resolution": outputs[0].get("resolution"),
            "duration_seconds": outputs[0].get("duration_seconds"),
        } if passed else None,
    }
    return review_view, final_view


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


def _collection_progress(project: Path) -> dict[str, Any] | None:
    value = _read_json(project / "automation/progress/media_collection.json")
    schema = _read_json(COLLECTION_PROGRESS_SCHEMA)
    if value is None or schema is None:
        return None
    try:
        jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        ).validate(value)
    except jsonschema.ValidationError:
        return None
    return {
        "state": value["state"],
        "current_source": value["current_source"],
        "current_query": value["current_query"],
        "sources": {
            "attempted": list(value["sources"]["attempted"]),
            "completed": list(value["sources"]["completed"]),
            "failed": list(value["sources"]["failed"]),
        },
        "counts": dict(value["counts"]),
        "rejected_counts": dict(value["rejected_counts"]),
        "elapsed_seconds": value["elapsed_seconds"],
        "updated_at": value["updated_at"],
        "error": "자료 수집 중 오류가 기록되었습니다." if value["error"] else None,
    }


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
        "media_collection": "실제 자료 수집",
        "evidence_lock": "사실검증",
        "proposal": "기획안 작성",
    }
    state = job["state"]
    collection = _collection_progress(project)
    collection_active = bool(
        collection and collection.get("state") in {"searching", "downloading"}
    )
    active_stage = "media_collection" if collection_active else job["current_stage"]
    if collection_active:
        label = "실제 자료 수집 실행 중"
    elif state == "queued":
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
        "active_stage": active_stage,
        "label": label,
        "attempt": job["attempt"],
        "max_retries": job["max_retries"],
        "completed_stages": [item["stage"] for item in job["stage_results"]],
        "last_error": job["last_error"],
        "can_retry": state == "failed",
        "updated_at": job["updated_at"],
        "media_collection": collection,
    }


def build_mobile_state(project_dir: Path) -> dict[str, Any]:
    """Derive a bounded mobile view without network/provider side effects."""
    project = Path(project_dir)
    board = load_board_state(project)
    shortlist, verification = _topic_artifacts(project, board)
    candidates = _candidate_cards(shortlist, verification)

    stages: list[dict[str, Any]] = []
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

    current_gate = None
    for card in stages:
        stage = card["name"]
        if (
            current_gate is None
            and card["status"] == "awaiting_human"
            and card["gated"]
            and not _stale_gate(stage, stages)
        ):
            current_gate = {
                "stage": stage,
                "checkpoint_sha256": card["checkpoint_sha256"],
                "status": "awaiting_human",
                "requires_two_step": stage in TWO_STEP_GATES,
                "summary": _gate_summary(stage, board, candidates),
            }

    stale_proposal = _stale_gate("proposal", stages)
    automation = _automation(project)
    if stale_proposal:
        current_work = {
            "stage": "proposal_refresh",
            "status": "in_progress",
            "title": "수집 자료를 반영한 새 기획안 준비",
            "detail": "새 기획안이 만들어질 때까지 이전 구성안 승인은 숨깁니다.",
        }
    elif automation:
        current_work = {
            "stage": automation.get("active_stage") or automation.get("current_stage"),
            "status": automation.get("state"),
            "title": automation.get("label"),
            "detail": "현재 제작 상태를 프로젝트 기록에서 실시간으로 읽고 있습니다.",
        }
    else:
        active = next(
            (
                item
                for item in stages
                if item["status"] in {"in_progress", "awaiting_human"}
            ),
            None,
        )
        current_work = {
            "stage": active["name"] if active else None,
            "status": active["status"] if active else "idle",
            "title": "현재 작업 대기" if active is None else active["name"].replace("_", " "),
            "detail": "다음 제작 단계가 시작되면 여기에 표시됩니다.",
        }

    project_id = str(board.get("project_id", project.name))
    review_view, final_view = _review_and_final_views(project, project_id)

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
            "project_id": project_id,
            "title": board.get("title", project.name),
            "pipeline_type": (board.get("pipeline") or {}).get("pipeline_type"),
            "last_sync": last_sync,
            "live": bool(board.get("live")),
        },
        "stages": stages,
        "current_gate": current_gate,
        "current_work": current_work,
        "topic_candidates": candidates,
        "script_view": _script_view(project),
        "asset_library": _asset_library(project, project_id),
        "edit_view": _edit_view(project),
        "review_view": review_view,
        "final_view": final_view,
        "automation": automation,
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
