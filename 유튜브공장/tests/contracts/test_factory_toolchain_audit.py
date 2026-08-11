from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from tools.tool_registry import ToolRegistry


ROOT = Path(__file__).resolve().parents[2]


def _tree_sha256(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        digest.update(path.relative_to(directory).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def test_toolchain_lock_covers_every_active_factory_runtime() -> None:
    lock = json.loads((ROOT / "config/toolchain-lock.json").read_text(encoding="utf-8"))
    tools = lock["tools"]

    assert lock["schema_version"] == "1.0.0"
    assert lock["topview_policy"] == {
        "integration_mode": "manual_ui",
        "api_allowed": False,
        "mcp_allowed": False,
        "browser_automation_allowed": False,
    }
    assert tools["openmontage"]["commit"] == "4eab34c5cfcccaa4f1970554928feccce73ee930"
    assert tools["hyperframes"]["version"] == "0.7.106"
    assert tools["remotion"]["version"] == "4.0.508"
    assert tools["comfyui"]["commit"] == "43cb4fffc89bba20ab7bd61467a36d0339338dab"
    assert tools["ffmpeg"]["verified_version"] == "8.1.2"
    assert tools["yt-dlp"]["verified_version"] == "2026.07.04"


def test_local_model_lock_uses_exact_hugging_face_revisions_and_license_gates() -> None:
    lock = json.loads((ROOT / "config/local-models.lock.json").read_text(encoding="utf-8"))
    models = {item["id"]: item for item in lock["models"]}

    assert models["Lightricks/LTX-2.3"]["revision"] == (
        "6f3520585aa27248020550da2f453aa0c572398c"
    )
    assert models["Lightricks/LTX-2.3"]["default_route"] == "LOCAL_LTX"
    assert models["Lightricks/LTX-2.3"]["license_review_required"] is True
    assert models["Wan-AI/Wan2.2-I2V-A14B"]["revision"] == (
        "206a9ee1b7bfaaf8f7e4d81335650533490646a3"
    )
    assert models["black-forest-labs/FLUX.2-klein-4B"]["revision"] == (
        "e7b7dc27f91deacad38e78976d1f2b499d76a294"
    )
    assert lock["download_policy"]["weights_bundled_in_git"] is False
    assert lock["download_policy"]["exact_revision_required"] is True


def test_topview_catalog_is_comprehensive_but_all_execution_stays_manual() -> None:
    catalog = yaml.safe_load(
        (ROOT / "config/topview-capabilities.yaml").read_text(encoding="utf-8")
    )

    assert catalog["policy"]["integration_mode"] == "manual_ui"
    assert catalog["policy"]["prohibited"] == [
        "api_submission",
        "mcp_submission",
        "browser_click_automation",
        "automatic_billing",
        "automatic_asset_approval",
    ]
    groups = catalog["capability_groups"]
    assert {
        "workspaces",
        "video",
        "image",
        "audio",
        "avatar",
        "three_d",
        "collaboration",
        "marketing",
        "automation_surfaces",
    } <= groups.keys()
    automation = {item["id"]: item for item in groups["automation_surfaces"]}
    assert automation["topview_api"]["factory_status"] == "PROHIBITED"
    assert automation["topview_mcp"]["factory_status"] == "PROHIBITED"
    assert automation["topview_official_skill"]["factory_status"] == "REFERENCE_ONLY"
    assert catalog["operator_requirements"]["record_exact_ui_model_label"] is True
    assert catalog["operator_requirements"]["capture_cost_before_submit"] is True


def test_every_project_agent_skill_is_hash_locked_and_routed() -> None:
    manifest = json.loads(
        (ROOT / "vendor/skills/manifest.json").read_text(encoding="utf-8")
    )
    routing = yaml.safe_load(
        (ROOT / "config/factory-skill-routing.yaml").read_text(encoding="utf-8")
    )
    records = {item["name"]: item for item in manifest["skills"]}
    route_records = {item["name"]: item for item in routing["skills"]}
    skill_dirs = {
        path.name
        for path in (ROOT / ".agents/skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }

    assert skill_dirs == records.keys()
    assert skill_dirs == route_records.keys()
    assert route_records["topview-manual-handoff"]["status"] == "REQUIRED"
    assert route_records["topview-manual-handoff"]["execution"] == "manual_ui_only"
    assert route_records["setup-api-key"]["status"] == "DISABLED_BY_DEFAULT"
    assert route_records["remotion-render"]["status"] == "REQUIRED"
    assert route_records["remotion-create"]["status"] == "REFERENCE_ONLY"
    assert route_records["embedded-captions"]["status"] == (
        "REQUIRED_WITH_RESTRICTION"
    )
    assert manifest["sources"]["remotion_official_current"]["commit"] == (
        "b12104ef5f1b1ca2ca5590fcc7c1804fbc85556f"
    )

    for name, record in records.items():
        directory = ROOT / record["path"]
        assert _tree_sha256(directory) == record["tree_sha256"], name


def test_vendored_comfyui_source_is_exact_and_has_local_video_blueprints() -> None:
    lock = json.loads(
        (ROOT / "vendor/comfyui/source-lock.json").read_text(encoding="utf-8")
    )
    source = ROOT / lock["path"]

    assert lock["repository"] == "https://github.com/Comfy-Org/ComfyUI.git"
    assert lock["release"] == "v0.31.0"
    assert lock["commit"] == "43cb4fffc89bba20ab7bd61467a36d0339338dab"
    assert lock["license"] == "GPL-3.0"
    assert (source / "main.py").is_file()
    assert (source / "LICENSE").is_file()
    archive_files = [
        path
        for path in source.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
        and path.suffix != ".pyc"
    ]
    assert len(archive_files) == lock["file_count"]
    blueprint_root = source / "blueprints"
    for name, expected in lock["required_blueprints"].items():
        assert hashlib.sha256((blueprint_root / name).read_bytes()).hexdigest() == expected
    assert list(source.rglob("*LTX*2*3*.json")) or list(source.rglob("*ltx*2*3*.json"))
    assert list(source.rglob("*Wan*2*2*.json")) or list(source.rglob("*wan*2*2*.json"))


def test_comfyui_runtime_scripts_are_project_local_and_mps_guarded() -> None:
    bootstrap = (ROOT / "scripts/bootstrap-comfyui.sh").read_text(encoding="utf-8")
    start = (ROOT / "scripts/start-comfyui.sh").read_text(encoding="utf-8")
    paths = (ROOT / "config/comfyui-extra-model-paths.yaml").read_text(encoding="utf-8")

    assert "vendor/comfyui/src" in bootstrap
    assert ".runtime/venvs/comfyui" in bootstrap
    assert "--extra-model-paths-config" in start
    assert "PYTORCH_ENABLE_MPS_FALLBACK=1" in start
    assert "--listen 127.0.0.1" in start
    assert ".runtime/models/comfyui" in paths
    assert "fp8" in start.lower()


def test_remotion_packages_are_exactly_aligned() -> None:
    package = json.loads(
        (ROOT / "remotion-composer/package.json").read_text(encoding="utf-8")
    )
    versions = {
        version
        for name, version in package["dependencies"].items()
        if name == "remotion" or name.startswith("@remotion/")
    }

    assert versions == {"4.0.508"}


def test_every_registered_tool_is_in_the_factory_inventory() -> None:
    inventory = json.loads(
        (ROOT / "config/tool-inventory.json").read_text(encoding="utf-8")
    )
    inventory_tools = {item["name"]: item for item in inventory["tools"]}
    registry = ToolRegistry()
    registry.discover()

    assert set(registry.list_all()) == inventory_tools.keys()
    assert inventory["policy"]["paid_or_credentialed"] == "DISABLED_BY_DEFAULT"
    assert inventory_tools["topview_manual_handoff"]["factory_status"] == "MANUAL_BRIDGE"
    assert inventory_tools["topview_manual_ingest"]["factory_status"] == "MANUAL_BRIDGE"
    assert inventory_tools["topview_manual_handoff"]["network_required"] is False
