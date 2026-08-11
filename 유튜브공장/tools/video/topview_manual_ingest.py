"""Validate and ingest files produced through the manual TopView UI handoff."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
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


def _inside(parent: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(parent)
        return True
    except ValueError:
        return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_rate(value: str | None) -> float:
    if not value or value == "0/0":
        return 0.0
    numerator, separator, denominator = value.partition("/")
    if not separator:
        return float(numerator)
    denominator_value = float(denominator)
    return float(numerator) / denominator_value if denominator_value else 0.0


def _probe_video(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None, "ffprobe not found on PATH"
    completed = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    if completed.returncode != 0:
        reason = completed.stderr.strip() or "unreadable media"
        return None, f"ffprobe failed: {reason}"
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None, "ffprobe returned invalid JSON"
    video = next(
        (stream for stream in payload.get("streams", []) if stream.get("codec_type") == "video"),
        None,
    )
    if video is None:
        return None, "ffprobe found no video stream"
    try:
        duration = float(payload.get("format", {}).get("duration") or video.get("duration") or 0)
        width = int(video["width"])
        height = int(video["height"])
    except (KeyError, TypeError, ValueError):
        return None, "ffprobe returned incomplete video metadata"
    return (
        {
            "duration_seconds": round(duration, 3),
            "width": width,
            "height": height,
            "resolution": f"{width}x{height}",
            "fps": round(_parse_rate(video.get("avg_frame_rate") or video.get("r_frame_rate")), 3),
            "codec": video.get("codec_name"),
            "format_name": payload.get("format", {}).get("format_name"),
        },
        None,
    )


class TopViewManualIngest(BaseTool):
    name = "topview_manual_ingest"
    version = "1.1.0"
    tier = ToolTier.SOURCE
    capability = "video_generation"
    provider = "topview_manual"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.LOCAL

    dependencies = ["cmd:ffprobe"]
    install_instructions = "Install FFmpeg, then use TopView manually and place downloads in the batch inbox."
    capabilities = ["manual_result_ingest", "media_probe", "provenance_capture"]
    supports = {
        "manual_ui": True,
        "input_preservation": True,
        "candidate_only": True,
        "network_calls": False,
    }
    best_for = ["bringing human-selected TopView downloads back into OpenMontage safely"]
    not_good_for = ["automatic generation", "automatic asset approval"]
    input_schema = {
        "type": "object",
        "required": ["project_dir", "batch_id", "metadata_path"],
        "properties": {
            "project_dir": {"type": "string"},
            "batch_id": {"type": "string", "pattern": _ID.pattern},
            "metadata_path": {"type": "string"},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "asset_manifest_path": {"type": "string"},
            "registered": {"type": "array", "items": {"type": "string"}},
            "already_registered": {"type": "array", "items": {"type": "string"}},
            "rejection_report_path": {"type": "string"},
        },
    }
    resource_profile = ResourceProfile(
        cpu_cores=1,
        ram_mb=256,
        vram_mb=0,
        disk_mb=1000,
        network_required=False,
    )
    idempotency_key_fields = ["project_dir", "batch_id", "metadata_path"]
    side_effects = [
        "copies validated video into project candidate assets",
        "updates asset_manifest without selecting or approving assets",
        "writes rejection reports while preserving inbox files",
    ]
    agent_skills = ["topview-manual-handoff", "ffmpeg"]
    user_visible_verification = [
        "Review the candidate in Backlot before GATE_ASSET_SELECTION",
        "Confirm the disclosure label remains visible in the planned composite",
    ]

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        project_dir = Path(str(inputs.get("project_dir", ""))).expanduser().resolve()
        if not project_dir.is_dir():
            return ToolResult(success=False, error=f"project_dir not found: {project_dir}")
        batch_id = str(inputs.get("batch_id", ""))
        if not _ID.fullmatch(batch_id):
            return ToolResult(success=False, error=f"invalid batch_id: {batch_id}")

        inbox = (project_dir / "handoff" / "topview" / "inbox" / batch_id).resolve()
        if not inbox.is_dir():
            return ToolResult(success=False, error=f"batch inbox not found: {inbox}")

        metadata_input = Path(str(inputs.get("metadata_path", ""))).expanduser()
        metadata_path = (
            (project_dir / metadata_input).resolve()
            if not metadata_input.is_absolute()
            else metadata_input.resolve()
        )
        if not _inside(inbox, metadata_path):
            return ToolResult(success=False, error="metadata_path must be inside the batch inbox")
        if not metadata_path.is_file():
            return ToolResult(success=False, error=f"metadata_path not found: {metadata_path}")

        job_path = project_dir / "handoff" / "topview" / "outbox" / batch_id / "job.json"
        if not job_path.is_file():
            return ToolResult(success=False, error=f"job pack not found: {job_path}")
        try:
            job_pack = json.loads(job_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            validate_artifact("topview_job_pack", job_pack)
            validate_artifact("topview_operator_result", metadata)
        except Exception as exc:
            return ToolResult(success=False, error=f"invalid manual result metadata: {exc}")
        if metadata.get("batch_id") != batch_id or job_pack.get("batch_id") != batch_id:
            return ToolResult(success=False, error="batch_id does not match job pack and operator metadata")

        jobs = {job["shot_id"]: job for job in job_pack["jobs"]}
        prepared: list[tuple[Path, Path, Path, Path, dict[str, Any]]] = []
        seen_filenames: set[str] = set()
        for item in metadata["results"]:
            shot_id = item["shot_id"]
            filename = item["filename"]
            if filename in seen_filenames:
                return self._reject(
                    project_dir, batch_id, item, metadata["recorded_at"], "duplicate filename in operator metadata"
                )
            seen_filenames.add(filename)
            job = jobs.get(shot_id)
            if job is None:
                return self._reject(
                    project_dir, batch_id, item, metadata["recorded_at"], f"shot_id is not in job pack: {shot_id}"
                )
            filename_pattern = re.compile(
                rf"^{re.escape(shot_id)}__candidate_[A-Z]\.(mp4|mov|webm)$"
            )
            if not filename_pattern.fullmatch(filename):
                return self._reject(
                    project_dir,
                    batch_id,
                    item,
                    metadata["recorded_at"],
                    f"filename does not match shot_id {shot_id}: {filename}",
                )
            source = (inbox / filename).resolve()
            if not _inside(inbox, source) or not source.is_file():
                return self._reject(
                    project_dir, batch_id, item, metadata["recorded_at"], f"result file not found: {filename}"
                )

            capture_metadata = item["settings_capture"]
            capture_source = (inbox / capture_metadata["path"]).resolve()
            if not _inside(inbox, capture_source) or not capture_source.is_file():
                return self._reject(
                    project_dir,
                    batch_id,
                    item,
                    metadata["recorded_at"],
                    f"settings capture not found: {capture_metadata['path']}",
                )
            capture_checksum = _sha256(capture_source)
            if capture_checksum != capture_metadata["sha256"]:
                return self._reject(
                    project_dir,
                    batch_id,
                    item,
                    metadata["recorded_at"],
                    "settings capture checksum mismatch",
                )
            if item["actual_ui_workspace"] != job["ui_workspace"]:
                return self._reject(
                    project_dir,
                    batch_id,
                    item,
                    metadata["recorded_at"],
                    (
                        "workspace mismatch: expected "
                        f"{job['ui_workspace']}, got {item['actual_ui_workspace']}"
                    ),
                )

            probe, probe_error = _probe_video(source)
            if probe_error:
                return self._reject(
                    project_dir, batch_id, item, metadata["recorded_at"], probe_error
                )
            assert probe is not None
            if probe["resolution"] != job["resolution"]:
                return self._reject(
                    project_dir,
                    batch_id,
                    item,
                    metadata["recorded_at"],
                    f"resolution mismatch: expected {job['resolution']}, got {probe['resolution']}",
                )
            expected_duration = float(job["duration_seconds"])
            duration_tolerance = max(0.25, expected_duration * 0.1)
            if abs(float(probe["duration_seconds"]) - expected_duration) > duration_tolerance:
                return self._reject(
                    project_dir,
                    batch_id,
                    item,
                    metadata["recorded_at"],
                    f"duration mismatch: expected {expected_duration:g}s, got {probe['duration_seconds']:g}s",
                )

            checksum = _sha256(source)
            extension = source.suffix.lower()
            destination_rel = (
                Path("assets/candidates/topview")
                / batch_id
                / f"{shot_id}_{checksum[:16]}{extension}"
            )
            destination = project_dir / destination_rel
            capture_destination_rel = (
                Path("artifacts/provenance/topview")
                / batch_id
                / f"{shot_id}_settings_{capture_checksum[:16]}{capture_source.suffix.lower()}"
            )
            capture_destination = project_dir / capture_destination_rel
            max_credits = job["budget"]["max_credits"]
            charged_credits = item["credits_charged"]
            budget_within_limit = (
                None
                if max_credits is None or charged_credits is None
                else float(charged_credits) <= float(max_credits)
            )
            record = {
                "id": f"ASSET_{shot_id}_{checksum[:8].upper()}",
                "type": "video",
                "path": destination_rel.as_posix(),
                "source_tool": self.name,
                "scene_id": shot_id,
                "prompt": job["prompt"],
                "model": item["actual_model_display_name"],
                "cost_usd": 0,
                "duration_seconds": probe["duration_seconds"],
                "resolution": probe["resolution"],
                "format": extension.lstrip("."),
                "subtype": "generated_candidate",
                "generation_summary": item["generation_notes"],
                "provider": "topview_manual",
                "sha256": checksum,
                "selection_status": "candidate",
                "provenance": {
                    "provider": "topview_manual",
                    "acquisition_mode": "manual_ui",
                    "batch_id": batch_id,
                    "source_filename": filename,
                    "actual_ui_workspace": item["actual_ui_workspace"],
                    "actual_tool_label": item["actual_tool_label"],
                    "actual_model_display_name": item["actual_model_display_name"],
                    "queue_mode": item["queue_mode"],
                    "plan_tier": item["plan_tier"],
                    "credits_estimated_before_submit": item[
                        "credits_estimated_before_submit"
                    ],
                    "credits_charged": charged_credits,
                    "budget_within_limit": budget_within_limit,
                    "attempt_number": item["attempt_number"],
                    "submitted_at": item["submitted_at"],
                    "completed_at": item["completed_at"],
                    "provider_project_reference": item[
                        "provider_project_reference"
                    ],
                    "settings_capture": {
                        "path": capture_destination_rel.as_posix(),
                        "sha256": capture_checksum,
                    },
                    "generation_notes": item["generation_notes"],
                    "recorded_at": metadata["recorded_at"],
                    "job_pack_path": job_path.relative_to(project_dir).as_posix(),
                },
            }
            prepared.append(
                (
                    source,
                    destination,
                    capture_source,
                    capture_destination,
                    record,
                )
            )

        manifest_path = project_dir / "artifacts" / "asset_manifest.json"
        if manifest_path.is_file():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                validate_artifact("asset_manifest", manifest)
            except Exception as exc:
                return ToolResult(success=False, error=f"existing asset_manifest is invalid: {exc}")
        else:
            manifest = {"version": "1.0", "assets": [], "total_cost_usd": 0, "metadata": {}}

        existing_hashes = {asset.get("sha256") for asset in manifest["assets"]}
        registered: list[str] = []
        already_registered: list[str] = []
        for source, destination, capture_source, capture_destination, record in prepared:
            source_filename = record["provenance"]["source_filename"]
            if record["sha256"] in existing_hashes:
                already_registered.append(source_filename)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            capture_destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(capture_source, capture_destination)
            manifest["assets"].append(record)
            existing_hashes.add(record["sha256"])
            registered.append(source_filename)

        manifest["metadata"] = {
            **manifest.get("metadata", {}),
            "asset_selection_gate": "required",
            "candidate_count": sum(
                1 for asset in manifest["assets"] if asset.get("selection_status") == "candidate"
            ),
        }
        try:
            validate_artifact("asset_manifest", manifest)
        except Exception as exc:
            return ToolResult(success=False, error=f"updated asset_manifest failed validation: {exc}")

        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_manifest = manifest_path.with_suffix(".json.tmp")
        temporary_manifest.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary_manifest.replace(manifest_path)
        return ToolResult(
            success=True,
            data={
                "asset_manifest_path": str(manifest_path),
                "registered": registered,
                "already_registered": already_registered,
                "selection_status": "candidate",
                "next_gate": "GATE_ASSET_SELECTION",
            },
            artifacts=[str(manifest_path)]
            + [str(item[1]) for item in prepared]
            + [str(item[3]) for item in prepared],
            cost_usd=0.0,
        )

    @staticmethod
    def _reject(
        project_dir: Path,
        batch_id: str,
        item: dict[str, Any],
        recorded_at: str,
        reason: str,
    ) -> ToolResult:
        safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.get("filename", "unknown"))
        report_path = (
            project_dir
            / "handoff"
            / "topview"
            / "rejections"
            / batch_id
            / f"{safe_name}.json"
        )
        report = {
            "schema_version": "1.0.0",
            "status": "rejected",
            "batch_id": batch_id,
            "shot_id": item.get("shot_id"),
            "filename": item.get("filename"),
            "reason": reason,
            "recorded_at": recorded_at,
            "input_preserved": True,
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return ToolResult(
            success=False,
            data={"rejection_report_path": str(report_path)},
            artifacts=[str(report_path)],
            error=reason,
            cost_usd=0.0,
        )
