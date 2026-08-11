from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess


FACTORY_ROOT = Path(__file__).resolve().parents[2]
ACTIVATE_SCRIPT = FACTORY_ROOT / "scripts" / "activate-youtube-factory.sh"


def _activated_environment() -> dict[str, str]:
    command = (
        f'source "{ACTIVATE_SCRIPT}" >/dev/null && '
        "python - <<'PY'\n"
        "import json, os\n"
        "keys = ['FACTORY_ROOT', 'OPENMONTAGE_PROJECTS_DIR', 'OPENMONTAGE_CACHE_DIR', "
        "'MEDIA_CACHE_DIR', 'MUSIC_LIBRARY_DIR', 'TOPVIEW_HANDOFF_ROOT', 'VIRTUAL_ENV', 'PATH']\n"
        "print(json.dumps({key: os.environ.get(key, '') for key in keys}))\n"
        "PY"
    )
    completed = subprocess.run(
        ["/bin/zsh", "-c", command],
        cwd=FACTORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONNOUSERSITE": "1"},
    )
    return json.loads(completed.stdout.strip().splitlines()[-1])


def test_activation_keeps_all_generated_state_inside_factory() -> None:
    env = _activated_environment()

    assert Path(env["FACTORY_ROOT"]).resolve() == FACTORY_ROOT
    assert Path(env["OPENMONTAGE_PROJECTS_DIR"]).resolve() == FACTORY_ROOT / "projects"
    assert Path(env["OPENMONTAGE_CACHE_DIR"]).resolve() == FACTORY_ROOT / ".runtime/clips_cache"
    assert Path(env["MEDIA_CACHE_DIR"]).resolve() == FACTORY_ROOT / ".runtime/media_cache"
    assert Path(env["MUSIC_LIBRARY_DIR"]).resolve() == FACTORY_ROOT / "music_library"
    assert Path(env["TOPVIEW_HANDOFF_ROOT"]).resolve() == FACTORY_ROOT / "projects"


def test_activation_uses_factory_owned_virtual_environment_first() -> None:
    env = _activated_environment()
    factory_venv = FACTORY_ROOT / ".venv"

    assert Path(env["VIRTUAL_ENV"]).resolve() == factory_venv
    assert Path(env["PATH"].split(os.pathsep)[0]).resolve() == factory_venv / "bin"


def test_environment_template_documents_local_and_optional_provider_settings() -> None:
    template = (FACTORY_ROOT / "config" / "youtube-factory.env.example").read_text(
        encoding="utf-8"
    )

    assert "OPENMONTAGE_PROJECTS_DIR=${FACTORY_ROOT}/projects" in template
    assert "OPENMONTAGE_CACHE_DIR=${FACTORY_ROOT}/.runtime/clips_cache" in template
    assert "MEDIA_CACHE_DIR=${FACTORY_ROOT}/.runtime/media_cache" in template
    assert "MUSIC_LIBRARY_DIR=${FACTORY_ROOT}/music_library" in template
    assert "COMFYUI_SERVER_URL=http://127.0.0.1:8188" in template
    assert "TOPVIEW_API" not in template

