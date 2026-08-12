from __future__ import annotations

import shutil
import subprocess

import pytest

from tools.video.media_visual_evidence import build_visual_evidence, classify_frames


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg unavailable")
def test_video_visual_evidence_samples_first_middle_last(tmp_path) -> None:
    video = tmp_path / "fixture.mp4"
    subprocess.run(
        [
            "ffmpeg", "-loglevel", "error", "-f", "lavfi", "-i",
            "color=c=blue:s=160x90:d=3", "-pix_fmt", "yuv420p", "-y", str(video),
        ],
        check=True,
    )
    result = build_visual_evidence(video, tmp_path / "frames")
    assert result["status"] == "sampled"
    assert {"first", "middle", "last"}.issubset(set(result["sample_roles"]))
    assert all((tmp_path / "frames" / name).exists() for name in result["frame_files"])


def test_image_is_recorded_as_a_single_local_sample(tmp_path) -> None:
    image = tmp_path / "image.jpg"
    image.write_bytes(b"fixture")
    result = build_visual_evidence(image, tmp_path / "frames")
    assert result["status"] == "sampled"
    assert result["sample_roles"] == ["still"]
    assert result["frame_files"] == [str(image.resolve())]


def test_unavailable_local_model_returns_unavailable_not_positive() -> None:
    result = classify_frames([], model_loader=lambda: None)
    assert result == {"status": "unavailable", "labels": [], "confidence": None}
