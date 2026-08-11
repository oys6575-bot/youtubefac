"""Project-local Obsidian knowledge for the isolated YouTube Factory.

Canonical registries remain authoritative. This module only materializes and retrieves
local knowledge; it never calls a provider, changes a checkpoint, or grants approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping
from urllib.parse import urlsplit

import yaml

from lib.visual_technique_registry import load_registry


FACTORY_ROOT = Path(__file__).resolve().parents[1]
_MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")
_USER_NOTES = re.compile(
    r"<!-- USER-NOTES:BEGIN -->(.*?)<!-- USER-NOTES:END -->", re.DOTALL
)
_WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
_TOKEN = re.compile(r"[0-9a-z가-힣_]+", re.IGNORECASE)


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


@dataclass(frozen=True)
class SyncReport:
    """Result of one non-destructive vault materialization."""

    created: int
    updated: int
    unchanged: int
    entity_cards: int
    entity_counts: dict[str, int]
    orphans: tuple[str, ...]


@dataclass(frozen=True)
class _Card:
    card_id: str
    entity_type: str
    title: str
    status: str
    relative_path: Path
    frontmatter: Mapping[str, Any]
    sections: tuple[tuple[str, str], ...]
    related_ids: tuple[str, ...] = ()


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


def _slug(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z가-힣._-]+", "-", value.strip())
    cleaned = re.sub(r"-+", "-", cleaned).strip("-.")
    return cleaned or "unnamed"


def _status_folder(value: str) -> str:
    return _slug(value.lower().replace("_", "-"))


def _json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2) + "\n```"


def _bullet_list(values: Iterable[Any]) -> str:
    items = [str(value) for value in values]
    return "\n".join(f"- {item}" for item in items) if items else "_None recorded._"


def _source_skill(path: str) -> str | None:
    parts = Path(path).parts
    if len(parts) >= 3 and parts[:2] == (".agents", "skills"):
        return parts[2]
    return None


def _research_bucket(host: str) -> str:
    if host in {"reddit.com", "www.reddit.com"}:
        return "reddit-signals"
    if host == "github.com":
        return "github"
    if host in {"huggingface.co", "www.huggingface.co"}:
        return "hugging-face"
    return "official-sites"


def _common_frontmatter(
    *, card_id: str, entity_type: str, title: str, status: str
) -> dict[str, Any]:
    return {
        "card_id": card_id,
        "type": entity_type,
        "title": title,
        "status": status,
        "knowledge_schema": "1.0",
        "generated": True,
    }


def _build_cards(sources: KnowledgeSources) -> tuple[list[_Card], dict[str, int]]:
    cards: list[_Card] = []
    counts: dict[str, int] = {}
    skill_names = {str(item["name"]) for item in sources.skills}
    creative_by_url = {
        str(item.get("url", "")).rstrip("/"): f"source.{item['id']}"
        for item in sources.creative_sources
        if item.get("url")
    }

    def add(card: _Card) -> None:
        cards.append(card)
        counts[card.entity_type] = counts.get(card.entity_type, 0) + 1

    for item in sources.techniques:
        technique_id = str(item["id"])
        source = dict(item.get("source", {}))
        source_path = str(source.get("path", ""))
        related: list[str] = []
        skill = _source_skill(source_path)
        if skill and skill in skill_names:
            related.append(f"skill.{skill}")
        manifest_id = source.get("manifest_id")
        if manifest_id:
            related.append(f"source.{manifest_id}")
        frontmatter = _common_frontmatter(
            card_id=technique_id,
            entity_type="visual-technique",
            title=str(item.get("name", technique_id)),
            status=str(item.get("status", "UNKNOWN")),
        )
        frontmatter.update(
            {
                "technique_id": technique_id,
                "category": item.get("category"),
                "selectable": bool(item.get("selectable", False)),
                "priority": item.get("priority"),
                "phases": item.get("phases", []),
                "intents": item.get("intents", []),
                "tags": item.get("tags", []),
                "provider_scopes": item.get("provider_scopes", []),
                "render_runtimes": item.get("render_runtimes", []),
                "source_path": source_path,
                "canonical_source": "config/visual-technique-registry.yaml",
            }
        )
        activation = dict(item.get("activation", {}))
        add(
            _Card(
                card_id=technique_id,
                entity_type="technique",
                title=str(item.get("name", technique_id)),
                status=str(item.get("status", "UNKNOWN")),
                relative_path=Path("02-TECHNIQUES")
                / _slug(str(item.get("category", "uncategorized")))
                / f"{_slug(technique_id)}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Purpose", str(item.get("description", ""))),
                    ("Selection cues", _bullet_list(item.get("intents", []))),
                    (
                        "Directing instructions",
                        _bullet_list(item.get("directives", [])),
                    ),
                    (
                        "Constraints and failure modes",
                        "- Status: `" + str(item.get("status", "UNKNOWN")) + "`\n"
                        + "- Selectable: `"
                        + str(bool(item.get("selectable", False))).lower()
                        + "`\n"
                        + "- Human opt-in: `"
                        + str(bool(activation.get("requires_human_opt_in", False))).lower()
                        + "`\n"
                        + "- License review: `"
                        + str(bool(activation.get("requires_license_review", False))).lower()
                        + "`\n"
                        + "- Network required: `"
                        + str(bool(activation.get("requires_network", False))).lower()
                        + "`",
                    ),
                    (
                        "Route and runtime use",
                        "Providers:\n"
                        + _bullet_list(item.get("provider_scopes", []))
                        + "\n\nRuntimes:\n"
                        + _bullet_list(item.get("render_runtimes", [])),
                    ),
                    ("Source and provenance", _json_block(source)),
                    ("Canonical record", _json_block(item)),
                ),
                related_ids=tuple(dict.fromkeys(related)),
            )
        )

    for item in sources.skills:
        name = str(item["name"])
        status = str(item.get("status", "UNKNOWN"))
        frontmatter = _common_frontmatter(
            card_id=f"skill.{name}",
            entity_type="skill",
            title=name,
            status=status,
        )
        frontmatter.update(
            {
                "skill_name": name,
                "execution": item.get("execution"),
                "owner": item.get("owner"),
                "source_path": item.get("path"),
                "canonical_source": "config/factory-skill-routing.yaml",
            }
        )
        add(
            _Card(
                card_id=f"skill.{name}",
                entity_type="skill",
                title=name,
                status=status,
                relative_path=Path("07-SKILLS")
                / _status_folder(status)
                / f"{_slug(name)}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Factory role", str(item.get("reason", ""))),
                    ("Execution policy", str(item.get("execution", "unspecified"))),
                    ("Source and license", _json_block({
                        "path": item.get("path"),
                        "origin": item.get("origin"),
                        "license_status": item.get("license_status"),
                        "tree_sha256": item.get("tree_sha256"),
                    })),
                    ("Canonical record", _json_block(item)),
                ),
            )
        )

    for item in sources.tools:
        name = str(item["name"])
        status = str(item.get("factory_status", "UNKNOWN"))
        related = tuple(
            f"skill.{skill}"
            for skill in item.get("agent_skills", [])
            if str(skill) in skill_names
        )
        frontmatter = _common_frontmatter(
            card_id=f"tool.{name}",
            entity_type="tool",
            title=name,
            status=status,
        )
        frontmatter.update(
            {
                "tool_name": name,
                "capability": item.get("capability"),
                "provider": item.get("provider"),
                "runtime": item.get("runtime"),
                "network_required": bool(item.get("network_required", False)),
                "canonical_source": "config/tool-inventory.json",
            }
        )
        add(
            _Card(
                card_id=f"tool.{name}",
                entity_type="tool",
                title=name,
                status=status,
                relative_path=Path("08-TOOLS")
                / _slug(str(item.get("capability", "uncategorized")))
                / f"{_slug(name)}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Capability", str(item.get("capability", ""))),
                    ("Factory use", "Provider: `" + str(item.get("provider", ""))
                     + "`  \nRuntime: `" + str(item.get("runtime", "")) + "`"),
                    ("Dependencies", _bullet_list(item.get("dependencies", []))),
                    ("Canonical record", _json_block(item)),
                ),
                related_ids=related,
            )
        )

    for item in sources.creative_sources:
        source_id = str(item["id"])
        status = str(item.get("activation_status", "UNKNOWN"))
        frontmatter = _common_frontmatter(
            card_id=f"source.{source_id}",
            entity_type="creative-source",
            title=source_id,
            status=status,
        )
        frontmatter.update(
            {
                "source_id": source_id,
                "source_kind": item.get("kind"),
                "url": item.get("url"),
                "license": item.get("license"),
                "canonical_source": "vendor/creative-sources/manifest.json",
            }
        )
        bucket = (
            "hugging-face"
            if "huggingface" in str(item.get("url", ""))
            else "github"
        )
        add(
            _Card(
                card_id=f"source.{source_id}",
                entity_type="creative_source",
                title=source_id,
                status=status,
                relative_path=Path("06-SOURCES") / bucket / f"{_slug(source_id)}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Why it is indexed", str(item.get("reason", ""))),
                    ("Activation and safety", "Status: `" + status + "`"),
                    ("Canonical record", _json_block(item)),
                ),
            )
        )

    for link in sources.research_links:
        normalized = link.url.rstrip("/")
        digest = sha256(normalized.encode("utf-8")).hexdigest()[:12]
        card_id = f"research-url.{digest}"
        related = (creative_by_url[normalized],) if normalized in creative_by_url else ()
        frontmatter = _common_frontmatter(
            card_id=card_id,
            entity_type="research-url",
            title=link.title,
            status=link.evidence_class,
        )
        frontmatter.update(
            {
                "url": link.url,
                "host": link.host,
                "evidence_class": link.evidence_class,
                "source_path": link.source_document,
                "canonical_source": link.source_document,
            }
        )
        caution = (
            "This is an anecdotal discovery signal. It must not be treated as a "
            "verified fact, executable instruction, or automatic production input."
            if link.evidence_class == "ANECDOTAL_SIGNAL"
            else "Use the linked primary or project-cited material as evidence; "
            "recheck time-sensitive claims before production."
        )
        add(
            _Card(
                card_id=card_id,
                entity_type="research_url",
                title=link.title,
                status=link.evidence_class,
                relative_path=Path("06-SOURCES")
                / _research_bucket(link.host)
                / f"{digest}-{_slug(link.title)[:72]}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Reference", f"[{link.title}]({link.url})"),
                    ("Evidence handling", caution),
                    ("Discovered in", f"`{link.source_document}`"),
                ),
                related_ids=related,
            )
        )

    for item in sources.local_models:
        model_id = str(item["id"])
        status = str(item.get("factory_status", "UNKNOWN"))
        frontmatter = _common_frontmatter(
            card_id=f"model.{model_id}",
            entity_type="model",
            title=model_id,
            status=status,
        )
        frontmatter.update(
            {
                "model_id": model_id,
                "default_route": item.get("default_route"),
                "license": item.get("license"),
                "license_review_required": bool(item.get("license_review_required", False)),
                "canonical_source": "config/local-models.lock.json",
            }
        )
        add(
            _Card(
                card_id=f"model.{model_id}",
                entity_type="model",
                title=model_id,
                status=status,
                relative_path=Path("09-MODELS") / f"{_slug(model_id)}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Pipeline", str(item.get("pipeline", ""))),
                    ("Mac policy", str(item.get("mac_policy", ""))),
                    ("License and route", _json_block({
                        "license": item.get("license"),
                        "license_review_required": item.get("license_review_required"),
                        "default_route": item.get("default_route"),
                    })),
                    ("Canonical record", _json_block(item)),
                ),
            )
        )

    for item in sources.toolchain:
        name = str(item["name"])
        frontmatter = _common_frontmatter(
            card_id=f"toolchain.{name}",
            entity_type="toolchain",
            title=name,
            status="PINNED",
        )
        frontmatter.update(
            {
                "tool_name": name,
                "role": item.get("role"),
                "repository": item.get("repository"),
                "revision": item.get("commit") or item.get("version"),
                "canonical_source": "config/toolchain-lock.json",
            }
        )
        add(
            _Card(
                card_id=f"toolchain.{name}",
                entity_type="toolchain",
                title=name,
                status="PINNED",
                relative_path=Path("08-TOOLS/toolchain")
                / f"toolchain.{_slug(name)}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Factory role", str(item.get("role", ""))),
                    ("Pinned provenance", _json_block(item)),
                ),
            )
        )

    for item in sources.topview_capabilities:
        group = str(item.get("group", "uncategorized"))
        capability_id = str(item["id"])
        status = str(item.get("factory_status", "UNKNOWN"))
        card_id = f"topview-capability.{group}.{capability_id}"
        frontmatter = _common_frontmatter(
            card_id=card_id,
            entity_type="topview-capability",
            title=str(item.get("official_name", capability_id)),
            status=status,
        )
        frontmatter.update(
            {
                "capability_id": capability_id,
                "capability_group": group,
                "execution_mode": "MANUAL_UI_ONLY",
                "canonical_source": "config/topview-capabilities.yaml",
            }
        )
        add(
            _Card(
                card_id=card_id,
                entity_type="topview_capability",
                title=str(item.get("official_name", capability_id)),
                status=status,
                relative_path=Path("04-PROVIDERS/topview-capabilities")
                / _slug(group)
                / f"{_slug(capability_id)}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Capability", str(item.get("capability", ""))),
                    ("Use for", str(item.get("use_for", ""))),
                    ("Do not use for", str(item.get("do_not_use_for", ""))),
                    (
                        "Execution boundary",
                        "TopView is operated manually in its UI after approval. No API, "
                        "MCP, browser automation, paid call, or implicit dispatch is allowed.",
                    ),
                    ("Canonical record", _json_block(item)),
                ),
            )
        )

    for item in sources.topview_models:
        media_type = str(item.get("media_type", "unknown"))
        family = str(item["family"])
        card_id = f"topview-model.{media_type}.{family}"
        frontmatter = _common_frontmatter(
            card_id=card_id,
            entity_type="topview-model",
            title=family,
            status="MANUAL_SELECTION",
        )
        frontmatter.update(
            {
                "model_family": family,
                "media_type": media_type,
                "exact_ui_label_required": bool(item.get("exact_ui_label_required", True)),
                "execution_mode": "MANUAL_UI_ONLY",
                "canonical_source": "config/topview-capabilities.yaml",
            }
        )
        add(
            _Card(
                card_id=card_id,
                entity_type="topview_model",
                title=family,
                status="MANUAL_SELECTION",
                relative_path=Path("04-PROVIDERS/topview-models")
                / _slug(media_type)
                / f"{_slug(family)}.md",
                frontmatter=frontmatter,
                sections=(
                    ("Use hint", str(item.get("use_hint", ""))),
                    (
                        "Selection rule",
                        "Confirm the exact label visible in TopView at handoff time. "
                        "This family record is planning vocabulary, not an API identifier.",
                    ),
                    ("Canonical record", _json_block(item)),
                ),
            )
        )

    duplicate_ids = sorted(
        card_id for card_id in {card.card_id for card in cards}
        if sum(card.card_id == card_id for card in cards) > 1
    )
    duplicate_paths = sorted(
        str(path) for path in {card.relative_path for card in cards}
        if sum(card.relative_path == path for card in cards) > 1
    )
    if duplicate_ids or duplicate_paths:
        raise KnowledgeVaultError(
            f"Duplicate knowledge cards: ids={duplicate_ids}, paths={duplicate_paths}"
        )
    return cards, counts


def _frontmatter_text(frontmatter: Mapping[str, Any]) -> str:
    return yaml.safe_dump(
        dict(frontmatter),
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=1000,
    ).strip()


def _preserved_notes(existing: str | None) -> str:
    if not existing:
        return "\n"
    match = _USER_NOTES.search(existing)
    return match.group(1) if match else "\n"


def _wiki_link(card: _Card) -> str:
    path = card.relative_path.with_suffix("").as_posix()
    return f"[[{path}|{card.title}]]"


def _render_card(card: _Card, lookup: Mapping[str, _Card], existing: str | None) -> str:
    sections = [f"---\n{_frontmatter_text(card.frontmatter)}\n---", f"# {card.title}"]
    for heading, body in card.sections:
        sections.append(f"## {heading}\n\n{body.strip()}")
    related = [lookup[item] for item in card.related_ids if item in lookup]
    related_body = _bullet_list(_wiki_link(item) for item in related)
    sections.append(f"## Related knowledge\n\n{related_body}")
    notes = _preserved_notes(existing)
    sections.append(
        "## Production notes\n\n"
        f"<!-- USER-NOTES:BEGIN -->{notes}<!-- USER-NOTES:END -->"
    )
    return "\n\n".join(sections).rstrip() + "\n"


def _write_if_changed(path: Path, content: str) -> str:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return "unchanged"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "created" if current is None else "updated"


def _entity_map(title: str, cards: Iterable[_Card]) -> str:
    grouped: dict[str, list[_Card]] = {}
    for card in cards:
        grouped.setdefault(card.status, []).append(card)
    parts = [f"# {title}", "Generated navigation; canonical registries remain authoritative."]
    for status in sorted(grouped):
        parts.append(f"## {status}")
        parts.append(
            _bullet_list(
                _wiki_link(card)
                for card in sorted(grouped[status], key=lambda item: item.title.lower())
            )
        )
    return "\n\n".join(parts).rstrip() + "\n"


def _static_vault_files(cards: list[_Card], catalog_version: str) -> dict[Path, str]:
    by_type: dict[str, list[_Card]] = {}
    for card in cards:
        by_type.setdefault(card.entity_type, []).append(card)

    maps = {
        Path("01-MAPS/Techniques.md"): _entity_map("Techniques", by_type["technique"]),
        Path("01-MAPS/Skills.md"): _entity_map("Skills", by_type["skill"]),
        Path("01-MAPS/Tools.md"): _entity_map(
            "Tools", by_type["tool"] + by_type["toolchain"]
        ),
        Path("01-MAPS/Sources.md"): _entity_map(
            "Sources", by_type["creative_source"] + by_type["research_url"]
        ),
        Path("01-MAPS/Models.md"): _entity_map(
            "Models", by_type["model"] + by_type["topview_model"]
        ),
        Path("01-MAPS/Providers.md"): _entity_map(
            "Providers", by_type["topview_capability"] + by_type["topview_model"]
        ),
    }
    phases: dict[str, list[_Card]] = {}
    runtimes: dict[str, list[_Card]] = {}
    for card in by_type["technique"]:
        for phase in card.frontmatter.get("phases", []):
            phases.setdefault(str(phase), []).append(card)
        for runtime in card.frontmatter.get("render_runtimes", []):
            runtimes.setdefault(str(runtime), []).append(card)
    maps[Path("01-MAPS/Production-Phases.md")] = "\n\n".join(
        ["# Production phases"]
        + [
            f"## {name}\n\n"
            + _bullet_list(_wiki_link(card) for card in sorted(items, key=lambda x: x.title))
            for name, items in sorted(phases.items())
        ]
    ) + "\n"
    maps[Path("01-MAPS/Runtimes.md")] = "\n\n".join(
        ["# Runtimes", "See also [[05-RUNTIMES/HyperFrames]], [[05-RUNTIMES/Remotion]], and [[05-RUNTIMES/FFmpeg]]."]
        + [
            f"## {name}\n\n"
            + _bullet_list(_wiki_link(card) for card in sorted(items, key=lambda x: x.title))
            for name, items in sorted(runtimes.items())
        ]
    ) + "\n"

    statuses: dict[str, int] = {}
    for card in cards:
        statuses[card.status] = statuses.get(card.status, 0) + 1
    maps[Path("01-MAPS/Status-and-Safety.md")] = (
        "# Status and safety\n\n"
        "Status is a production constraint, not decoration. `BLOCKED`, `PROHIBITED`, "
        "or reference-only knowledge cannot be silently activated. Reddit material is "
        "always `ANECDOTAL_SIGNAL`. Human Gates remain outside this vault.\n\n"
        "## Current counts\n\n"
        + _bullet_list(f"{status}: {count}" for status, count in sorted(statuses.items()))
        + "\n"
    )

    start = """# 유튜브공장 Knowledge Vault

This is the searchable knowledge layer for MK Visual Director and OpenMontage. It indexes every audited technique, skill, tool, source, model, TopView capability, and research URL without making any of them automatically executable.

## Start here

- [[01-MAPS/Techniques]]
- [[01-MAPS/Production-Phases]]
- [[01-MAPS/Providers]]
- [[01-MAPS/Runtimes]]
- [[01-MAPS/Skills]]
- [[01-MAPS/Tools]]
- [[01-MAPS/Sources]]
- [[01-MAPS/Models]]
- [[01-MAPS/Status-and-Safety]]
- [[03-PLAYBOOKS/Heritage-Forge]]
- [[04-PROVIDERS/TopView-Manual]]

## Authority order

1. OpenMontage is the control plane and source of truth.
2. MK Visual Director selects visual grammar and prepares an approved VisualPlan.
3. Canonical config registries decide status, routing, license, and activation.
4. This vault expands knowledge and preserves production notes; it never approves a gate.
5. TopView is manual UI only. No TopView API, MCP, or browser automation is permitted.

## Working rule

Search broadly here, then build a bounded knowledge pack. A shot receives only the 3–7 techniques and related support cards selected for its intent, provider, runtime, evidence role, and approval state.
"""
    playbook = """# Heritage Forge

The factory's documentary playbook prioritizes meaning, material detail, verified evidence, and controlled cinematic movement.

## Ladder

1. Evidence ingest and claim ledger
2. MK Visual Director sequence meaning and shot grammar
3. Animatic and fact/budget Human Gate
4. Production Router dispatch to real ingest, manual TopView, local generation, or HyperFrames
5. Asset-selection Human Gate
6. OpenMontage edit, compose, audio, captions, QC, and delivery state

Use [[01-MAPS/Techniques]] and [[01-MAPS/Production-Phases]] to assemble the shot-specific knowledge pack. Do not load every technique into every shot.
"""
    topview = """# TopView Manual

TopView is a semi-automated production workstation, not the factory control plane.

## Allowed flow

1. OpenMontage records the approved work order.
2. MK Visual Director exports shot intent, references, negative constraints, duration, aspect ratio, and exact fact overlays.
3. A human selects the current TopView UI feature and exact visible model label.
4. A human submits and downloads the result.
5. The result is ingested back into OpenMontage with provenance and selection state.

## Forbidden flow

- No TopView API calls
- No TopView MCP execution
- No browser automation or hidden paid dispatch
- No replacement of Visual Director decisions
- No automatic approval of generated assets

See [[01-MAPS/Providers]] for all indexed capabilities and model families.
"""
    local_ltx = """# Local LTX

Local LTX is the preferred pilot route for compatible image-to-video work on this Mac. Use the locked model card and verified MPS workflow, keep license review flags visible, and inspect the rendered media before accepting it.

See [[01-MAPS/Models]].
"""
    isolation = """# Provider Isolation

Provider outputs are proposals. They cannot write approval state or become timeline truth until OpenMontage ingests them with provenance. Manual TopView, local models, actual evidence, and graphics runtimes stay isolated behind their route contracts.
"""
    runtime_docs = {
        Path("05-RUNTIMES/HyperFrames.md"): "# HyperFrames\n\nPrimary motion-graphics and exact overlay runtime. Use registry-approved techniques and render checks.\n",
        Path("05-RUNTIMES/Remotion.md"): "# Remotion\n\nSecondary programmatic composition runtime for templates that explicitly route to Remotion.\n",
        Path("05-RUNTIMES/FFmpeg.md"): "# FFmpeg\n\nDeterministic media inspection, encoding, assembly support, and metadata verification layer.\n",
    }
    templates = {
        Path("11-TEMPLATES/Technique-Note.md"): "# {{technique}}\n\n## Shot intent\n\n## Why selected\n\n## Failure to avoid\n\n## Production notes\n",
        Path("11-TEMPLATES/Shot-Knowledge-Pack.md"): "# {{shot_id}} knowledge pack\n\n## Intent\n\n## Selected techniques (3–7)\n\n## Related skills and tools\n\n## Sources and evidence class\n\n## Exclusions\n",
        Path("11-TEMPLATES/Source-Evidence.md"): "# {{source}}\n\n## Claim\n\n## Evidence class\n\n## License and date check\n\n## Production relevance\n",
        Path("11-TEMPLATES/TopView-Handoff.md"): "# {{shot_id}} TopView manual handoff\n\n## Approved intent\n\n## Exact UI label\n\n## References\n\n## Negative constraints\n\n## Manual return path\n",
        Path("11-TEMPLATES/Pilot-Observation.md"): "# {{pilot}} observation\n\n## Expected\n\n## Observed\n\n## Media verification\n\n## Registry change proposal\n",
    }

    files: dict[Path, str] = {
        Path("00-START-HERE.md"): start,
        Path("03-PLAYBOOKS/Heritage-Forge.md"): playbook,
        Path("04-PROVIDERS/TopView-Manual.md"): topview,
        Path("04-PROVIDERS/Local-LTX.md"): local_ltx,
        Path("04-PROVIDERS/Provider-Isolation.md"): isolation,
        Path("06-SOURCES/Source-Manifest.md"): "# Source manifest\n\nSee [[01-MAPS/Sources]]. Canonical lock: `vendor/creative-sources/manifest.json`.\n",
        Path("06-SOURCES/Capability-Audit.md"): "# Capability audit\n\nCanonical research: `docs/research/2026-08-11-tool-skill-capability-audit.md`.\n",
        Path("06-SOURCES/Evidence-Map.md"): "# Evidence map\n\nCited references and anecdotal discovery signals are deliberately separated in [[01-MAPS/Sources]].\n",
        Path("10-INBOX/README.md"): "# Inbox\n\nTemporary human notes go here. Promote them only by proposing a reviewed registry or knowledge update.\n",
        Path(".obsidian/app.json"): json.dumps({
            "alwaysUpdateLinks": True,
            "newFileLocation": "folder",
            "newFileFolderPath": "10-INBOX",
            "showLineNumber": False,
            "useMarkdownLinks": False,
        }, ensure_ascii=False, indent=2) + "\n",
        Path(".obsidian/appearance.json"): json.dumps({
            "accentColor": "#b87333",
            "baseFontSize": 16,
            "theme": "obsidian",
        }, ensure_ascii=False, indent=2) + "\n",
        Path(".obsidian/core-plugins.json"): json.dumps([
            "file-explorer", "global-search", "switcher", "graph", "backlink",
            "outgoing-link", "tag-pane", "properties", "templates"
        ], ensure_ascii=False, indent=2) + "\n",
        Path(".gitignore"): "/.obsidian/workspace*.json\n/.obsidian/cache/\n/.obsidian/plugins/\n/.trash/\n.DS_Store\n",
    }
    files.update(maps)
    files.update(runtime_docs)
    files.update(templates)
    catalog = {
        "knowledge_schema": "1.0",
        "visual_technique_catalog_version": catalog_version,
        "entity_count": len(cards),
        "cards": [
            {
                "card_id": card.card_id,
                "entity_type": card.entity_type,
                "status": card.status,
                "path": card.relative_path.as_posix(),
            }
            for card in sorted(cards, key=lambda item: item.card_id)
        ],
    }
    files[Path(".factory-catalog.json")] = (
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )
    return files


def sync_vault(
    sources: KnowledgeSources, *, root: Path | None = None
) -> SyncReport:
    """Materialize the complete portable vault without deleting human content.

    Generated sections follow canonical project inventories. The delimited production
    notes section in every entity card is preserved byte-for-byte across synchronizations.
    Unknown Markdown files are reported as orphans and never deleted.
    """

    project_root = Path(root).resolve() if root is not None else sources.project_root
    vault = project_root / "knowledge"
    cards, counts = _build_cards(sources)
    lookup = {card.card_id: card for card in cards}
    expected_paths = {card.relative_path for card in cards}

    existing_managed: set[Path] = set()
    for folder in (
        "02-TECHNIQUES",
        "04-PROVIDERS/topview-capabilities",
        "04-PROVIDERS/topview-models",
        "06-SOURCES/github",
        "06-SOURCES/hugging-face",
        "06-SOURCES/official-sites",
        "06-SOURCES/reddit-signals",
        "07-SKILLS",
        "08-TOOLS",
        "09-MODELS",
    ):
        base = vault / folder
        if base.exists():
            existing_managed.update(path.relative_to(vault) for path in base.rglob("*.md"))
    orphans = tuple(sorted((existing_managed - expected_paths), key=lambda path: path.as_posix()))

    outcomes = {"created": 0, "updated": 0, "unchanged": 0}
    for card in sorted(cards, key=lambda item: item.relative_path.as_posix()):
        path = vault / card.relative_path
        existing = path.read_text(encoding="utf-8") if path.exists() else None
        result = _write_if_changed(path, _render_card(card, lookup, existing))
        outcomes[result] += 1

    for relative_path, content in sorted(
        _static_vault_files(cards, sources.catalog_version).items(),
        key=lambda item: item[0].as_posix(),
    ):
        result = _write_if_changed(vault / relative_path, content)
        outcomes[result] += 1

    return SyncReport(
        created=outcomes["created"],
        updated=outcomes["updated"],
        unchanged=outcomes["unchanged"],
        entity_cards=len(cards),
        entity_counts=counts,
        orphans=tuple(path.as_posix() for path in orphans),
    )


def _parse_frontmatter(text: str, *, path: Path) -> dict[str, Any]:
    if not text.startswith("---\n"):
        raise KnowledgeVaultError(f"Missing YAML frontmatter: {path}")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise KnowledgeVaultError(f"Unterminated YAML frontmatter: {path}")
    try:
        payload = yaml.safe_load(text[4:marker])
    except yaml.YAMLError as exc:
        raise KnowledgeVaultError(f"Invalid YAML frontmatter {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise KnowledgeVaultError(f"Frontmatter must be an object: {path}")
    return payload


def _managed_entity_paths(vault: Path) -> set[Path]:
    paths: set[Path] = set()
    for folder in (
        "02-TECHNIQUES",
        "04-PROVIDERS/topview-capabilities",
        "04-PROVIDERS/topview-models",
        "06-SOURCES/github",
        "06-SOURCES/hugging-face",
        "06-SOURCES/official-sites",
        "06-SOURCES/reddit-signals",
        "07-SKILLS",
        "08-TOOLS",
        "09-MODELS",
    ):
        base = vault / folder
        if base.exists():
            paths.update(path.relative_to(vault) for path in base.rglob("*.md"))
    return paths


def audit_vault(
    sources: KnowledgeSources, *, root: Path | None = None
) -> list[str]:
    """Return deterministic drift and integrity findings without changing the vault."""

    project_root = Path(root).resolve() if root is not None else sources.project_root
    vault = project_root / "knowledge"
    findings: list[str] = []
    if not vault.is_dir():
        return [f"missing vault: {vault}"]

    cards, _ = _build_cards(sources)
    lookup = {card.card_id: card for card in cards}
    expected_paths = {card.relative_path for card in cards}
    actual_paths = _managed_entity_paths(vault)

    for relative_path in sorted(expected_paths - actual_paths, key=lambda path: path.as_posix()):
        card = next(item for item in cards if item.relative_path == relative_path)
        findings.append(f"missing card {card.card_id}: {relative_path.as_posix()}")
    for relative_path in sorted(actual_paths - expected_paths, key=lambda path: path.as_posix()):
        findings.append(f"orphan card: {relative_path.as_posix()}")

    seen_ids: dict[str, Path] = {}
    for card in sorted(cards, key=lambda item: item.card_id):
        path = vault / card.relative_path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        try:
            actual_frontmatter = _parse_frontmatter(text, path=path)
        except KnowledgeVaultError as exc:
            findings.append(str(exc))
            continue
        actual_id = str(actual_frontmatter.get("card_id", ""))
        if actual_id and actual_id in seen_ids:
            findings.append(
                "duplicate card_id " + actual_id + ": "
                + seen_ids[actual_id].relative_to(vault).as_posix()
                + ", " + card.relative_path.as_posix()
            )
        elif actual_id:
            seen_ids[actual_id] = path
        for key, expected_value in card.frontmatter.items():
            actual_value = actual_frontmatter.get(key)
            if actual_value != expected_value:
                findings.append(
                    f"drift {card.card_id}: {key} expected={expected_value!r} "
                    f"actual={actual_value!r}"
                )
        expected_text = _render_card(card, lookup, text)
        if text != expected_text and not any(
            item.startswith(f"drift {card.card_id}:") for item in findings
        ):
            findings.append(f"generated content drift: {card.card_id}")

        source_path = actual_frontmatter.get("source_path")
        if isinstance(source_path, str) and source_path and not source_path.startswith(
            ("http://", "https://")
        ):
            source_target = sources.project_root / source_path
            if not source_target.exists():
                findings.append(
                    f"missing local source_path {card.card_id}: {source_path}"
                )

    for relative_path in sorted(actual_paths - expected_paths, key=lambda path: path.as_posix()):
        path = vault / relative_path
        try:
            frontmatter = _parse_frontmatter(path.read_text(encoding="utf-8"), path=path)
        except KnowledgeVaultError:
            continue
        card_id = frontmatter.get("card_id")
        if card_id and str(card_id) in seen_ids:
            findings.append(
                f"duplicate card_id {card_id}: {relative_path.as_posix()}"
            )

    static_files = _static_vault_files(cards, sources.catalog_version)
    for relative_path, expected in sorted(
        static_files.items(), key=lambda item: item[0].as_posix()
    ):
        path = vault / relative_path
        if not path.is_file():
            findings.append(f"missing generated vault file: {relative_path.as_posix()}")
        elif path.read_text(encoding="utf-8") != expected:
            findings.append(f"generated vault file drift: {relative_path.as_posix()}")

    if (vault / ".obsidian/community-plugins.json").exists():
        findings.append("prohibited Obsidian community-plugin state")
    for path in sorted((vault / ".obsidian").glob("workspace*")):
        findings.append(f"prohibited Obsidian workspace state: {path.name}")

    markdown_paths = sorted(vault.rglob("*.md"))
    for path in markdown_paths:
        text = path.read_text(encoding="utf-8")
        for raw_target in _WIKILINK.findall(text):
            target = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
            if not target or "://" in target:
                continue
            target_path = vault / target
            if not target.lower().endswith(".md"):
                target_path = Path(str(target_path) + ".md")
            if not target_path.is_file():
                findings.append(
                    "broken wikilink " + path.relative_to(vault).as_posix()
                    + f": {target}"
                )

    return sorted(dict.fromkeys(findings))


def _token_list(value: str) -> list[str]:
    tokens: list[str] = []
    for raw in _TOKEN.findall(value.casefold()):
        for token in (raw, *raw.split("_")):
            if token and token not in tokens:
                tokens.append(token)
    return tokens


def _flatten_search_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        flattened: list[str] = []
        for item in value.values():
            flattened.extend(_flatten_search_values(item))
        return flattened
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray)):
        flattened = []
        for item in value:
            flattened.extend(_flatten_search_values(item))
        return flattened
    return [str(value)] if value is not None else []


def search_vault(
    query: str,
    *,
    entity_types: tuple[str, ...] | None = None,
    root: Path = FACTORY_ROOT,
) -> list[dict[str, Any]]:
    """Search every indexed status using deterministic structured-first ranking."""

    query_phrase = query.strip().casefold()
    query_tokens = _token_list(query)
    if not query_tokens:
        raise KnowledgeVaultError("Search query must contain at least one token")
    vault = Path(root).resolve() / "knowledge"
    catalog_path = vault / ".factory-catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeVaultError(f"Cannot load vault catalog {catalog_path}: {exc}") from exc
    records = catalog.get("cards", [])
    if not isinstance(records, list):
        raise KnowledgeVaultError("Vault catalog cards must be a list")

    allowed_types = set(entity_types) if entity_types is not None else None
    results: list[dict[str, Any]] = []
    structured_keys = {
        "card_id", "technique_id", "intents", "tags", "skill_name", "tool_name",
        "source_id", "model_id", "capability_id", "model_family", "default_route",
        "provider_scopes", "render_runtimes", "capability", "provider", "runtime",
    }
    for record in records:
        entity_type = str(record.get("entity_type", ""))
        if allowed_types is not None and entity_type not in allowed_types:
            continue
        relative_path = Path(str(record.get("path", "")))
        path = vault / relative_path
        if not path.is_file():
            continue
        body = path.read_text(encoding="utf-8")
        try:
            frontmatter = _parse_frontmatter(body, path=path)
        except KnowledgeVaultError:
            continue
        structured_values = _flatten_search_values(
            {key: frontmatter[key] for key in structured_keys if key in frontmatter}
        )
        structured_exact = {item.casefold() for item in structured_values}
        structured_tokens = set(_token_list(" ".join(structured_values)))
        title = str(frontmatter.get("title", record.get("card_id", "")))
        title_tokens = set(_token_list(title))
        body_tokens = set(_token_list(body))
        required = set(query_tokens)

        if query_phrase in structured_exact:
            score = 400
        elif required.issubset(structured_tokens):
            score = 300
        elif query_phrase and query_phrase in title.casefold():
            score = 250
        elif required.issubset(title_tokens):
            score = 200
        elif required.issubset(body_tokens):
            score = 100
        else:
            matches = required & body_tokens
            if not matches:
                continue
            score = 10 * len(matches)
        matched_terms = [term for term in query_tokens if term in body_tokens]
        results.append(
            {
                "card_id": str(record.get("card_id", "")),
                "entity_type": entity_type,
                "title": title,
                "status": str(frontmatter.get("status", record.get("status", ""))),
                "evidence_class": frontmatter.get("evidence_class"),
                "path": (Path("knowledge") / relative_path).as_posix(),
                "score": score,
                "matched_terms": matched_terms,
            }
        )
    return sorted(results, key=lambda item: (-int(item["score"]), str(item["card_id"])))


def _card_reference(card: _Card) -> dict[str, Any]:
    return {
        "card_id": card.card_id,
        "entity_type": card.entity_type,
        "title": card.title,
        "status": card.status,
        "path": (Path("knowledge") / card.relative_path).as_posix(),
    }


def _dedupe(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def resolve_knowledge_pack(
    selection: dict[str, Any],
    *,
    sources: KnowledgeSources,
    root: Path | None = None,
) -> dict[str, Any]:
    """Resolve an approved selector result into a small route-safe reading pack.

    This function never selects a provider or technique. It revalidates the supplied
    selection against the canonical registry, then resolves only explicit local
    relations. Search-only and anecdotal records cannot enter a production pack.
    """

    if not isinstance(selection, dict):
        raise KnowledgeVaultError("Technique selection must be an object")
    query = selection.get("query")
    selected_records = selection.get("selected")
    if not isinstance(query, dict) or not isinstance(selected_records, list):
        raise KnowledgeVaultError("Technique selection requires query and selected")
    if not 3 <= len(selected_records) <= 7:
        raise KnowledgeVaultError("Technique selection must contain between 3 and 7 items")

    selected_ids: list[str] = []
    for record in selected_records:
        if not isinstance(record, dict) or not isinstance(record.get("id"), str):
            raise KnowledgeVaultError("Every selected technique requires a string id")
        selected_ids.append(record["id"])
    if len(set(selected_ids)) != len(selected_ids):
        raise KnowledgeVaultError("Technique selection contains duplicate ids")

    provider_scope = str(query.get("provider_scope", "")).upper()
    render_runtime = str(query.get("render_runtime", "ANY")).upper()
    phase = str(query.get("phase", ""))
    include_on_demand = query.get("include_on_demand") is True
    techniques = {str(item["id"]): item for item in sources.techniques}
    selected_techniques: list[dict[str, Any]] = []
    for technique_id in selected_ids:
        item = techniques.get(technique_id)
        if item is None:
            raise KnowledgeVaultError(f"Unknown selected technique: {technique_id}")
        status = str(item.get("status", "UNKNOWN"))
        if status in {"BLOCKED", "REFERENCE_ONLY"}:
            raise KnowledgeVaultError(f"{technique_id}: status {status} cannot enter a pack")
        if status == "ON_DEMAND" and not include_on_demand:
            raise KnowledgeVaultError(
                f"{technique_id}: ON_DEMAND requires explicit opt-in"
            )
        if status not in {"ACTIVE", "ON_DEMAND"}:
            raise KnowledgeVaultError(f"{technique_id}: unsupported status {status}")
        if not bool(item.get("selectable", False)):
            raise KnowledgeVaultError(f"{technique_id}: selectable is false")
        provider_scopes = {str(value).upper() for value in item.get("provider_scopes", [])}
        if "GENERIC" not in provider_scopes and provider_scope not in provider_scopes:
            raise KnowledgeVaultError(
                f"{technique_id}: provider_scope {provider_scope} is not allowed"
            )
        runtimes = {str(value).upper() for value in item.get("render_runtimes", [])}
        if (
            render_runtime != "ANY"
            and "ANY" not in runtimes
            and render_runtime not in runtimes
        ):
            raise KnowledgeVaultError(
                f"{technique_id}: render_runtime {render_runtime} is not allowed"
            )
        phases = {str(value) for value in item.get("phases", [])}
        if phase and "ALL" not in phases and phase not in phases:
            raise KnowledgeVaultError(f"{technique_id}: phase {phase} is not allowed")
        selected_techniques.append(item)

    project_root = Path(root).resolve() if root is not None else sources.project_root
    vault = project_root / "knowledge"
    cards, _ = _build_cards(sources)
    card_lookup = {card.card_id: card for card in cards}

    def require_card(card_id: str) -> _Card:
        card = card_lookup.get(card_id)
        if card is None:
            raise KnowledgeVaultError(f"Knowledge card is not indexed: {card_id}")
        if not (vault / card.relative_path).is_file():
            raise KnowledgeVaultError(f"Knowledge card is missing: {card_id}")
        return card

    technique_cards = [_card_reference(require_card(item)) for item in selected_ids]
    exclusions: list[dict[str, str]] = []
    for excluded in selection.get("excluded", []):
        if isinstance(excluded, dict) and excluded.get("id") and excluded.get("reason"):
            exclusions.append(
                {"id": str(excluded["id"]), "reason": "selector:" + str(excluded["reason"])}
            )

    direct_skill_ids: list[str] = []
    direct_source_ids: list[str] = []
    source_paths: list[str] = []
    for item in selected_techniques:
        source = dict(item.get("source", {}))
        source_path = str(source.get("path", ""))
        if source_path:
            source_paths.append(source_path)
            skill_name = _source_skill(source_path)
            if skill_name:
                direct_skill_ids.append(f"skill.{skill_name}")
        manifest_id = source.get("manifest_id")
        if manifest_id:
            direct_source_ids.append(f"source.{manifest_id}")

    candidate_tools: list[tuple[int, str, dict[str, Any]]] = []
    direct_skill_names = {item.removeprefix("skill.") for item in direct_skill_ids}
    runtime_provider = {
        "HYPERFRAMES": "hyperframes",
        "REMOTION": "remotion",
        "FFMPEG": "ffmpeg",
    }.get(render_runtime)
    route_provider = {
        "TOPVIEW_MANUAL": "topview_manual",
        "HIGGSFIELD_MANUAL": "higgsfield",
        "SEEDANCE_MANUAL": "seedance",
        "LOCAL_LTX": "ltx",
    }.get(provider_scope)
    for item in sources.tools:
        tool_name = str(item["name"])
        agent_skills = {str(value) for value in item.get("agent_skills", [])}
        provider = str(item.get("provider", ""))
        priority: int | None = None
        if direct_skill_names & agent_skills:
            priority = 0
        elif route_provider and provider == route_provider:
            priority = 1
        elif runtime_provider and provider == runtime_provider:
            priority = 2
        if priority is None:
            continue
        status = str(item.get("factory_status", "UNKNOWN"))
        if status in {"DISABLED_BY_DEFAULT", "EXPLICIT_OPT_IN", "HUMAN_GATE_ONLY"}:
            exclusions.append({"id": f"tool.{tool_name}", "reason": f"status:{status}"})
            continue
        if bool(item.get("network_required", False)):
            exclusions.append({"id": f"tool.{tool_name}", "reason": "network_required"})
            continue
        candidate_tools.append((priority, tool_name, item))
    candidate_tools.sort(key=lambda row: (row[0], row[1]))

    tool_card_ids = [f"tool.{item['name']}" for _, _, item in candidate_tools]
    toolchain_ids = ["toolchain.openmontage"]
    if route_provider:
        route_toolchain = {
            "topview_manual": "toolchain.topview",
            "ltx": "toolchain.comfyui",
        }.get(route_provider)
        if route_toolchain:
            toolchain_ids.append(route_toolchain)
    runtime_toolchain = {
        "HYPERFRAMES": "toolchain.hyperframes",
        "REMOTION": "toolchain.remotion",
        "FFMPEG": "toolchain.ffmpeg",
    }.get(render_runtime)
    if runtime_toolchain:
        toolchain_ids.append(runtime_toolchain)
    all_tool_ids = _dedupe([*tool_card_ids, *toolchain_ids])
    if len(all_tool_ids) > 7:
        for card_id in all_tool_ids[7:]:
            exclusions.append({"id": card_id, "reason": "tool_card_budget:7"})
        all_tool_ids = all_tool_ids[:7]
    tool_cards = [_card_reference(require_card(card_id)) for card_id in all_tool_ids]

    support_skill_ids = list(direct_skill_ids)
    tools_by_id = {f"tool.{item['name']}": item for item in sources.tools}
    for tool_id in all_tool_ids:
        item = tools_by_id.get(tool_id)
        if item:
            support_skill_ids.extend(
                f"skill.{skill}" for skill in item.get("agent_skills", [])
            )
    support_skill_ids = _dedupe(support_skill_ids)
    allowed_skill_ids: list[str] = []
    for card_id in support_skill_ids:
        card = card_lookup.get(card_id)
        if card is None:
            exclusions.append({"id": card_id, "reason": "skill_not_indexed"})
            continue
        if card.status in {"DISABLED_BY_DEFAULT", "REFERENCE_ONLY"}:
            exclusions.append({"id": card_id, "reason": f"status:{card.status}"})
            continue
        allowed_skill_ids.append(card_id)
    if len(allowed_skill_ids) > 7:
        for card_id in allowed_skill_ids[7:]:
            exclusions.append({"id": card_id, "reason": "skill_card_budget:7"})
        allowed_skill_ids = allowed_skill_ids[:7]
    skill_cards = [_card_reference(require_card(card_id)) for card_id in allowed_skill_ids]

    source_ids = _dedupe(direct_source_ids)
    if len(source_ids) > 7:
        for card_id in source_ids[7:]:
            exclusions.append({"id": card_id, "reason": "source_card_budget:7"})
        source_ids = source_ids[:7]
    source_cards: list[dict[str, Any]] = []
    for card_id in source_ids:
        card = require_card(card_id)
        if card.status in {"BLOCKED", "REFERENCE_ONLY"}:
            exclusions.append({"id": card_id, "reason": f"status:{card.status}"})
            continue
        source_cards.append(_card_reference(card))

    skills_by_id = {f"skill.{item['name']}": item for item in sources.skills}
    for card_id in allowed_skill_ids:
        source_path = str(skills_by_id.get(card_id, {}).get("path", ""))
        if source_path:
            source_paths.append(source_path)
    source_paths = _dedupe(source_paths)

    load_order = [
        item["path"]
        for family in (technique_cards, skill_cards, tool_cards, source_cards)
        for item in family
    ]
    exclusions = sorted(
        (dict(item) for item in exclusions),
        key=lambda item: (item.get("id", ""), item.get("reason", "")),
    )
    return {
        "registry_version": sources.catalog_version,
        "query": {
            "phase": phase,
            "provider_scope": provider_scope,
            "render_runtime": render_runtime,
            "include_on_demand": include_on_demand,
        },
        "selected_ids": selected_ids,
        "technique_cards": technique_cards,
        "skill_cards": skill_cards,
        "tool_cards": tool_cards,
        "source_cards": source_cards,
        "source_paths": source_paths,
        "load_order": load_order,
        "exclusions": exclusions,
    }
