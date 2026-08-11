from __future__ import annotations

import importlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


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

