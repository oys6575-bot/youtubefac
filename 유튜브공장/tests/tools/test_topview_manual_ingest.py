from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from schemas.artifacts import validate_artifact
from tools.video.topview_manual_handoff import TopViewManualHandoff


ROOT = Path(__file__).resolve().parents[2]
VALID_PLAN = ROOT / "tests/fixtures/youtube_factory/visual_plan.valid.json"


def _ingest_class():
    return importlib.import_module("tools.video.topview_manual_ingest").TopViewManualIngest


def _render_video(path: Path, duration: float = 1.0) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        pytest.skip("ffmpeg is required for media-ingest contract tests")
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0xB87333:s=320x180:d={duration}",
            "-r",
            "30",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _prepared_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    project = tmp_path / "demo-project"
    artifact_dir = project / "artifacts"
    artifact_dir.mkdir(parents=True)
    plan = json.loads(VALID_PLAN.read_text(encoding="utf-8"))
    plan["global_style"]["resolution"] = "320x180"
    plan["sequences"][0]["shots"][1]["duration_seconds"] = 1
    plan["sequences"][0]["shots"][1]["generation_brief"]["reference_paths"] = []
    plan_path = artifact_dir / "visual_plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    handoff = TopViewManualHandoff().execute(
        {
            "project_dir": str(project),
            "visual_plan_path": str(plan_path),
            "batch_id": "BATCH_001",
        }
    )
    assert handoff.success is True, handoff.error
    inbox = project / "handoff/topview/inbox/BATCH_001"
    inbox.mkdir(parents=True)
    return project, plan_path, inbox


def _operator_metadata(inbox: Path, filename: str) -> Path:
    capture = inbox / "captures/SHOT_002-settings.png"
    capture.parent.mkdir(parents=True, exist_ok=True)
    capture.write_bytes(b"topview-settings-capture")
    capture_sha256 = hashlib.sha256(capture.read_bytes()).hexdigest()
    metadata = {
        "schema_version": "1.1.0",
        "batch_id": "BATCH_001",
        "recorded_at": "2026-08-11T21:00:00+09:00",
        "results": [
            {
                "shot_id": "SHOT_002",
                "filename": filename,
                "actual_ui_workspace": "BOARD",
                "actual_tool_label": "AI Video",
                "actual_model_display_name": "TopView UI selected model",
                "queue_mode": "STANDARD",
                "plan_tier": "Monthly test plan",
                "credits_estimated_before_submit": 12.5,
                "credits_charged": 12.5,
                "attempt_number": 1,
                "submitted_at": "2026-08-11T20:50:00+09:00",
                "completed_at": "2026-08-11T20:59:00+09:00",
                "provider_project_reference": "manual-board-reference",
                "settings_capture": {
                    "path": "captures/SHOT_002-settings.png",
                    "sha256": capture_sha256,
                },
                "generation_notes": "카메라 이동이 가장 절제된 후보 A",
            }
        ],
    }
    path = inbox / "operator-result.json"
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_valid_result_is_copied_and_registered_only_as_candidate(tmp_path: Path) -> None:
    project, _, inbox = _prepared_project(tmp_path)
    video = inbox / "SHOT_002__candidate_A.mp4"
    _render_video(video)
    metadata_path = _operator_metadata(inbox, video.name)

    result = _ingest_class()().execute(
        {
            "project_dir": str(project),
            "batch_id": "BATCH_001",
            "metadata_path": str(metadata_path),
        }
    )

    assert result.success is True, result.error
    manifest = json.loads(Path(result.data["asset_manifest_path"]).read_text(encoding="utf-8"))
    validate_artifact("asset_manifest", manifest)
    assert len(manifest["assets"]) == 1
    record = manifest["assets"][0]
    assert record["selection_status"] == "candidate"
    assert record["provenance"]["provider"] == "topview_manual"
    assert record["provenance"]["acquisition_mode"] == "manual_ui"
    assert record["provenance"]["actual_model_display_name"] == "TopView UI selected model"
    assert record["provenance"]["actual_ui_workspace"] == "BOARD"
    assert record["provenance"]["actual_tool_label"] == "AI Video"
    assert record["provenance"]["credits_charged"] == 12.5
    assert record["provenance"]["queue_mode"] == "STANDARD"
    settings_capture = record["provenance"]["settings_capture"]
    assert settings_capture["sha256"] == hashlib.sha256(
        b"topview-settings-capture"
    ).hexdigest()
    assert (project / settings_capture["path"]).read_bytes() == b"topview-settings-capture"
    assert record["sha256"] == _sha256(video)
    assert record["resolution"] == "320x180"
    assert video.exists()
    assert (project / record["path"]).is_file()


def test_same_checksum_is_idempotent_and_does_not_duplicate_manifest_record(tmp_path: Path) -> None:
    project, _, inbox = _prepared_project(tmp_path)
    video = inbox / "SHOT_002__candidate_A.mp4"
    _render_video(video)
    metadata_path = _operator_metadata(inbox, video.name)
    inputs = {
        "project_dir": str(project),
        "batch_id": "BATCH_001",
        "metadata_path": str(metadata_path),
    }

    first = _ingest_class()().execute(inputs)
    second = _ingest_class()().execute(inputs)
    manifest = json.loads(Path(second.data["asset_manifest_path"]).read_text(encoding="utf-8"))

    assert first.success is True
    assert second.success is True
    assert second.data["already_registered"] == ["SHOT_002__candidate_A.mp4"]
    assert len(manifest["assets"]) == 1


def test_unexpected_filename_is_rejected_without_moving_input(tmp_path: Path) -> None:
    project, _, inbox = _prepared_project(tmp_path)
    video = inbox / "WRONG_SHOT__candidate_A.mp4"
    _render_video(video)
    metadata_path = _operator_metadata(inbox, video.name)

    result = _ingest_class()().execute(
        {
            "project_dir": str(project),
            "batch_id": "BATCH_001",
            "metadata_path": str(metadata_path),
        }
    )

    assert result.success is False
    assert "filename does not match shot_id" in (result.error or "")
    assert video.exists()
    assert Path(result.data["rejection_report_path"]).is_file()


def test_corrupt_expected_video_is_rejected_with_probe_reason(tmp_path: Path) -> None:
    project, _, inbox = _prepared_project(tmp_path)
    video = inbox / "SHOT_002__candidate_A.mp4"
    video.write_bytes(b"not-a-video")
    metadata_path = _operator_metadata(inbox, video.name)

    result = _ingest_class()().execute(
        {
            "project_dir": str(project),
            "batch_id": "BATCH_001",
            "metadata_path": str(metadata_path),
        }
    )

    assert result.success is False
    assert "ffprobe" in (result.error or "")
    assert video.exists()
    report = json.loads(Path(result.data["rejection_report_path"]).read_text(encoding="utf-8"))
    assert report["status"] == "rejected"
    assert report["input_preserved"] is True
