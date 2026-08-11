from __future__ import annotations

from copy import deepcopy
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest


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


def _sync_fixture(tmp_path: Path):
    module = _module()
    sources = module.load_knowledge_sources(root=ROOT)
    module.sync_vault(sources, root=tmp_path)
    return sources


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


def test_audit_accepts_a_clean_vault(tmp_path: Path) -> None:
    sources = _sync_fixture(tmp_path)

    assert _module().audit_vault(sources, root=tmp_path) == []


def test_audit_detects_policy_drift_orphan_and_broken_link(tmp_path: Path) -> None:
    sources = _sync_fixture(tmp_path)
    card = (
        tmp_path
        / "knowledge/02-TECHNIQUES/camera/camera.variable_velocity_push.md"
    )
    card.write_text(
        card.read_text(encoding="utf-8")
        .replace("status: ACTIVE", "status: BLOCKED", 1)
        .replace(
            "<!-- USER-NOTES:BEGIN -->",
            "[[02-TECHNIQUES/camera/does-not-exist]]\n<!-- USER-NOTES:BEGIN -->",
        ),
        encoding="utf-8",
    )
    orphan = tmp_path / "knowledge/02-TECHNIQUES/camera/orphan.md"
    orphan.write_text(
        "---\ntype: visual-technique\ntechnique_id: orphan\n---\n",
        encoding="utf-8",
    )

    findings = _module().audit_vault(sources, root=tmp_path)

    assert any(
        "camera.variable_velocity_push" in item and "status" in item
        for item in findings
    )
    assert any("orphan.md" in item and "orphan" in item for item in findings)
    assert any("does-not-exist" in item and "broken wikilink" in item for item in findings)
    assert orphan.exists()


def test_search_exposes_all_statuses_but_labels_reddit_as_anecdotal(
    tmp_path: Path,
) -> None:
    _sync_fixture(tmp_path)

    motion = _module().search_vault("photo_to_motion", root=tmp_path)
    reddit = _module().search_vault("unlimited plans", root=tmp_path)

    assert motion[0]["card_id"] == "camera.material_macro_parallax"
    assert any(item["evidence_class"] == "ANECDOTAL_SIGNAL" for item in reddit)


def _selection() -> dict:
    return json.loads(
        (ROOT / "tests/fixtures/youtube_factory/technique_selection.valid.json")
        .read_text(encoding="utf-8")
    )


def test_pack_is_bounded_ordered_and_route_safe_for_topview(tmp_path: Path) -> None:
    sources = _sync_fixture(tmp_path)

    pack = _module().resolve_knowledge_pack(
        _selection(), sources=sources, root=tmp_path
    )

    expected = [item["id"] for item in _selection()["selected"]]
    assert pack["selected_ids"] == expected
    assert [item["card_id"] for item in pack["technique_cards"]] == expected
    for family in ("skill_cards", "tool_cards", "source_cards"):
        assert len(pack[family]) <= 7
    for card in (
        pack["technique_cards"]
        + pack["skill_cards"]
        + pack["tool_cards"]
        + pack["source_cards"]
    ):
        assert (tmp_path / card["path"]).is_file()
    serialized = json.dumps(pack, ensure_ascii=False).casefold()
    assert "higgsfield" not in serialized
    assert "seedance" not in serialized
    assert "local_ltx" not in serialized
    assert "anecdotal_signal" not in serialized
    assert all(item["status"] != "BLOCKED" for item in pack["technique_cards"])
    assert pack["load_order"][:5] == [item["path"] for item in pack["technique_cards"]]


def test_pack_rejects_selection_outside_three_to_seven_boundary(
    tmp_path: Path,
) -> None:
    sources = _sync_fixture(tmp_path)
    empty = _selection()
    empty["selected"] = []
    too_many = _selection()
    extra_ids = [
        "direction.sequence_meaning_first",
        "direction.shot_motivation",
        "editing.rhythmic_variation",
    ]
    too_many["selected"].extend({"id": item} for item in extra_ids)

    with pytest.raises(_module().KnowledgeVaultError, match="between 3 and 7"):
        _module().resolve_knowledge_pack(empty, sources=sources, root=tmp_path)
    with pytest.raises(_module().KnowledgeVaultError, match="between 3 and 7"):
        _module().resolve_knowledge_pack(too_many, sources=sources, root=tmp_path)


@pytest.mark.parametrize(
    ("replacement", "include_on_demand", "message"),
    [
        ("provider.topview.first_last_frame_bridge", False, "explicit opt-in"),
        ("research.hf.camera_motion_classifier", True, "BLOCKED"),
        ("provider.higgsfield.camera_preset", True, "provider_scope"),
        ("runtime.remotion_scene_reuse", True, "render_runtime"),
        ("not.a.real.technique", True, "not.a.real.technique"),
    ],
)
def test_pack_revalidates_selector_boundaries(
    tmp_path: Path,
    replacement: str,
    include_on_demand: bool,
    message: str,
) -> None:
    sources = _sync_fixture(tmp_path)
    selection = deepcopy(_selection())
    selection["selected"][0] = {"id": replacement}
    selection["query"]["include_on_demand"] = include_on_demand

    with pytest.raises(_module().KnowledgeVaultError, match=message):
        _module().resolve_knowledge_pack(selection, sources=sources, root=tmp_path)


def test_pack_rejects_a_missing_materialized_card(tmp_path: Path) -> None:
    sources = _sync_fixture(tmp_path)
    missing_id = "camera.material_macro_parallax"
    (
        tmp_path
        / "knowledge/02-TECHNIQUES/camera/camera.material_macro_parallax.md"
    ).unlink()

    with pytest.raises(_module().KnowledgeVaultError, match=missing_id):
        _module().resolve_knowledge_pack(
            _selection(), sources=sources, root=tmp_path
        )


def test_cli_audit_search_and_pack_are_machine_readable() -> None:
    audit = subprocess.run(
        [sys.executable, "scripts/knowledge-vault.py", "audit"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(audit.stdout) == {"ok": True, "findings": []}

    search = subprocess.run(
        [sys.executable, "scripts/knowledge-vault.py", "search", "photo_to_motion"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(search.stdout)[0]["entity_type"] == "technique"

    pack = subprocess.run(
        [
            sys.executable,
            "scripts/knowledge-vault.py",
            "pack",
            "--selection",
            "tests/fixtures/youtube_factory/technique_selection.valid.json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(pack.stdout)
    assert len(payload["technique_cards"]) == 5
    assert len(payload["skill_cards"]) <= 7
