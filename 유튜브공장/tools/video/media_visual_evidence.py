"""Local-only representative frame evidence without automatic model downloads."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
from typing import Callable


_VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".ogv", ".m4v"}
_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}


def _duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "json", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def build_visual_evidence(media_path: str | Path, frame_dir: str | Path) -> dict:
    """Freeze deterministic still/video samples; never infer event identity."""
    path = Path(media_path).resolve()
    suffix = path.suffix.lower()
    if suffix in _IMAGE_SUFFIXES:
        return {
            "status": "sampled",
            "sample_roles": ["still"],
            "frame_files": [str(path)],
            "labels": [],
            "confidence": None,
        }
    if suffix not in _VIDEO_SUFFIXES or not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        return {
            "status": "unavailable",
            "sample_roles": [],
            "frame_files": [],
            "labels": [],
            "confidence": None,
        }

    destination = Path(frame_dir)
    destination.mkdir(parents=True, exist_ok=True)
    duration = max(_duration(path), 0.1)
    times = {
        "first": min(0.05, duration / 4),
        "middle": duration / 2,
        "last": max(duration - 0.05, duration * 0.75),
    }
    frame_files = []
    for role, timestamp in times.items():
        output = destination / f"{path.stem}-{role}.jpg"
        subprocess.run(
            [
                "ffmpeg", "-loglevel", "error", "-ss", f"{timestamp:.3f}",
                "-i", str(path), "-frames:v", "1", "-q:v", "2", "-y", str(output),
            ],
            check=True,
        )
        frame_files.append(output.name)
    return {
        "status": "sampled",
        "sample_roles": list(times),
        "frame_files": frame_files,
        "labels": [],
        "confidence": None,
    }


def classify_frames(
    frame_paths: list[str | Path],
    *,
    model_loader: Callable[[], object | None],
) -> dict:
    """Use an already-installed local classifier or fail closed without downloading."""
    model = model_loader()
    if model is None or not frame_paths:
        return {"status": "unavailable", "labels": [], "confidence": None}
    if hasattr(model, "classify"):
        value = model.classify([str(Path(path)) for path in frame_paths])
    elif callable(model):
        value = model([str(Path(path)) for path in frame_paths])
    else:
        return {"status": "unavailable", "labels": [], "confidence": None}
    labels = list(value.get("labels", []))
    confidence = value.get("confidence")
    return {"status": "classified", "labels": labels, "confidence": confidence}
