from __future__ import annotations

from pathlib import Path

from backlot import server


def test_ffmpeg_discovery_uses_macos_install_when_service_path_is_minimal(
    tmp_path: Path, monkeypatch
) -> None:
    fake = tmp_path / "ffmpeg"
    fake.write_text("#!/bin/sh\n", encoding="utf-8")
    fake.chmod(0o755)
    monkeypatch.setenv("PATH", "/usr/bin:/bin:/usr/sbin:/sbin")
    monkeypatch.setattr(server, "FFMPEG_CANDIDATES", (fake,))

    assert server._ffmpeg_binary() == str(fake)
