from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts.orca.provision_role_env import (
    ProvisionError,
    merge_allowed_secret,
    provision_role_env,
)


def test_research_receives_only_youtube_key(tmp_path: Path) -> None:
    source = tmp_path / "source.env"
    target = tmp_path / "research.env"
    source.write_text(
        "YOUTUBE_API_KEY=youtube-secret\n"
        "PEXELS_API_KEY=pexels-secret\n"
        "PIXABAY_API_KEY=pixabay-secret\n",
        encoding="utf-8",
    )

    status = provision_role_env(
        "research",
        source,
        target,
        runtime_values={"OPENMONTAGE_PROJECTS_DIR": "/factory/projects"},
    )

    assert status == {
        "role": "research",
        "keys_present": ["YOUTUBE_API_KEY"],
        "runtime_keys": ["OPENMONTAGE_PROJECTS_DIR"],
    }
    assert target.read_text(encoding="utf-8") == (
        "OPENMONTAGE_PROJECTS_DIR=/factory/projects\n"
        "YOUTUBE_API_KEY=youtube-secret\n"
    )
    assert os.stat(target).st_mode & 0o777 == 0o600


def test_production_receives_only_stock_keys(tmp_path: Path) -> None:
    source = tmp_path / "source.env"
    target = tmp_path / "production.env"
    source.write_text(
        "YOUTUBE_API_KEY=youtube-secret\n"
        "PEXELS_API_KEY=pexels-secret\n"
        "PIXABAY_API_KEY=pixabay-secret\n"
        "UNSPLASH_ACCESS_KEY=unsplash-secret\n",
        encoding="utf-8",
    )

    status = provision_role_env("production", source, target)

    assert status["keys_present"] == [
        "PEXELS_API_KEY",
        "PIXABAY_API_KEY",
        "UNSPLASH_ACCESS_KEY",
    ]
    text = target.read_text(encoding="utf-8")
    assert "YOUTUBE_API_KEY" not in text
    assert "pexels-secret" in text
    assert "pixabay-secret" in text
    assert "unsplash-secret" in text


@pytest.mark.parametrize("role", ["control", "verification", "story_visual", "qa"])
def test_secretless_roles_get_empty_private_env(tmp_path: Path, role: str) -> None:
    source = tmp_path / "source.env"
    target = tmp_path / f"{role}.env"
    source.write_text("YOUTUBE_API_KEY=secret\n", encoding="utf-8")

    status = provision_role_env(role, source, target)

    assert status == {"role": role, "keys_present": [], "runtime_keys": []}
    assert target.read_text(encoding="utf-8") == ""
    assert os.stat(target).st_mode & 0o777 == 0o600


def test_unknown_role_and_missing_required_key_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "source.env"
    source.write_text("", encoding="utf-8")

    with pytest.raises(ProvisionError, match="unknown role"):
        provision_role_env("admin", source, tmp_path / "admin.env")
    with pytest.raises(ProvisionError, match="YOUTUBE_API_KEY"):
        provision_role_env("research", source, tmp_path / "research.env")
    with pytest.raises(ProvisionError, match="runtime key"):
        provision_role_env(
            "control",
            source,
            tmp_path / "control.env",
            runtime_values={"PATH": "/unsafe"},
        )


def test_merge_allowed_secret_preserves_existing_keys_without_printing_value(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.env"
    target = tmp_path / "target.env"
    source.write_text("YOUTUBE_API_KEY=youtube-secret\n", encoding="utf-8")
    target.write_text("PEXELS_API_KEY=pexels-secret\n", encoding="utf-8")

    status = merge_allowed_secret(source, target, "YOUTUBE_API_KEY")

    assert status == {"key": "YOUTUBE_API_KEY", "present": True}
    values = target.read_text(encoding="utf-8")
    assert "YOUTUBE_API_KEY=youtube-secret" in values
    assert "PEXELS_API_KEY=pexels-secret" in values
    assert os.stat(target).st_mode & 0o777 == 0o600


def test_merge_rejects_non_allowlisted_secret_name(tmp_path: Path) -> None:
    source = tmp_path / "source.env"
    target = tmp_path / "target.env"
    source.write_text("ADMIN_TOKEN=secret\n", encoding="utf-8")

    with pytest.raises(ProvisionError, match="not allowlisted"):
        merge_allowed_secret(source, target, "ADMIN_TOKEN")
