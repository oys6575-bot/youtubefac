from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "vendor" / "skills" / "manifest.json"

HYPERFRAMES_SKILLS = {
    "embedded-captions",
    "faceless-explainer",
    "general-video",
    "hyperframes",
    "hyperframes-animation",
    "hyperframes-cli",
    "hyperframes-core",
    "hyperframes-creative",
    "hyperframes-keyframes",
    "hyperframes-registry",
    "media-use",
    "motion-graphics",
    "music-to-video",
    "remotion-to-hyperframes",
}

USER_SKILLS = {
    "beat-sync-editing",
    "color-motion",
    "diagram-animation",
    "isometric-animation",
    "kinetic-typography",
    "map-animation",
    "motion-art-direction",
    "remotion-bits",
    "shot-composition",
}

FACTORY_SKILLS = {"topview-manual-handoff"}

REMOTION_OFFICIAL_SKILLS = {
    "remotion-best-practices",
    "remotion-captions",
    "remotion-create",
    "remotion-docs",
    "remotion-interactivity",
    "remotion-maps",
    "remotion-markup",
    "remotion-multimedia",
    "remotion-render",
    "remotion-saas",
    "remotion-studio",
    "remotion-upgrade",
}


def _tree_sha256(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        relative = path.relative_to(directory).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def test_skill_inventory_is_project_local_complete_and_hash_locked() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest["policy"] == {
        "project_local_only": True,
        "symlinks_allowed": False,
        "topview_api_skill_included": False,
    }
    assert set(manifest["required_groups"]["hyperframes_current"]) == HYPERFRAMES_SKILLS
    assert set(manifest["required_groups"]["imported_user_skills"]) == USER_SKILLS
    assert set(manifest["required_groups"]["remotion_official_current"]) == (
        REMOTION_OFFICIAL_SKILLS
    )

    records = {record["name"]: record for record in manifest["skills"]}
    assert (
        HYPERFRAMES_SKILLS
        | USER_SKILLS
        | FACTORY_SKILLS
        | REMOTION_OFFICIAL_SKILLS
        <= records.keys()
    )

    for name in HYPERFRAMES_SKILLS | USER_SKILLS | FACTORY_SKILLS:
        record = records[name]
        directory = ROOT / record["path"]
        assert directory.is_dir(), name
        assert (directory / "SKILL.md").is_file(), name
        assert not any(path.is_symlink() for path in directory.rglob("*")), name
        assert _tree_sha256(directory) == record["tree_sha256"], name


def test_factory_core_skills_and_topview_manual_boundary_are_explicit() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    core = manifest["required_groups"]["factory_core"]

    for name in core:
        assert (ROOT / ".agents" / "skills" / name / "SKILL.md").is_file(), name

    all_names = {path.name.lower() for path in (ROOT / ".agents" / "skills").iterdir()}
    assert "topview" not in all_names
    assert "topview-api" not in all_names
    assert "topview-generate" not in all_names
    assert "topview-manual-handoff" in all_names
    assert manifest["integration_modes"]["topview"] == "manual_ui"
    assert manifest["integration_modes"]["topview_submission"] == "human_only"
