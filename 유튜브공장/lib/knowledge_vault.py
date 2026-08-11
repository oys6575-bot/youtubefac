"""Project-local Obsidian knowledge for the isolated YouTube Factory.

Canonical registries remain authoritative. This module only materializes and retrieves
local knowledge; it never calls a provider, changes a checkpoint, or grants approval.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlsplit

import yaml

from lib.visual_technique_registry import load_registry


FACTORY_ROOT = Path(__file__).resolve().parents[1]
_MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")


class KnowledgeVaultError(ValueError):
    """Raised when canonical knowledge cannot be loaded or safely resolved."""


@dataclass(frozen=True)
class ResearchLink:
    title: str
    url: str
    host: str
    evidence_class: str
    source_document: str


@dataclass(frozen=True)
class KnowledgeSources:
    project_root: Path
    catalog_version: str
    techniques: tuple[dict[str, Any], ...]
    skills: tuple[dict[str, Any], ...]
    tools: tuple[dict[str, Any], ...]
    creative_sources: tuple[dict[str, Any], ...]
    research_links: tuple[ResearchLink, ...]
    local_models: tuple[dict[str, Any], ...]
    toolchain: tuple[dict[str, Any], ...]
    topview_capabilities: tuple[dict[str, Any], ...]
    topview_models: tuple[dict[str, Any], ...]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeVaultError(f"Cannot load JSON knowledge source {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeVaultError(f"Knowledge source must be an object: {path}")
    return payload


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise KnowledgeVaultError(f"Cannot load YAML knowledge source {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeVaultError(f"Knowledge source must be an object: {path}")
    return payload


def _load_research_links(project_root: Path) -> tuple[ResearchLink, ...]:
    links: list[ResearchLink] = []
    seen: set[str] = set()
    for document in sorted((project_root / "docs" / "research").glob("*.md")):
        text = document.read_text(encoding="utf-8")
        for title, raw_url in _MARKDOWN_LINK.findall(text):
            url = raw_url.strip()
            normalized = url.rstrip("/")
            if normalized in seen:
                continue
            seen.add(normalized)
            host = (urlsplit(url).hostname or "").lower()
            links.append(
                ResearchLink(
                    title=title.strip(),
                    url=url,
                    host=host,
                    evidence_class=(
                        "ANECDOTAL_SIGNAL"
                        if host in {"reddit.com", "www.reddit.com"}
                        else "CITED_REFERENCE"
                    ),
                    source_document=document.relative_to(project_root).as_posix(),
                )
            )
    return tuple(links)


def load_knowledge_sources(*, root: Path = FACTORY_ROOT) -> KnowledgeSources:
    """Load and normalize every explicit project-local knowledge inventory."""

    project_root = Path(root).resolve()
    registry = load_registry(project_root / "config" / "visual-technique-registry.yaml")
    skill_routing = _read_yaml(project_root / "config" / "factory-skill-routing.yaml")
    skill_manifest = _read_json(project_root / "vendor" / "skills" / "manifest.json")
    tool_inventory = _read_json(project_root / "config" / "tool-inventory.json")
    creative_manifest = _read_json(
        project_root / "vendor" / "creative-sources" / "manifest.json"
    )
    local_models = _read_json(project_root / "config" / "local-models.lock.json")
    toolchain = _read_json(project_root / "config" / "toolchain-lock.json")
    topview = _read_yaml(project_root / "config" / "topview-capabilities.yaml")

    routed_skills = {item["name"]: item for item in skill_routing.get("skills", [])}
    manifested_skills = {item["name"]: item for item in skill_manifest.get("skills", [])}
    if routed_skills.keys() != manifested_skills.keys():
        routing_only = sorted(routed_skills.keys() - manifested_skills.keys())
        manifest_only = sorted(manifested_skills.keys() - routed_skills.keys())
        raise KnowledgeVaultError(
            "Skill inventories disagree: "
            f"routing_only={routing_only}, manifest_only={manifest_only}"
        )

    skills = tuple(
        {**manifested_skills[name], **routed_skills[name]}
        for name in sorted(routed_skills)
    )
    toolchain_records = tuple(
        {"name": name, **record}
        for name, record in toolchain.get("tools", {}).items()
    )
    topview_capabilities = tuple(
        {"group": group, **record}
        for group, records in topview.get("capability_groups", {}).items()
        for record in records
    )
    topview_models = tuple(
        {"media_type": media_type, **record}
        for media_type, records in topview.get("model_families", {}).items()
        for record in records
    )

    return KnowledgeSources(
        project_root=project_root,
        catalog_version=str(registry["catalog_version"]),
        techniques=tuple(registry.get("techniques", [])),
        skills=skills,
        tools=tuple(tool_inventory.get("tools", [])),
        creative_sources=tuple(creative_manifest.get("sources", [])),
        research_links=_load_research_links(project_root),
        local_models=tuple(local_models.get("models", [])),
        toolchain=toolchain_records,
        topview_capabilities=topview_capabilities,
        topview_models=topview_models,
    )

