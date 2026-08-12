# Cinematic Direction Principles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add provider-neutral camera, spatial, physical, performance, and reference-direction controls to MK Visual Director; preserve the complete paraphrased research in Obsidian; and carry selected controls into the manual TopView handoff.

**Architecture:** Six concise techniques remain the operational layer selected per sequence. A typed `cinematic_direction` block carries only shot-relevant controls through `visual_plan` and the TopView job packet. Four hand-authored Obsidian research notes preserve comprehensive paraphrased knowledge as `REFERENCE_ONLY`; they are searchable and audited but cannot enter normal production knowledge packs.

**Tech Stack:** Python 3.11, pytest, JSON Schema draft 2020-12, PyYAML, Markdown/Obsidian, OpenMontage artifact and tool contracts.

## Global Constraints

- Do not copy, vendor, quote, or redistribute the reviewed CINEDANCE, ACTING, or LIRA Markdown files.
- Use original project wording and preserve source URLs and SHA-256 audit hashes only as provenance.
- Keep TopView manual UI only: no API, MCP, browser automation, payment, or Human Gate changes.
- Keep Higgsfield and Seedance vocabulary isolated from `TOPVIEW_MANUAL` and generic routes.
- Keep normal knowledge packs bounded to 3–7 techniques; comprehensive research notes remain `REFERENCE_ONLY` and outside `load_order`.
- Require `cinematic_direction` for `TOPVIEW_HANDOFF` and `LOCAL_LTX`; allow it optionally elsewhere.
- Preserve existing user files and unrelated worktree changes.

---

## File Map

- `config/visual-technique-registry.yaml`: six new generic selectable principles.
- `schemas/artifacts/visual_plan.schema.json`: typed shot-level cinematic direction contract.
- `lib/visual_plan_validator.py`: cross-field beat ordering, duration, and reference-role checks.
- `tests/fixtures/youtube_factory/visual_plan.valid.json`: executable representative contract.
- `schemas/artifacts/topview_job_pack.schema.json`: typed handoff copy of cinematic direction and reference controls.
- `tools/video/topview_manual_handoff.py`: preserve direction and role-aware frozen references.
- `skills/pipelines/youtube-factory/mk-visual-director.md`: authoring and selective-loading procedure.
- `config/cinematic-direction-coverage.yaml`: canonical coverage IDs and source provenance.
- `knowledge/10-RESEARCH/cinematic-direction/*.md`: comprehensive paraphrased research and map.
- `lib/knowledge_vault.py`: synchronize, index, search, and audit the reference-only research collection.
- `tests/contracts/test_visual_technique_registry.py`: selection and provider-neutrality behavior.
- `tests/contracts/test_youtube_factory_visual_plan.py`: visual direction contract behavior.
- `tests/tools/test_topview_manual_handoff.py`: manual handoff behavior.
- `tests/contracts/test_knowledge_vault.py`: coverage, search, audit, and pack-exclusion behavior.

---

### Task 1: Register Six Provider-Neutral Principles

**Files:**
- Modify: `tests/contracts/test_visual_technique_registry.py`
- Modify: `config/visual-technique-registry.yaml`

**Interfaces:**
- Consumes: `select_techniques(intents, phase, provider_scope, render_runtime)`.
- Produces: six `ACTIVE` generic IDs usable by later visual plans.

- [ ] **Step 1: Write the failing selection test**

Add a table-driven test that queries these intent/ID pairs with `provider_scope="TOPVIEW_MANUAL"` and verifies selection without provider-specific leakage:

```python
@pytest.mark.parametrize(
    ("intent", "technique_id"),
    [
        ("opening_frame", "direction.opening_frame_intent"),
        ("spatial_blocking", "continuity.explicit_spatial_blocking"),
        ("behavioral_performance", "direction.behavioral_performance_beats"),
        ("optical_result", "camera.observable_optical_result"),
        ("physical_causality", "direction.physical_causality"),
        ("reference_role", "continuity.reference_role_binding"),
    ],
)
def test_generic_cinematic_principles_are_route_safe(intent, technique_id):
    result = _module().select_techniques(
        intents=[intent], phase="visual_plan", provider_scope="TOPVIEW_MANUAL"
    )
    selected = {item["id"]: item for item in result["selected"]}
    assert technique_id in selected
    assert selected[technique_id]["provider_scopes"] == ["GENERIC"]
```

- [ ] **Step 2: Run the test and confirm RED**

Run: `.venv/bin/pytest tests/contracts/test_visual_technique_registry.py -q`

Expected: six cases fail because the IDs do not exist.

- [ ] **Step 3: Add the six minimal registry records**

Use `status: ACTIVE`, `selectable: true`, `provider_scopes: [GENERIC]`, `render_runtimes: [ANY]`, the approved project-local design specification as the initial source path, and intent-specific directives. Do not add provider names or model syntax. Task 4 replaces the initial source path with the corresponding comprehensive project note after those notes exist.

- [ ] **Step 4: Run registry tests and audit**

Run:

```bash
.venv/bin/pytest tests/contracts/test_visual_technique_registry.py -q
.venv/bin/python scripts/visual-techniques.py audit
```

Expected: all tests pass and audit reports no findings.

- [ ] **Step 5: Commit**

```bash
git add config/visual-technique-registry.yaml tests/contracts/test_visual_technique_registry.py
git commit -m "feat: add provider-neutral cinematic direction techniques"
```

### Task 2: Type and Validate Shot-Level Cinematic Direction

**Files:**
- Modify: `tests/contracts/test_youtube_factory_visual_plan.py`
- Modify: `tests/fixtures/youtube_factory/visual_plan.valid.json`
- Modify: `schemas/artifacts/visual_plan.schema.json`
- Modify: `lib/visual_plan_validator.py`

**Interfaces:**
- Produces: `shot.cinematic_direction` containing `opening_frame`, `spatial_blocking`, `optical_result`, `timed_beats`, `physical_cues`, optional `performance`, and optional `reference_bindings`.
- Enforces: generated routes require the block; beats are ordered and bounded; reference paths bind exactly once.

- [ ] **Step 1: Add failing contract tests**

Add tests that mutate a valid plan and assert these observable failures:

```python
def test_generated_motion_route_requires_cinematic_direction():
    plan = _load("visual_plan.valid.json")
    plan["sequences"][0]["shots"][1].pop("cinematic_direction")
    errors = _validator_module().validate_visual_plan(
        plan, _load("evidence_registry.valid.json")
    )
    assert "SHOT_002: generated motion route requires cinematic_direction" in errors

def test_cinematic_beats_must_be_ordered_and_fit_duration():
    plan = _load("visual_plan.valid.json")
    beats = plan["sequences"][0]["shots"][1]["cinematic_direction"]["timed_beats"]
    beats[1]["start_seconds"] = beats[0]["end_seconds"] - 0.25
    errors = _validator_module().validate_visual_plan(
        plan, _load("evidence_registry.valid.json")
    )
    assert "SHOT_002: cinematic timed beats overlap" in errors

def test_generation_references_require_exact_role_bindings():
    plan = _load("visual_plan.valid.json")
    plan["sequences"][0]["shots"][1]["cinematic_direction"][
        "reference_bindings"
    ] = []
    errors = _validator_module().validate_visual_plan(
        plan, _load("evidence_registry.valid.json")
    )
    assert "SHOT_002: generation references and reference_bindings must match" in errors
```

Also validate that a material-only direction without `performance` passes.

- [ ] **Step 2: Run the tests and confirm RED**

Run: `.venv/bin/pytest tests/contracts/test_youtube_factory_visual_plan.py -q`

Expected: missing fixture field/key failures or missing semantic findings.

- [ ] **Step 3: Add the representative fixture and JSON Schema definitions**

Populate `SHOT_002` with a hand-checked two-beat direction. Define strict nested objects with `additionalProperties: false`; require the direction block in the existing conditional for `TOPVIEW_HANDOFF` and `LOCAL_LTX`.

- [ ] **Step 4: Add minimal semantic validation**

In `validate_visual_plan`, check:

```python
generated_motion = route in {"TOPVIEW_HANDOFF", "LOCAL_LTX"}
if generated_motion and not direction:
    errors.append(f"{shot_id}: generated motion route requires cinematic_direction")

previous_end = 0.0
for beat in direction.get("timed_beats", []):
    start = float(beat["start_seconds"])
    end = float(beat["end_seconds"])
    if start < previous_end:
        errors.append(f"{shot_id}: cinematic timed beats overlap")
        break
    if end > float(shot["duration_seconds"]):
        errors.append(f"{shot_id}: cinematic timed beat exceeds shot duration")
        break
    previous_end = end
```

Compare `generation_brief.reference_paths` with binding paths as duplicate-free sets and report the exact mismatch finding.

- [ ] **Step 5: Run visual-plan tests**

Run: `.venv/bin/pytest tests/contracts/test_youtube_factory_visual_plan.py -q`

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add schemas/artifacts/visual_plan.schema.json lib/visual_plan_validator.py tests/fixtures/youtube_factory/visual_plan.valid.json tests/contracts/test_youtube_factory_visual_plan.py
git commit -m "feat: add cinematic direction visual-plan contract"
```

### Task 3: Preserve Direction and Reference Roles in TopView Handoff

**Files:**
- Modify: `tests/tools/test_topview_manual_handoff.py`
- Modify: `schemas/artifacts/topview_job_pack.schema.json`
- Modify: `tools/video/topview_manual_handoff.py`

**Interfaces:**
- Consumes: valid `visual_plan` cinematic direction and reference bindings.
- Produces: job-level `cinematic_direction` plus frozen references with `role`, `controls`, and `excludes`.

- [ ] **Step 1: Add failing handoff assertions**

Extend the real handoff test:

```python
assert topview_job["cinematic_direction"] == plan_shot["cinematic_direction"]
assert topview_job["reference_files"][0]["role"] == "ENVIRONMENT_REFERENCE"
assert topview_job["reference_files"][0]["controls"] == [
    "workspace geometry", "material character", "light direction"
]
assert "camera framing" in topview_job["reference_files"][0]["excludes"]
instructions = Path(result.data["instructions_path"]).read_text(encoding="utf-8")
assert "첫 프레임" in instructions
assert "시간 비트" in instructions
assert "레퍼런스 역할" in instructions
```

Add a failure test for a missing role binding that verifies no outbox is created.

- [ ] **Step 2: Run the tests and confirm RED**

Run: `.venv/bin/pytest tests/tools/test_topview_manual_handoff.py -q`

Expected: missing job fields and role metadata.

- [ ] **Step 3: Extend schema and tool minimally**

Build a path-indexed binding map before freezing references, reject mismatches, copy role/controls/excludes to each frozen record, preserve `cinematic_direction` unchanged, and format its essential controls in the human instructions. Keep `operator_policy` unchanged.

- [ ] **Step 4: Run handoff and ingest tests**

Run:

```bash
.venv/bin/pytest tests/tools/test_topview_manual_handoff.py -q
.venv/bin/pytest tests/tools/test_topview_manual_ingest.py -q
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add schemas/artifacts/topview_job_pack.schema.json tools/video/topview_manual_handoff.py tests/tools/test_topview_manual_handoff.py
git commit -m "feat: carry cinematic direction into TopView handoff"
```

### Task 4: Preserve and Audit the Comprehensive Obsidian Knowledge

**Files:**
- Modify: `tests/contracts/test_knowledge_vault.py`
- Modify: `config/visual-technique-registry.yaml`
- Create: `config/cinematic-direction-coverage.yaml`
- Create: `knowledge/10-RESEARCH/cinematic-direction/Camera-Spatial-Physics-Direction.md`
- Create: `knowledge/10-RESEARCH/cinematic-direction/Behavioral-Performance-Direction.md`
- Create: `knowledge/10-RESEARCH/cinematic-direction/Image-Reference-Asset-Direction.md`
- Create: `knowledge/10-RESEARCH/cinematic-direction/Cinematic-Direction-Map.md`
- Modify: `lib/knowledge_vault.py`

**Interfaces:**
- Consumes: canonical coverage manifest and four project-authored Markdown notes.
- Produces: searchable `research_synthesis` catalog records; `audit_vault` findings for missing, duplicate, drifted, or broken research knowledge; no production-pack inclusion.

- [ ] **Step 1: Add failing vault behavior tests**

Add tests proving that a temporary sync:

```python
research_dir = tmp_path / "knowledge/10-RESEARCH/cinematic-direction"
assert len(list(research_dir.glob("*.md"))) == 4
results = module.search_vault("시선 호흡 전술", root=tmp_path)
assert results[0]["entity_type"] == "research_synthesis"
assert results[0]["status"] == "REFERENCE_ONLY"
pack = module.resolve_knowledge_pack(_selection(), sources=sources, root=tmp_path)
assert all("10-RESEARCH" not in path for path in pack["load_order"])
assert module.audit_vault(sources, root=tmp_path) == []
```

Then tamper one coverage ID in a copied note and assert the audit returns a coverage mismatch. Existing wikilink auditing proves the Map links resolve.

- [ ] **Step 2: Run the vault tests and confirm RED**

Run: `.venv/bin/pytest tests/contracts/test_knowledge_vault.py -q`

Expected: missing files/catalog records or missing audit finding.

- [ ] **Step 3: Create the coverage manifest and four original notes**

The manifest lists each expected note path, card ID, title, domain, and exact `coverage_ids`; records these source URLs and audit hashes:

```yaml
sources:
  - url: https://www.all-ai.de/media/textfiles/cinedance-skill.md
    sha256: 7b0e4f8dad1515631f54b6b6401b333adbdbbe3b8832a71c6ac78fe5d20b95f8
  - url: https://www.all-ai.de/media/textfiles/acting-skill.md
    sha256: 8841c5d1155ee9347d5fc302a2f0fdac76fed21070c94bf01741821ea1c42365
  - url: https://www.all-ai.de/media/textfiles/lira-skill.md
    sha256: 329240f47888689e16576682c5de52dd2c1075b1fe5482068c647dad9f03544a
```

Write comprehensive Korean paraphrases. Do not reproduce source sentences, prompt blocks, examples, or provider personas.

After all three domain notes exist, update each of the six generic technique records so
its `source.path` points to the corresponding note under
`knowledge/10-RESEARCH/cinematic-direction/`, then run the visual-technique audit.

- [ ] **Step 4: Extend vault synchronization, indexing, and audit**

Load the coverage manifest from `sources.project_root`. Copy the four canonical notes during alternate-root sync, append them to `.factory-catalog.json` as `research_synthesis`, include `coverage_ids` in structured search fields, and audit:

- required frontmatter values;
- exact per-note coverage set;
- global uniqueness of non-empty coverage IDs;
- presence of all four notes;
- reference-only status;
- unchanged generic pack resolver behavior.

- [ ] **Step 5: Run vault tests and live vault sync/audit**

Run:

```bash
.venv/bin/pytest tests/contracts/test_knowledge_vault.py -q
.venv/bin/python scripts/knowledge-vault.py sync
.venv/bin/python scripts/knowledge-vault.py audit
.venv/bin/python scripts/knowledge-vault.py search "시선 호흡 전술"
```

Expected: tests pass, audit has no findings, and search returns the behavioral research note as `REFERENCE_ONLY`.

- [ ] **Step 6: Commit**

```bash
git add config/cinematic-direction-coverage.yaml knowledge/10-RESEARCH lib/knowledge_vault.py tests/contracts/test_knowledge_vault.py knowledge/.factory-catalog.json knowledge/01-MAPS knowledge/02-TECHNIQUES
git commit -m "feat: preserve cinematic direction research in Obsidian"
```

### Task 5: Wire MK Visual Director to the New Contract

**Files:**
- Modify: `skills/pipelines/youtube-factory/mk-visual-director.md`

**Interfaces:**
- Consumes: selected generic techniques and bounded knowledge pack.
- Produces: a valid `cinematic_direction` block without loading reference-only notes by default.

- [ ] **Step 1: Update the director procedure**

Document the required authoring order:

1. meaning and evidence;
2. selected technique set;
3. opening frame and spatial blocking;
4. optical result and timed beats;
5. physical causality;
6. optional visible performance;
7. explicit reference roles;
8. route and fallback.

State that full research notes may be opened only for a difficult shot, research, or maintenance, never added to normal `load_order`. Do not add provider syntax or a command that invokes a provider.

- [ ] **Step 2: Validate the instruction against executable contracts**

Run:

```bash
.venv/bin/pytest tests/contracts/test_youtube_factory_visual_plan.py tests/contracts/test_visual_technique_registry.py tests/tools/test_topview_manual_handoff.py -q
.venv/bin/python scripts/visual-techniques.py audit
.venv/bin/python scripts/knowledge-vault.py audit
```

Expected: all pass; the artifact and tool behavior, rather than prose matching, prove the instruction is executable.

- [ ] **Step 3: Commit**

```bash
git add skills/pipelines/youtube-factory/mk-visual-director.md
git commit -m "docs: direct cinematic controls through MK Visual Director"
```

### Task 6: Full Regression and Delivery Verification

**Files:**
- Create: `docs/verification/2026-08-12-cinematic-direction-principles.md`

**Interfaces:**
- Consumes: all implementation commits.
- Produces: fresh verification evidence and a concise delivery record.

- [ ] **Step 1: Run focused contracts**

```bash
.venv/bin/pytest \
  tests/contracts/test_visual_technique_registry.py \
  tests/contracts/test_youtube_factory_visual_plan.py \
  tests/contracts/test_knowledge_vault.py \
  tests/tools/test_topview_manual_handoff.py \
  tests/tools/test_topview_manual_ingest.py -q
```

- [ ] **Step 2: Run the complete test suite**

Run: `.venv/bin/pytest -q`

Expected: zero failures.

- [ ] **Step 3: Run deterministic audits and repository checks**

```bash
.venv/bin/python scripts/visual-techniques.py audit
.venv/bin/python scripts/knowledge-vault.py audit
git diff --check
git status --short
```

Expected: both audits clean, no whitespace errors, only the intended verification note uncommitted before the final commit.

- [ ] **Step 4: Record exact evidence and commit**

Write the commands, counts, and key manual-policy assertions to the verification note, then run the focused suite once more before committing.

```bash
git add docs/verification/2026-08-12-cinematic-direction-principles.md
git commit -m "docs: verify cinematic direction integration"
```
