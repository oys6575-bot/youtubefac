from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_ENTITY_COUNTS = {
    "technique": 43,
    "skill": 107,
    "tool": 104,
    "creative_source": 16,
    "research_url": 23,
    "model": 6,
    "toolchain": 10,
    "topview_capability": 59,
    "topview_model": 12,
}


def _module():
    return importlib.import_module("lib.knowledge_vault")


def test_loads_every_audited_knowledge_source() -> None:
    sources = _module().load_knowledge_sources(root=ROOT)

    assert sources.project_root == ROOT.resolve()
    assert len(sources.techniques) == 43
    assert len(sources.skills) == 107
    assert len(sources.tools) == 104
    assert len(sources.creative_sources) == 16
    assert len(sources.research_links) == 23
    assert sum(link.host == "www.reddit.com" for link in sources.research_links) == 6
    assert all(
        link.evidence_class == "ANECDOTAL_SIGNAL"
        for link in sources.research_links
        if link.host == "www.reddit.com"
    )
    assert len(sources.local_models) == 6
    assert len(sources.toolchain) == 10
    assert len(sources.topview_capabilities) == 59
    assert len(sources.topview_models) == 12


def test_sync_creates_complete_portable_vault(tmp_path: Path) -> None:
    module = _module()
    sources = module.load_knowledge_sources(root=ROOT)

    report = module.sync_vault(sources, root=tmp_path)
    vault = tmp_path / "knowledge"

    assert report.entity_cards == 380
    assert report.entity_counts == EXPECTED_ENTITY_COUNTS
    assert len(list(vault.rglob("*.md"))) > 380
    assert (vault / "00-START-HERE.md").is_file()
    assert (vault / "01-MAPS/Techniques.md").is_file()
    assert (vault / ".obsidian/app.json").is_file()
    assert not (vault / ".obsidian/community-plugins.json").exists()
    assert not list((vault / ".obsidian").glob("workspace*"))

    card = vault / "02-TECHNIQUES/camera/camera.variable_velocity_push.md"
    text = card.read_text(encoding="utf-8")
    assert "type: visual-technique" in text
    assert "technique_id: camera.variable_velocity_push" in text
    assert "source_path: .agents/skills/hyperframes-animation/rules/nudge-curve.md" in text
    assert "<!-- USER-NOTES:BEGIN -->" in text
    assert "<!-- USER-NOTES:END -->" in text


def test_sync_is_idempotent_and_preserves_production_notes(tmp_path: Path) -> None:
    module = _module()
    sources = module.load_knowledge_sources(root=ROOT)
    module.sync_vault(sources, root=tmp_path)
    card = (
        tmp_path
        / "knowledge/02-TECHNIQUES/camera/camera.variable_velocity_push.md"
    )
    card.write_text(
        card.read_text(encoding="utf-8").replace(
            "<!-- USER-NOTES:BEGIN -->\n",
            "<!-- USER-NOTES:BEGIN -->\nVerified on the bangjja pilot.\n",
        ),
        encoding="utf-8",
    )

    second = module.sync_vault(sources, root=tmp_path)

    assert "Verified on the bangjja pilot." in card.read_text(encoding="utf-8")
    assert second.created == 0
    assert second.updated == 0
    assert second.unchanged > 380
