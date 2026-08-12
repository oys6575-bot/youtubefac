from __future__ import annotations

import json
from pathlib import Path
import subprocess


FACTORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_LOCK = FACTORY_ROOT / "vendor" / "openmontage" / "source-lock.json"


def test_factory_source_lock_pins_clean_upstream() -> None:
    lock = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))

    assert lock["repository"] == "https://github.com/calesthio/OpenMontage.git"
    assert lock["commit"] == "4eab34c5cfcccaa4f1970554928feccce73ee930"
    assert lock["license"] == "AGPL-3.0"
    assert lock["import_method"] == "git archive"
    assert lock["tracked_file_count"] == 2038


def test_factory_tree_excludes_existing_runtime_material_and_protects_local_env() -> None:
    forbidden = [
        FACTORY_ROOT / "pexels_6684209.jpg",
        FACTORY_ROOT / "projects" / "aurora",
    ]

    assert [str(path.relative_to(FACTORY_ROOT)) for path in forbidden if path.exists()] == []

    env_path = FACTORY_ROOT / ".env"
    if env_path.exists():
        assert env_path.stat().st_mode & 0o777 == 0o600
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", ".env"],
            cwd=FACTORY_ROOT,
            check=False,
        )
        assert ignored.returncode == 0

    venv_config = (FACTORY_ROOT / ".venv" / "pyvenv.cfg").read_text(encoding="utf-8")
    assert "/Users/mk-macbook/Desktop/openmontage" not in venv_config


def test_factory_git_index_does_not_track_runtime_or_secrets() -> None:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=FACTORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = completed.stdout.splitlines()
    forbidden_parts = {
        ".env",
        ".venv",
        "node_modules",
        ".cache",
        ".remotion",
        ".runtime",
        "tmp",
    }

    assert [path for path in tracked if forbidden_parts.intersection(Path(path).parts)] == []


def test_factory_gitignore_covers_generated_runtime_boundaries() -> None:
    ignored = {
        line.strip()
        for line in (FACTORY_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert {
        ".env",
        ".venv/",
        ".runtime/",
        ".cache/",
        ".remotion/",
        ".superpowers/",
        "tmp/",
        "remotion-composer/node_modules/",
        "projects/*",
    }.issubset(ignored)
