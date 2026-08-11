#!/usr/bin/env python3
"""Regenerate project-local skill hashes and explicit factory routing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / ".agents" / "skills"
MANIFEST_PATH = ROOT / "vendor" / "skills" / "manifest.json"
ROUTING_PATH = ROOT / "config" / "factory-skill-routing.yaml"
TOOL_INVENTORY_PATH = ROOT / "config" / "tool-inventory.json"

sys.path.insert(0, str(ROOT))

from tools.tool_registry import ToolRegistry  # noqa: E402

HYPERFRAMES = {
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
REMOTION_OFFICIAL = {
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
REMOTION_REQUIRED = {
    "remotion-best-practices",
    "remotion-captions",
    "remotion-markup",
    "remotion-multimedia",
    "remotion-render",
    "remotion-upgrade",
}
REMOTION_REFERENCE_ONLY = {"remotion-create", "remotion-saas"}
IMPORTED_USER = {
    "beat-sync-editing",
    "color-motion",
    "diagram-animation",
    "isometric-animation",
    "kinetic-typography",
    "map-animation",
    "motion-art-direction",
    "shot-composition",
}
REQUIRED = {
    "ai-video-gen",
    "beat-sync-editing",
    "color-motion",
    "comfyui",
    "embedded-captions",
    "faceless-explainer",
    "ffmpeg",
    "flux-best-practices",
    "general-video",
    "hyperframes",
    "hyperframes-animation",
    "hyperframes-cli",
    "hyperframes-core",
    "hyperframes-creative",
    "hyperframes-keyframes",
    "hyperframes-registry",
    "kinetic-typography",
    "ltx2",
    "media-use",
    "motion-art-direction",
    "motion-graphics",
    "remotion",
    "remotion-best-practices",
    "remotion-captions",
    "remotion-markup",
    "remotion-multimedia",
    "remotion-render",
    "remotion-upgrade",
    "remotion-bits",
    "shot-composition",
    "sound-effects",
    "speech-to-text",
    "text-to-speech",
    "topview-manual-handoff",
    "video-download",
    "video-edit",
    "video-understand",
    "visual-style",
}
PROVIDER_DISABLED = {
    "avatar-video",
    "azure-speech-to-text",
    "bfl-api",
    "create-video",
    "dashscope",
    "doubao-tts",
    "elevenlabs",
    "faceswap",
    "gemini-omni",
    "grok-media",
    "heygen",
    "kling-official",
    "lyria",
    "seedance-2-0",
    "setup-api-key",
}
REFERENCE_ONLY = {
    "agents",
    "tailwind-design-system",
    "vercel-composition-patterns",
    "vercel-react-best-practices",
    "web-design-guidelines",
    *REMOTION_REFERENCE_ONLY,
}


def tree_sha256(directory: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        digest.update(path.relative_to(directory).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def explicit_license(skill_file: Path) -> str | None:
    match = re.search(
        r"(?m)^license:\s*['\"]?([^'\"\n]+)",
        skill_file.read_text(encoding="utf-8", errors="replace")[:5000],
    )
    return match.group(1).strip() if match else None


def origin_for(name: str) -> str:
    if name in REMOTION_OFFICIAL:
        return "remotion_official_current"
    if name in HYPERFRAMES:
        return "hyperframes_current"
    if name == "remotion-bits":
        return "remotion_bits_upstream"
    if name in IMPORTED_USER:
        return "user_existing_openmontage"
    if name == "topview-manual-handoff":
        return "youtube_factory"
    return "openmontage_baseline"


def license_for(name: str, skill_file: Path, origin: str) -> str:
    declared = explicit_license(skill_file)
    if declared:
        return f"declared in skill: {declared}"
    if origin == "hyperframes_current":
        return "Apache-2.0"
    if origin == "remotion_bits_upstream":
        return "project-local; upstream repository has no detected license"
    if origin == "remotion_official_current":
        return "project-local skill snapshot; upstream skills repository has no detected license"
    if origin == "youtube_factory":
        return "project-owned under repository license"
    if origin == "user_existing_openmontage":
        return "project-local; explicit license not found"
    return "OpenMontage AGPL-3.0 snapshot; upstream skill terms not individually asserted"


def routing_for(name: str) -> tuple[str, str, str, str]:
    if name == "topview-manual-handoff":
        return (
            "REQUIRED",
            "manual_ui_only",
            "OpenMontage Asset Director",
            "Prepare and recover human-operated TopView candidates without provider automation.",
        )
    if name == "embedded-captions":
        return (
            "REQUIRED_WITH_RESTRICTION",
            "local_or_knowledge",
            "MK Visual Director / HyperFrames",
            "Use the core caption workflow only; exclude PORTING.md and test-set examples while upstream issue #3219 remains open.",
        )
    if name in REMOTION_REQUIRED:
        return (
            "REQUIRED",
            "local_or_knowledge",
            "OpenMontage Edit/Compose",
            "Current official Remotion production guidance pinned with the 4.0.508 runtime.",
        )
    if name in REQUIRED:
        return (
            "REQUIRED",
            "local_or_knowledge",
            "MK Visual Director / OpenMontage",
            "Active factory capability; invoke only at the matching production stage.",
        )
    if name in PROVIDER_DISABLED:
        return (
            "DISABLED_BY_DEFAULT",
            "provider_api_disabled",
            "Human Gate",
            "Preserved for future opt-in use; never call or request a key without explicit approval.",
        )
    if name in REFERENCE_ONLY:
        return (
            "REFERENCE_ONLY",
            "knowledge_only",
            "Technical Director",
            "Retained as supporting knowledge, not part of the normal documentary route.",
        )
    return (
        "OPTIONAL",
        "local_or_knowledge",
        "MK Visual Director",
        "Use only when the approved shot design explicitly needs this specialty.",
    )


def tool_factory_status(info: dict) -> str:
    if info["provider"] == "topview_manual":
        return "MANUAL_BRIDGE"
    if info["provider"] == "selector":
        return "PLANNING_ONLY"
    if info["tier"] == "publish":
        return "HUMAN_GATE_ONLY"
    if any(str(item).startswith("env:") for item in info["dependencies"]):
        return "DISABLED_BY_DEFAULT"
    if info["resource_profile"]["network_required"]:
        return "EXPLICIT_OPT_IN"
    if info["runtime"] == "local":
        return "ACTIVE_LOCAL" if info["status"] == "available" else "LOCAL_SETUP_REQUIRED"
    return "OPTIONAL"


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["captured_at"] = "2026-08-11T23:10:00+09:00"
    manifest["sources"].update(
        {
            "openmontage_baseline": {
                "repository": "https://github.com/calesthio/OpenMontage.git",
                "commit": "4eab34c5cfcccaa4f1970554928feccce73ee930",
                "license": "AGPL-3.0",
            },
            "remotion_bits_upstream": {
                "repository": "https://github.com/av/remotion-bits.git",
                "commit": "6c71169aa061f15313fadbdc6e29a3a3a87f2c03",
                "license_status": "No detected repository license; keep project-local.",
            },
            "remotion_official_current": {
                "repository": "https://github.com/remotion-dev/skills.git",
                "commit": "b12104ef5f1b1ca2ca5590fcc7c1804fbc85556f",
                "license_status": "No detected repository license file; copied as a project-local instruction snapshot.",
                "runtime_version": "4.0.508",
            },
            "youtube_factory": {
                "path": ".agents/skills/topview-manual-handoff",
                "purpose": "Manual-only TopView work-order and result-recovery contract",
                "runtime_dependency_on_topview_api": False,
            },
        }
    )
    manifest["required_groups"]["factory_core"] = sorted(REQUIRED)
    manifest["required_groups"]["remotion_official_current"] = sorted(
        REMOTION_OFFICIAL
    )

    records = []
    routes = []
    for directory in sorted(path for path in SKILLS_ROOT.iterdir() if path.is_dir()):
        skill_file = directory / "SKILL.md"
        if not skill_file.is_file():
            continue
        name = directory.name
        origin = origin_for(name)
        records.append(
            {
                "name": name,
                "path": f".agents/skills/{name}",
                "origin": origin,
                "file_count": sum(1 for item in directory.rglob("*") if item.is_file()),
                "tree_sha256": tree_sha256(directory),
                "license_status": license_for(name, skill_file, origin),
            }
        )
        status, execution, owner, reason = routing_for(name)
        routes.append(
            {
                "name": name,
                "status": status,
                "execution": execution,
                "owner": owner,
                "reason": reason,
            }
        )

    manifest["skills"] = records
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    routing = {
        "schema_version": "1.0.0",
        "captured_at": "2026-08-11T23:10:00+09:00",
        "policy": {
            "paid_provider_skills": "disabled_by_default",
            "topview": "manual_ui_only",
            "publishing": "human_gate",
            "optional_skills": "invoke_only_from_approved_shot_design",
        },
        "skills": routes,
    }
    ROUTING_PATH.write_text(
        yaml.safe_dump(routing, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )

    registry = ToolRegistry()
    envelope = registry.support_envelope()
    tool_records = []
    for name in sorted(envelope):
        info = envelope[name]
        tool_records.append(
            {
                "name": name,
                "version": info["version"],
                "tier": info["tier"],
                "capability": info["capability"],
                "provider": info["provider"],
                "runtime": info["runtime"],
                "captured_status": info["status"],
                "stability": info["stability"],
                "dependencies": info["dependencies"],
                "agent_skills": info["agent_skills"],
                "network_required": info["resource_profile"]["network_required"],
                "factory_status": tool_factory_status(info),
            }
        )
    tool_inventory = {
        "schema_version": "1.0.0",
        "captured_at": "2026-08-11T23:10:00+09:00",
        "captured_environment": {
            "python": "3.11.15",
            "node": "26.5.0",
            "ffmpeg": "8.1.2",
            "credentials_loaded": False,
        },
        "policy": {
            "paid_or_credentialed": "DISABLED_BY_DEFAULT",
            "publish": "HUMAN_GATE_ONLY",
            "topview": "MANUAL_BRIDGE",
            "captured_status_is_not_approval": True,
        },
        "tool_count": len(tool_records),
        "tools": tool_records,
    }
    TOOL_INVENTORY_PATH.write_text(
        json.dumps(tool_inventory, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
