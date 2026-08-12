# Rights-Cleared Media Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an automatic, observable `media_collection` stage that downloads only explicitly reusable real media and defers creative selection until OpenMontage prepares the edit.

**Architecture:** A dedicated rights-aware collector searches existing stock-source adapters, rejects unusable candidates before download, atomically freezes accepted files, and writes a schema-valid manifest. The Orca auto-dispatch state machine inserts this production-role stage between research and evidence lock, while the mobile projection reads a bounded progress file. Later asset selection consumes the manifest without mutating source files.

**Tech Stack:** Python 3.11, JSON Schema Draft 2020-12, pytest, OpenMontage stock-source adapters, Orca auto-dispatch, Backlot mobile dashboard.

## Global Constraints

- Gemini and all generative search APIs are excluded.
- No paid API, TopView call, generated asset, upload, or publish action is allowed.
- Restricted, unknown-rights, permission-required, purchase-required, watermarked, preview-only, and inaccessible-original items are rejected before download.
- Accepted bytes live only beneath `projects/<project-id>/assets/source/`.
- The manifest contains accepted items only and has no creative-selection field.
- Collection is idempotent and checksum-deduplicated.
- `GATE_ASSET_SELECTION` remains a single later Human Gate; collection cannot approve it.
- Existing topic approval, research, and evidence artifacts must be preserved.

---

### Task 1: Canonical manifest and pipeline contracts

**Files:**
- Create: `schemas/artifacts/media_collection_manifest.schema.json`
- Modify: `schemas/artifacts/__init__.py`
- Modify: `pipeline_defs/youtube-factory.yaml`
- Create: `skills/pipelines/youtube-factory/media-collection-director.md`
- Modify: `tests/contracts/test_youtube_factory_pipeline.py`
- Create: `tests/contracts/test_media_collection_contract.py`

**Interfaces:**
- Consumes: `research_brief`, `evidence_registry`, and the canonical project root.
- Produces: artifact name `media_collection_manifest`; stage name `media_collection`; checkpoint `checkpoint_media_collection.json`.

- [ ] **Step 1: Write failing contract tests**

```python
def test_media_collection_is_between_research_and_evidence_lock():
    manifest = load_pipeline("youtube-factory")
    order = get_stage_order(manifest)
    assert order[order.index("research") + 1] == "media_collection"
    stage = next(s for s in manifest["stages"] if s["name"] == "media_collection")
    assert stage["produces"] == ["media_collection_manifest"]
    assert stage["human_approval_default"] is False


def test_manifest_rejects_creative_selection_fields(sample_manifest):
    sample_manifest["items"][0]["selected_for_edit"] = True
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("media_collection_manifest", sample_manifest)
```

- [ ] **Step 2: Verify RED**

Run: `.venv/bin/pytest tests/contracts/test_youtube_factory_pipeline.py tests/contracts/test_media_collection_contract.py -q`

Expected: FAIL because the stage, director, schema, and artifact registration do not exist.

- [ ] **Step 3: Add the minimal schema and pipeline stage**

The schema must require top-level `schema_version`, `project_id`, `collection_status`, `generated_at`, `queries`, `source_summary`, and `items`. Each item must require `id`, `media_type`, `local_path`, `sha256`, `source`, `source_url`, `creator`, `license`, `license_url`, `public_domain_basis`, `attribution_required`, `attribution_text`, `allowed_uses`, `accessed_at`, `claim_ids`, and `technical` while setting `additionalProperties: false`.

The pipeline stage must use `pipelines/youtube-factory/media-collection-director`, require `research_brief` and `evidence_registry`, expose `rights_cleared_media_collection`, produce only `media_collection_manifest`, and have no Human Gate.

- [ ] **Step 4: Verify GREEN**

Run: `.venv/bin/pytest tests/contracts/test_youtube_factory_pipeline.py tests/contracts/test_media_collection_contract.py -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add schemas/artifacts pipeline_defs/youtube-factory.yaml skills/pipelines/youtube-factory tests/contracts
git commit -m "feat: define rights-cleared media collection contract"
```

### Task 2: Rights-first collector and atomic source library

**Files:**
- Create: `tools/video/rights_cleared_media_collection.py`
- Create: `tests/tools/test_rights_cleared_media_collection.py`

**Interfaces:**
- Consumes: `queries: list[{query, kind, claim_ids}]`, `output_dir`, optional `sources`, `max_items_per_query`, and stock-source `Candidate` objects.
- Produces: `ToolResult.data` with `manifest`, `progress`, `accepted`, `rejected_counts`, `duplicates`, and `source_errors`; writes accepted bytes beneath the passed `output_dir`.

- [ ] **Step 1: Write failing rights and idempotence tests**

```python
def test_unknown_rights_are_rejected_before_download(tmp_path, fake_source):
    fake_source.candidates = [candidate(license="", download_url="https://x/media.jpg")]
    result = run_collection(tmp_path, fake_source)
    assert result.success
    assert result.data["accepted"] == 0
    assert result.data["rejected_counts"]["unknown_rights"] == 1
    assert fake_source.download_calls == []


def test_permission_required_is_rejected_before_download(tmp_path, fake_source):
    fake_source.candidates = [candidate(license="Permission required")]
    result = run_collection(tmp_path, fake_source)
    assert result.data["accepted"] == 0
    assert fake_source.download_calls == []


def test_retry_reuses_checksum_identical_file(tmp_path, fake_source):
    fake_source.candidates = [candidate(license="CC BY 4.0")]
    first = run_collection(tmp_path, fake_source)
    second = run_collection(tmp_path, fake_source)
    assert first.data["accepted"] == 1
    assert second.data["duplicates"] == 1
    assert len(list((tmp_path / "images").glob("*"))) == 1
```

- [ ] **Step 2: Verify RED**

Run: `.venv/bin/pytest tests/tools/test_rights_cleared_media_collection.py -q`

Expected: FAIL because `RightsClearedMediaCollection` does not exist.

- [ ] **Step 3: Implement deterministic pre-download policy**

Create `RightsClearedMediaCollection(BaseTool)` with name `rights_cleared_media_collection`, cost estimate `0.0`, and a strict `evaluate_rights(candidate) -> RightsDecision`. Accept explicit Pexels, Pixabay, and Unsplash licenses; explicit public-domain statements; and CC0/CC BY/CC BY-SA licenses. Reject empty or fallback licenses, NC, ND, permission, purchase, editorial-only, preview, watermark, and unknown terms.

Search adapters first, evaluate rights before `source.download`, write downloads to a sibling staging directory, validate non-empty bytes and supported extensions, compute SHA-256, and atomically move to `images/`, `video/`, or `documents/`. Reuse an existing identical checksum without overwriting it.

- [ ] **Step 4: Verify GREEN and registry discovery**

Run: `.venv/bin/pytest tests/tools/test_rights_cleared_media_collection.py -q`

Run: `.venv/bin/python -c "from tools.tool_registry import registry; registry.discover(); assert registry.get('rights_cleared_media_collection')"`

Expected: both commands pass.

- [ ] **Step 5: Commit**

```bash
git add tools/video/rights_cleared_media_collection.py tests/tools/test_rights_cleared_media_collection.py
git commit -m "feat: collect only rights-cleared source media"
```

### Task 3: Auto-dispatch and durable stage validation

**Files:**
- Modify: `config/orca-model-routing.yaml`
- Modify: `schemas/orchestration/orca-model-routing.schema.json`
- Modify: `lib/orca_model_routing.py`
- Modify: `backlot/auto_dispatch.py`
- Modify: `backlot/auto_dispatch_worker.py`
- Modify: `backlot/orca_auto_dispatch.py`
- Modify: `schemas/mobile-dashboard/auto-dispatch-job.schema.json`
- Modify: `tests/contracts/test_orca_model_routing.py`
- Modify: `tests/backlot/test_auto_dispatch_jobs.py`
- Modify: `tests/backlot/test_auto_dispatch_worker.py`
- Modify: `tests/backlot/test_orca_auto_dispatch.py`
- Modify: `tests/backlot/test_auto_dispatch_integration.py`

**Interfaces:**
- Consumes: completed research artifacts and the production role with stock-provider secret allowlist.
- Produces: exact stage result paths `artifacts/media_collection_manifest.json`, `automation/progress/media_collection.json`, and `checkpoint_media_collection.json` plus transitively verified files referenced by the manifest.

- [ ] **Step 1: Write failing four-stage workflow tests**

```python
def test_worker_runs_collection_between_research_and_evidence_lock(project, runner):
    Coordinator(project.parent, runner).run_once()
    assert runner.calls == ["research", "media_collection", "evidence_lock", "proposal"]


def test_collection_result_rejects_missing_source_file(project, collection_result):
    with pytest.raises(JobValidationError, match="source file"):
        Coordinator(project.parent, FakeRunner([collection_result])).run_once()
```

Update job assertions so `stages` is exactly `research`, `media_collection`, `evidence_lock`, `proposal`, `stage_results.maxItems` is four, and retry resumes at the first unsettled stage.

- [ ] **Step 2: Verify RED**

Run: `.venv/bin/pytest tests/contracts/test_orca_model_routing.py tests/backlot/test_auto_dispatch_jobs.py tests/backlot/test_auto_dispatch_worker.py tests/backlot/test_orca_auto_dispatch.py tests/backlot/test_auto_dispatch_integration.py -q`

Expected: FAIL because all contracts still contain the old three-stage sequence.

- [ ] **Step 3: Implement the four-stage state machine**

Route `media_collection` to the production Hermes role. Its prompt must read the collection director, forbid Gemini and paid calls, allow writes only to `assets/source/**`, the manifest, progress file, checkpoint, and trusted result file, and require final schema/checksum validation. The coordinator must validate the manifest, every local path beneath `assets/source/`, every referenced SHA-256, the final progress schema, and the checkpoint embedding before settling the stage.

Old failed three-stage jobs remain immutable history. A retry builder may migrate only a job whose settled results form a valid prefix ending at research; it inserts `media_collection` as the next stage without changing the old job file.

- [ ] **Step 4: Verify GREEN**

Run the same focused pytest command from Step 2.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add config schemas/orchestration schemas/mobile-dashboard lib/orca_model_routing.py backlot tests/contracts/test_orca_model_routing.py tests/backlot
git commit -m "feat: auto-dispatch media collection after research"
```

### Task 4: Observable mobile progress

**Files:**
- Create: `schemas/mobile-dashboard/media-collection-progress.schema.json`
- Modify: `backlot/mobile_state.py`
- Modify: `backlot/ui/mobile.js`
- Modify: `backlot/ui/mobile.css`
- Modify: `tests/backlot/test_mobile_state.py`
- Modify: `tests/backlot/test_mobile_api.py`
- Modify: `tests/contracts/test_mobile_dashboard_contract.py`

**Interfaces:**
- Consumes: `automation/progress/media_collection.json` with state, current source, safe query summary, source counts, discovered, accepted, downloaded, duplicates, rejection counts, elapsed time, updated timestamp, and error.
- Produces: `automation.media_collection` in the mobile API and a visible progress panel when the current stage is collection.

- [ ] **Step 1: Write failing projection tests**

```python
def test_mobile_state_exposes_collection_activity(project):
    write_progress(project, state="downloading", current_source="pexels", accepted=7)
    state = build_mobile_state(project)
    assert state["automation"]["current_stage"] == "media_collection"
    assert state["automation"]["media_collection"]["state"] == "downloading"
    assert state["automation"]["media_collection"]["accepted"] == 7


def test_malformed_progress_is_not_exposed(project):
    (project / "automation/progress/media_collection.json").write_text("{}")
    assert build_mobile_state(project)["automation"]["media_collection"] is None
```

- [ ] **Step 2: Verify RED**

Run: `.venv/bin/pytest tests/backlot/test_mobile_state.py tests/backlot/test_mobile_api.py tests/contracts/test_mobile_dashboard_contract.py -q`

Expected: FAIL because the projection and UI contract do not expose collection progress.

- [ ] **Step 3: Implement bounded projection and UI card**

Validate the progress file before projecting it. Render current source, completed sources, discovered, accepted, downloaded, duplicates, aggregate rejected counts, elapsed time, last activity, and error. Do not expose API keys, direct signed URLs, or unrestricted error payloads.

- [ ] **Step 4: Verify GREEN**

Run the same focused pytest command from Step 2.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add schemas/mobile-dashboard backlot/mobile_state.py backlot/ui/mobile.js backlot/ui/mobile.css tests/backlot tests/contracts/test_mobile_dashboard_contract.py
git commit -m "feat: show live rights-cleared collection progress"
```

### Task 5: End-to-end safety and existing-pilot readiness

**Files:**
- Modify: `docs/operations/mobile-dashboard.md`
- Create: `reviews/2026-08-12-media-collection-verification.md`
- Test: `tests/contracts/test_media_collection_contract.py`
- Test: `tests/backlot/test_auto_dispatch_integration.py`

**Interfaces:**
- Consumes: all contracts and implementation from Tasks 1-4.
- Produces: a verification report with exact commands, results, known limitations, and current-pilot migration decision.

- [ ] **Step 1: Add an integration fixture with accepted, rejected, duplicate, and failed-source candidates**

The fixture must prove that accepted bytes exist and match hashes, rejected candidates were never downloaded, duplicate bytes produce one file, one source error preserves other successes, no creative-selection field exists, and the completed checkpoint embeds the exact manifest object.

- [ ] **Step 2: Run focused and full verification**

Run: `.venv/bin/pytest tests/contracts/test_media_collection_contract.py tests/contracts/test_youtube_factory_pipeline.py tests/contracts/test_orca_model_routing.py tests/backlot -q`

Run: `.venv/bin/pytest tests/contracts -q`

Run: `git diff --check`

Expected: all commands pass with no warnings or whitespace errors.

- [ ] **Step 3: Perform a no-network dry run for the current pilot**

Read the current topic/research checkpoints and construct the next job state without calling any external provider. Confirm that existing artifact hashes remain unchanged, `media_collection` is next when research is complete, and no Human Gate state is fabricated.

- [ ] **Step 4: Write the verification report and operations note**

Record the exact test counts, current source readiness, migration result, and the explicit statement that no paid/Gemini/TopView/generation call occurred.

- [ ] **Step 5: Commit**

```bash
git add docs/operations/mobile-dashboard.md reviews/2026-08-12-media-collection-verification.md
git commit -m "docs: verify rights-cleared collection workflow"
```

