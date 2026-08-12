# Obsidian Knowledge Vault Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable Obsidian vault that indexes every currently inventoried
YouTube Factory technique, skill, tool, model, toolchain item, TopView capability, and
research source while loading only route-safe knowledge into production.

**Architecture:** Canonical JSON/YAML inventories remain policy sources. A local Python
library materializes deterministic Markdown cards and Maps of Content, audits drift,
searches every status, and resolves a bounded knowledge pack from an already-approved
technique selection. MK Visual Director reads the pack; it never lets the vault select
providers, call tools, or approve a gate.

**Tech Stack:** Python 3.11, PyYAML, dataclasses, pathlib, hashlib, pytest, plain Markdown,
Obsidian core settings.

## Global Constraints

- Work only inside the isolated `유튜브공장/` project on
  `agent/youtube-factory-runtime`; do not touch the user's other production folders.
- Preserve OpenMontage as control plane and every existing Human Gate.
- Keep `config/visual-technique-registry.yaml`, `config/factory-skill-routing.yaml`,
  `config/tool-inventory.json`, lock files, and manifests as canonical policy inputs.
- Index all 43 techniques, 107 skills, 104 tools, 16 pinned creative sources, 23
  research URLs, 6 local models, 10 toolchain entries, 59 TopView capabilities, and 12
  TopView model-family records.
- Store no API key, cookie, paid output, personal workspace state, model weight, or
  copied external corpus.
- Enable no Obsidian community plugin, online sync, vector database, provider API, or
  automated TopView UI action.
- Search visibility is not activation. `REFERENCE_ONLY` and `BLOCKED` techniques never
  enter packs; `ON_DEMAND` requires explicit selector opt-in.
- Default pack budget is seven records per entity family and exactly three to seven
  selected techniques.
- All new executable behavior follows a witnessed RED-GREEN TDD cycle.

---

### Task 1: Canonical Inventory Loader

**Files:**
- Create: `tests/contracts/test_knowledge_vault.py`
- Create: `lib/knowledge_vault.py`

**Interfaces:**
- Consumes: project-local registry, inventory, manifest, lock, TopView, and research files.
- Produces: `KnowledgeSources`, `ResearchLink`, and
  `load_knowledge_sources(*, root: Path) -> KnowledgeSources`.

- [x] **Step 1: Write the failing loader test**

```python
def test_loads_every_audited_knowledge_source() -> None:
    sources = _module().load_knowledge_sources(root=ROOT)

    assert len(sources.techniques) == 43
    assert len(sources.skills) == 107
    assert len(sources.tools) == 104
    assert len(sources.creative_sources) == 16
    assert len(sources.research_links) == 23
    assert sum(link.host == "www.reddit.com" for link in sources.research_links) == 6
    assert len(sources.local_models) == 6
    assert len(sources.toolchain) == 10
    assert len(sources.topview_capabilities) == 59
    assert len(sources.topview_models) == 12
```

- [x] **Step 2: Run the loader test and witness RED**

Run:

```bash
.venv/bin/python -m pytest tests/contracts/test_knowledge_vault.py::test_loads_every_audited_knowledge_source -q
```

Expected: FAIL because `lib.knowledge_vault` does not exist.

- [x] **Step 3: Implement the minimal loader**

Implement immutable dataclasses and parse only explicit files:

```python
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
```

Read Markdown links with a deterministic regex, deduplicate by normalized URL, retain
document order, and assign Reddit links `ANECDOTAL_SIGNAL`; all other research links
receive `CITED_REFERENCE`. Merge skill routing and skill manifest entries by exact
skill name, fail on a missing counterpart, and retain `project_root` so temporary-vault
tests still resolve canonical local source paths against the real isolated factory.

- [x] **Step 4: Run the loader test and witness GREEN**

Run the command from Step 2. Expected: `1 passed`.

- [x] **Step 5: Commit the loader cycle**

```bash
git add tests/contracts/test_knowledge_vault.py lib/knowledge_vault.py
git commit -m "feat: load factory knowledge inventories"
```

---

### Task 2: Deterministic Obsidian Card and Map Sync

**Files:**
- Modify: `tests/contracts/test_knowledge_vault.py`
- Modify: `lib/knowledge_vault.py`
- Generate: `knowledge/**`

**Interfaces:**
- Consumes: `KnowledgeSources` from Task 1.
- Produces: `SyncReport` and
  `sync_vault(sources: KnowledgeSources, *, root: Path) -> SyncReport`.

- [x] **Step 1: Write failing sync, idempotence, and note-preservation tests**

```python
def test_sync_creates_complete_portable_vault(tmp_path: Path) -> None:
    sources = _module().load_knowledge_sources(root=ROOT)
    report = _module().sync_vault(sources, root=tmp_path)
    cards = list((tmp_path / "knowledge").rglob("*.md"))

    assert report.entity_cards == 380
    assert len(cards) > 380  # entity cards plus maps, templates, and guides
    assert not (tmp_path / "knowledge/.obsidian/community-plugins.json").exists()
    assert not list((tmp_path / "knowledge/.obsidian").glob("workspace*"))

def test_sync_is_idempotent_and_preserves_production_notes(tmp_path: Path) -> None:
    sources = _module().load_knowledge_sources(root=ROOT)
    first = _module().sync_vault(sources, root=tmp_path)
    card = tmp_path / "knowledge/02-TECHNIQUES/camera/camera.variable_velocity_push.md"
    card.write_text(card.read_text().replace(
        "<!-- USER-NOTES:BEGIN -->\n",
        "<!-- USER-NOTES:BEGIN -->\nVerified on the bangjja pilot.\n",
    ))
    second = _module().sync_vault(sources, root=tmp_path)
    third = _module().sync_vault(sources, root=tmp_path)

    assert first.entity_cards == 380
    assert "Verified on the bangjja pilot." in card.read_text()
    assert third.created == 0 and third.updated == 0
```

- [x] **Step 2: Run the sync tests and witness RED**

Run:

```bash
.venv/bin/python -m pytest tests/contracts/test_knowledge_vault.py -k "sync" -q
```

Expected: FAIL because `sync_vault` and `SyncReport` are absent.

- [x] **Step 3: Implement record normalization and rendering**

Add internal `CardRecord` objects with `card_id`, `entity_type`, `title`, `status`,
`relative_path`, canonical frontmatter, body sections, and typed related IDs. Build
records directly from inventory fields; do not infer relations with an LLM.

Use these stable IDs:

```text
technique: <registry id>
skill: skill.<skill name>
tool: tool.<tool name>
creative source: source.<manifest id>
research URL: research-url.<12-char sha256 of normalized URL>
model: model.<normalized model id>
toolchain: toolchain.<tool name>
TopView capability: topview-capability.<group>.<id>
TopView model family: topview-model.<kind>.<normalized family>
```

Render YAML frontmatter using `yaml.safe_dump(sort_keys=False, allow_unicode=True)` and
preserve exactly the text between:

```markdown
<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
```

Write only when bytes differ. Never delete an unexpected card during sync.

- [x] **Step 4: Generate Maps of Content and portable Obsidian settings**

Create `00-START-HERE.md`, all files under `01-MAPS/`, provider/runtime/playbook pages,
five templates, and `.obsidian/app.json`, `appearance.json`, `core-plugins.json`.
Configure native Markdown/wiki links and no community plugins. Ignore workspace files,
cache, trash, and community-plugin state in `knowledge/.gitignore`.

- [x] **Step 5: Run sync tests and witness GREEN**

Run the command from Step 2. Expected: all sync tests pass.

- [x] **Step 6: Materialize the real vault**

Run:

```bash
.venv/bin/python -c "from pathlib import Path; from lib.knowledge_vault import load_knowledge_sources, sync_vault; s=load_knowledge_sources(root=Path('.')); print(sync_vault(s, root=Path('.')))"
```

Expected: `knowledge/` contains 380 entity cards plus navigation and template files.

- [x] **Step 7: Commit cards and sync behavior**

```bash
git add lib/knowledge_vault.py tests/contracts/test_knowledge_vault.py knowledge
git commit -m "feat: materialize Obsidian factory knowledge"
```

---

### Task 3: Vault Audit and Deterministic Search

**Files:**
- Modify: `tests/contracts/test_knowledge_vault.py`
- Modify: `lib/knowledge_vault.py`

**Interfaces:**
- Consumes: `KnowledgeSources` and a materialized vault.
- Produces:
  `audit_vault(sources: KnowledgeSources, *, root: Path) -> list[str]` and
  `search_vault(query: str, *, entity_types: tuple[str, ...] | None, root: Path) -> list[dict]`.

- [x] **Step 1: Write failing behavioral tests for drift, orphan, links, and search**

```python
def test_audit_detects_policy_drift_and_orphan_without_deleting(tmp_path: Path) -> None:
    sources = _sync_fixture(tmp_path)
    card = tmp_path / "knowledge/02-TECHNIQUES/camera/camera.variable_velocity_push.md"
    card.write_text(card.read_text().replace("status: ACTIVE", "status: BLOCKED"))
    orphan = tmp_path / "knowledge/02-TECHNIQUES/camera/orphan.md"
    orphan.write_text("---\ntype: visual-technique\ntechnique_id: orphan\n---\n")

    findings = _module().audit_vault(sources, root=tmp_path)

    assert any("camera.variable_velocity_push" in item and "status" in item for item in findings)
    assert any("orphan.md" in item and "orphan" in item for item in findings)
    assert orphan.exists()

def test_search_exposes_all_statuses_but_labels_reddit_as_anecdotal(tmp_path: Path) -> None:
    _sync_fixture(tmp_path)
    motion = _module().search_vault("photo_to_motion", root=tmp_path)
    reddit = _module().search_vault("unlimited plans", root=tmp_path)

    assert motion[0]["card_id"] == "camera.material_macro_parallax"
    assert any(item["evidence_class"] == "ANECDOTAL_SIGNAL" for item in reddit)
```

- [x] **Step 2: Run audit/search tests and witness RED**

```bash
.venv/bin/python -m pytest tests/contracts/test_knowledge_vault.py -k "audit or search" -q
```

Expected: FAIL because audit and search functions do not exist.

- [x] **Step 3: Implement audit**

Parse every entity card frontmatter, report duplicate IDs and unexpected paths, render
the canonical expected card around the preserved notes, and report field-level drift.
Validate all generated `[[wikilinks]]`, local `source_path` targets, portable JSON
settings, absence of workspace/community-plugin state, and orphan cards. Return findings
without mutating the vault.

- [x] **Step 4: Implement deterministic search**

Tokenize the normalized query and score exact ID/intent/tag matches before title, then
body text. Return stable order by descending score and card ID. Include entity type,
status, evidence class, path, score, and matched terms. Never filter dormant statuses
unless `entity_types` is supplied.

- [x] **Step 5: Run audit/search tests and witness GREEN**

Run the command from Step 2. Expected: all audit/search tests pass.

- [x] **Step 6: Commit audit and search**

```bash
git add lib/knowledge_vault.py tests/contracts/test_knowledge_vault.py
git commit -m "feat: audit and search the knowledge vault"
```

---

### Task 4: Bounded Knowledge Pack

**Files:**
- Modify: `tests/contracts/test_knowledge_vault.py`
- Modify: `lib/knowledge_vault.py`
- Create: `tests/fixtures/youtube_factory/technique_selection.valid.json`

**Interfaces:**
- Consumes: the exact JSON result of `select_techniques`.
- Produces:
  `resolve_knowledge_pack(selection: dict, *, sources: KnowledgeSources, root: Path) -> dict`.

- [x] **Step 1: Write a fixed selector-result fixture and failing pack tests**

The fixture contains five selected IDs in this order:

```json
[
  "camera.variable_velocity_push",
  "typography.exact_fact_overlay",
  "transition.semantic_match_cut",
  "camera.material_macro_parallax",
  "camera.static_evidence_hold"
]
```

Tests assert that pack order matches the fixture, every card exists, linked skill/tool/
source lists contain at most seven items each, and a `TOPVIEW_MANUAL` pack contains no
Higgsfield, Seedance, local-only execution record, blocked record, or Reddit factual
guidance.

Add separate mutations for empty selection, eight selected items, on-demand without
opt-in, blocked selection, provider mismatch, runtime mismatch, and missing card. Each
must raise `KnowledgeVaultError` with the offending ID or boundary.

- [x] **Step 2: Run pack tests and witness RED**

```bash
.venv/bin/python -m pytest tests/contracts/test_knowledge_vault.py -k "pack" -q
```

Expected: FAIL because `resolve_knowledge_pack` is absent.

- [x] **Step 3: Implement route-safe pack resolution**

Revalidate selected IDs against registry status, `query.include_on_demand`, provider
scope, runtime scope, and the three-to-seven size boundary. Resolve technique cards in
input order. Add only explicit relations from technique source paths/manifest IDs,
tool `agent_skills`, and approved provider/runtime fields. Record every omitted support
record in `exclusions` with a reason. Return:

```python
{
    "registry_version": sources.catalog_version,
    "selected_ids": [...],
    "technique_cards": [...],
    "skill_cards": [...],
    "tool_cards": [...],
    "source_cards": [...],
    "source_paths": [...],
    "load_order": [...],
    "exclusions": [...],
}
```

- [x] **Step 4: Run pack tests and witness GREEN**

Run the command from Step 2. Expected: all pack tests pass.

- [x] **Step 5: Commit pack behavior**

```bash
git add lib/knowledge_vault.py tests/contracts/test_knowledge_vault.py tests/fixtures/youtube_factory/technique_selection.valid.json
git commit -m "feat: resolve route-safe knowledge packs"
```

---

### Task 5: CLI and MK Visual Director Integration

**Files:**
- Create: `scripts/knowledge-vault.py`
- Modify: `tests/contracts/test_knowledge_vault.py`
- Modify: `tests/contracts/test_youtube_factory_pipeline.py`
- Modify: `pipeline_defs/youtube-factory.yaml`
- Modify: `skills/pipelines/youtube-factory/mk-visual-director.md`
- Modify: `docs/operations/START-HERE.md`

**Interfaces:**
- Consumes: Task 1–4 library APIs.
- Produces: `sync`, `audit`, `search`, and `pack` commands plus pipeline metadata that
  points Visual Director at the audited vault.

- [x] **Step 1: Write failing CLI and pipeline integration tests**

Run the real script in a subprocess against the repository:

```python
def test_cli_audit_search_and_pack_are_machine_readable() -> None:
    audit = subprocess.run(
        [PYTHON, "scripts/knowledge-vault.py", "audit"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    assert json.loads(audit.stdout) == {"ok": True, "findings": []}

    search = subprocess.run(
        [PYTHON, "scripts/knowledge-vault.py", "search", "photo_to_motion"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    assert json.loads(search.stdout)[0]["entity_type"] == "technique"
```

The pipeline test asserts `metadata.knowledge_vault.root == "knowledge"`, audit before
selection, pack after selection, and the same seven-item budget. It also confirms all
existing Human Gates and `topview_integration_mode: manual_ui` remain unchanged.

- [x] **Step 2: Run CLI/integration tests and witness RED**

```bash
.venv/bin/python -m pytest tests/contracts/test_knowledge_vault.py tests/contracts/test_youtube_factory_pipeline.py -k "cli or knowledge_vault" -q
```

Expected: FAIL because the CLI and pipeline metadata do not exist.

- [x] **Step 3: Implement the CLI**

Use `argparse`; load sources once per command. `sync` and `audit` emit JSON reports,
`search` emits a JSON array, and `pack` reads a JSON file then emits or writes the pack.
Errors print structured JSON to stderr and exit non-zero. The script performs no
network, tool execution, checkpoint write, or provider call.

- [x] **Step 4: Wire the pipeline and Visual Director**

Add declarative knowledge-vault metadata to `youtube-factory.yaml`. Update MK Visual
Director's sequence-first recipe to run vault audit, select three to seven technique
IDs, resolve the knowledge pack, read cards in `load_order`, and treat disabled support
records as exclusions. Preserve all provider, budget, and Human Gate language.

Because subagent pressure testing is unavailable in this session, validate the edited
director instruction through the executable CLI/pipeline contract and record that
limitation in the verification report; do not claim an LLM behavior test was run.

- [x] **Step 5: Document human Obsidian use**

Add concise instructions to `START-HERE.md`: open the `knowledge/` folder as a vault,
start at `00-START-HERE.md`, use maps/search, write only inside production-note markers
or `99-INBOX`, and run audit before production.

- [x] **Step 6: Run CLI/integration tests and witness GREEN**

Run the command from Step 2. Expected: all selected tests pass.

- [x] **Step 7: Commit integration**

```bash
git add scripts/knowledge-vault.py pipeline_defs/youtube-factory.yaml skills/pipelines/youtube-factory/mk-visual-director.md docs/operations/START-HERE.md tests/contracts/test_knowledge_vault.py tests/contracts/test_youtube_factory_pipeline.py
git commit -m "feat: connect Visual Director to Obsidian knowledge"
```

---

### Task 6: Real Vault Verification and GitHub Save

**Files:**
- Create: `docs/verification/2026-08-12-obsidian-knowledge-vault.md`
- Modify: `docs/superpowers/plans/2026-08-12-obsidian-knowledge-vault.md`

**Interfaces:**
- Consumes: complete implementation and generated vault.
- Produces: reproducible verification evidence and updated draft PR.

- [x] **Step 1: Run the real sync and audit twice**

```bash
.venv/bin/python scripts/knowledge-vault.py sync
.venv/bin/python scripts/knowledge-vault.py audit
.venv/bin/python scripts/knowledge-vault.py sync
```

Expected: first audit has zero findings; second sync reports zero created/updated files.

- [x] **Step 2: Exercise real search and pack scenarios**

```bash
.venv/bin/python scripts/knowledge-vault.py search photo_to_motion
.venv/bin/python scripts/knowledge-vault.py search "unlimited plans"
.venv/bin/python scripts/knowledge-vault.py pack \
  --selection tests/fixtures/youtube_factory/technique_selection.valid.json
```

Expected: technique search finds active and dormant knowledge; Reddit search labels
results anecdotal; pack includes only route-safe bounded records.

- [x] **Step 3: Run focused regression tests**

```bash
.venv/bin/python -m pytest \
  tests/contracts/test_knowledge_vault.py \
  tests/contracts/test_visual_technique_registry.py \
  tests/contracts/test_youtube_factory_pipeline.py \
  tests/contracts/test_youtube_factory_visual_plan.py \
  tests/tools/test_topview_manual_handoff.py \
  tests/tools/test_topview_manual_ingest.py -q
```

Expected: zero failures.

- [x] **Step 4: Verify repository hygiene**

```bash
git diff --check
git status --short
```

Scan changed text for secrets, confirm no Obsidian workspace state or community plugin,
and verify generated card counts against the canonical source counts.

- [x] **Step 5: Write the verification report**

Record exact counts, commands, pass/fail output, sample search/pack results, known
limitations, and confirmation that no network/provider/Human Gate action occurred.

- [x] **Step 6: Commit, push, and update Draft PR #3**

```bash
git add docs/verification/2026-08-12-obsidian-knowledge-vault.md docs/superpowers/plans/2026-08-12-obsidian-knowledge-vault.md
git commit -m "docs: verify Obsidian knowledge vault"
git push
```

Update the existing draft PR body with the Vault scope and fresh verification. Do not
merge, approve a Human Gate, or mark the PR ready for review.
