# Media Relevance Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every future media collection automatically run event-relevance review, quarantine unrelated assets, supplement missing reusable news/archive material, and expose only reviewed candidates to OpenMontage by default.

**Architecture:** Add a mandatory `media_relevance_review` stage after `media_collection`. A deterministic local reviewer combines identity metadata, explicit mismatch rules, technical evidence, and optional local visual evidence; a separate archive supplement helper invokes the existing rights-cleared collector only for uncovered exact-event lanes. The immutable collection manifest remains unchanged, while one canonical review artifact binds the base manifest, any supplement manifest, all decisions, and coverage.

**Tech Stack:** Python 3.11, JSON Schema Draft 2020-12, pytest, existing OpenMontage stock-source adapters, local FFmpeg frame sampling, optional local CLIP/visual-understanding runtime, vanilla mobile JavaScript/CSS.

## Global Constraints

- Preserve the original 75 source files and `media_collection_manifest.json` byte-for-byte.
- No Gemini, paid provider, TopView dispatch, publication, or automatic Human Gate approval.
- Permission-required, purchase-only, editorial-only, unknown-rights, watermarked, preview-only, and inaccessible-original media must not be downloaded.
- Query text and inherited `claim_ids` are not event-identity evidence.
- Visual similarity cannot promote an item to `event_direct` or `news_report` without positive identity metadata.
- Missing visual analysis fails closed to `unknown` when visual confirmation is required.
- `unrelated` and `unknown` never enter automatic OpenMontage candidates.
- `generic_broll` is excluded by default and requires an explicit approved VisualPlan request later.
- Every new project uses `research -> media_collection -> media_relevance_review -> evidence_lock -> proposal`.
- Historical completed jobs remain readable and immutable; they are not silently reactivated.

---

### Task 1: Canonical review contract

**Files:**
- Create: `schemas/artifacts/media_relevance_review.schema.json`
- Modify: `schemas/artifacts/__init__.py`
- Create: `schemas/mobile-dashboard/media-relevance-progress.schema.json`
- Test: `tests/contracts/test_media_relevance_review_contract.py`

**Interfaces:**
- Consumes: media IDs and SHA-256-bound records from `media_collection_manifest`.
- Produces: validated `media_relevance_review` artifact with `base_manifest_sha256`, embedded optional `supplement_manifest`, `decisions`, `coverage`, and category counts.

- [ ] **Step 1: Write failing schema tests**

```python
def test_review_requires_manifest_binding_and_one_decision_per_item():
    review = review_fixture()
    validate_artifact("media_relevance_review", review)
    broken = deepcopy(review)
    broken["base_manifest_sha256"] = "not-a-hash"
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("media_relevance_review", broken)

def test_event_direct_requires_identity_evidence():
    review = review_fixture(category="event_direct", identity_evidence=[])
    with pytest.raises(jsonschema.ValidationError):
        validate_artifact("media_relevance_review", review)
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/contracts/test_media_relevance_review_contract.py -v`  
Expected: FAIL because the artifact and progress schemas do not exist.

- [ ] **Step 3: Implement strict schemas**

Define category enum `event_direct|news_report|official_record|explanatory|generic_broll|unrelated|unknown`, eligibility enum `eligible|excluded|held`, 0-100 score, evidence arrays, review methods, ISO timestamp, coverage enum `covered|partial|missing`, and `additionalProperties: false` at every object boundary. Register `media_relevance_review` in `ARTIFACT_NAMES`.

- [ ] **Step 4: Run GREEN and contract suite**

Run: `.venv/bin/python -m pytest tests/contracts/test_media_relevance_review_contract.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add schemas/artifacts schemas/mobile-dashboard tests/contracts/test_media_relevance_review_contract.py
git commit -m "feat: define media relevance review contract"
```

### Task 2: Deterministic local relevance reviewer

**Files:**
- Create: `tools/video/media_relevance_review.py`
- Create: `tests/tools/test_media_relevance_review.py`

**Interfaces:**
- Consumes: `review_manifest(manifest, manifest_sha256, topic_identity, visual_evidence=None)`.
- Produces: a complete schema-valid review object; no filesystem mutation and no network call.

- [ ] **Step 1: Write failing behavior tests**

```python
def test_query_claim_cannot_promote_ukraine_war_ruins():
    item = manifest_item(
        media_id="MEDIA_BAD",
        source_url="https://pexels.com/video/war-in-ukraine-1/",
        claim_ids=["CLAIM_WARNING_CRACKS"],
    )
    decision = review_one(item, rana_plaza_identity())
    assert decision["category"] == "unrelated"
    assert decision["eligibility"] == "excluded"

def test_exact_rana_plaza_news_metadata_is_news_report():
    item = manifest_item(
        media_id="MEDIA_NEWS",
        source_url="https://archive.org/details/rana-plaza-news-report-2013",
        title="Rana Plaza collapse news report, Savar, 24 April 2013",
    )
    decision = review_one(item, rana_plaza_identity())
    assert decision["category"] == "news_report"
    assert decision["identity_evidence"]

def test_ambiguous_visual_item_fails_closed_without_visual_evidence():
    decision = review_one(manifest_item(source_url="https://example.test/asset/1"), rana_plaza_identity())
    assert decision["category"] == "unknown"
    assert decision["eligibility"] == "held"
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/tools/test_media_relevance_review.py -v`  
Expected: FAIL because the reviewer module does not exist.

- [ ] **Step 3: Implement minimal reviewer**

Implement normalized metadata extraction, positive event identity terms, explicit geographic/event mismatch terms, category rules, optional visual evidence, coverage aggregation, and deterministic ordering. Treat `claim_ids` only as intended coverage labels. Do not load a model or access the network in this module.

- [ ] **Step 4: Run GREEN**

Run: `.venv/bin/python -m pytest tests/tools/test_media_relevance_review.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/video/media_relevance_review.py tests/tools/test_media_relevance_review.py
git commit -m "feat: classify collected media relevance"
```

### Task 3: Archive supplement and local visual evidence

**Files:**
- Create: `tools/video/media_archive_supplement.py`
- Create: `tools/video/media_visual_evidence.py`
- Modify: `tools/analysis/video_analyzer.py` only if a public frame-sampling helper must be exposed without duplicating FFmpeg logic.
- Test: `tests/tools/test_media_archive_supplement.py`
- Test: `tests/tools/test_media_visual_evidence.py`

**Interfaces:**
- Consumes: first-pass review coverage, topic identity, canonical `assets/source` directory, registered source adapters.
- Produces: an in-memory rights-cleared supplement manifest plus visual-evidence records keyed by media ID.

- [ ] **Step 1: Write failing supplement tests**

```python
def test_archive_queries_are_exact_event_and_only_fill_missing_lanes():
    specs = build_supplement_queries(rana_plaza_identity(), missing={"news", "official"})
    assert {q["lane"] for q in specs} == {"news", "official"}
    assert all("Rana Plaza" in q["query"] or "ILO Rana Plaza" in q["query"] for q in specs)

def test_supplement_uses_only_archive_allowlist():
    assert ARCHIVE_SOURCE_ALLOWLIST == (
        "archive_org", "wikimedia", "nara", "loc", "pond5_pd"
    )
```

- [ ] **Step 2: Run supplement RED**

Run: `.venv/bin/python -m pytest tests/tools/test_media_archive_supplement.py -v`  
Expected: FAIL because the supplement module does not exist.

- [ ] **Step 3: Implement supplement helper**

Build exact-event query specs only for missing coverage lanes and invoke `RightsClearedMediaCollection` with the fixed archive source allowlist. Return an empty completed supplement when no eligible source returns reusable material. Never substitute stock providers on failure.

- [ ] **Step 4: Write and run visual-evidence RED**

```python
def test_video_visual_evidence_samples_first_middle_last_and_scene_frames(tmp_path):
    result = build_visual_evidence(video_fixture(tmp_path), tmp_path / "frames")
    assert {"first", "middle", "last"}.issubset(set(result["sample_roles"]))

def test_unavailable_local_model_returns_unavailable_not_positive():
    result = classify_frames([], model_loader=lambda: None)
    assert result == {"status": "unavailable", "labels": [], "confidence": None}
```

Run: `.venv/bin/python -m pytest tests/tools/test_media_visual_evidence.py -v`  
Expected: FAIL because the visual-evidence module does not exist.

- [ ] **Step 5: Implement local evidence helper and run GREEN**

Use FFmpeg for deterministic representative frames and the existing local visual-understanding/CLIP path only when already available. Record `unavailable` without downloading a model during an automatic run. Do not let visual labels establish event identity.

Run: `.venv/bin/python -m pytest tests/tools/test_media_archive_supplement.py tests/tools/test_media_visual_evidence.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/video/media_archive_supplement.py tools/video/media_visual_evidence.py tools/analysis/video_analyzer.py tests/tools/test_media_archive_supplement.py tests/tools/test_media_visual_evidence.py
git commit -m "feat: supplement reviewed media from archives"
```

### Task 4: Mandatory automatic review stage

**Files:**
- Create: `tools/video/media_review_pipeline.py`
- Modify: `backlot/auto_dispatch.py`
- Modify: `backlot/auto_dispatch_worker.py`
- Modify: `backlot/orca_auto_dispatch.py`
- Modify: `schemas/mobile-dashboard/auto-dispatch-job.schema.json`
- Modify: `config/orca-model-routing.yaml`
- Modify: `schemas/orchestration/orca-model-routing.schema.json`
- Modify: `pipeline_defs/youtube-factory.yaml`
- Create: `skills/pipelines/youtube-factory/media-relevance-review-director.md`
- Test: `tests/backlot/test_auto_dispatch_jobs.py`
- Test: `tests/backlot/test_auto_dispatch_worker.py`
- Test: `tests/backlot/test_orca_auto_dispatch.py`
- Test: `tests/contracts/test_orca_model_routing.py`

**Interfaces:**
- Consumes: canonical base manifest and topic/research identity.
- Produces: `artifacts/media_relevance_review.json`, `automation/progress/media_relevance_review.json`, and `checkpoint_media_relevance_review.json` before evidence lock can start.

- [ ] **Step 1: Write failing stage-order tests**

```python
def test_new_jobs_always_review_after_collection():
    job = build_topic_job(project, receipt, checkpoint_hash, NOW, topic_selection=selection)
    assert job["stages"] == [
        "research", "media_collection", "media_relevance_review", "evidence_lock", "proposal"
    ]

def test_worker_cannot_skip_review_to_evidence_lock():
    worker = Coordinator(projects, runner_that_returns_collection_then_evidence())
    worker.process_next()
    assert load_job(job_path)["state"] == "failed"
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/backlot/test_auto_dispatch_jobs.py tests/backlot/test_auto_dispatch_worker.py -v`  
Expected: FAIL because current jobs use four stages.

- [ ] **Step 3: Implement stage contract and pipeline runner**

Add the five-stage current contract and retain old four-stage and three-stage contracts as terminal historical variants. The new pipeline runner executes first review, exact archive supplement when coverage is missing, visual evidence where locally available, final review, atomic artifact/progress writes, and a completed non-human checkpoint. Bind the review to the exact base manifest hash and all supplement item hashes.

- [ ] **Step 4: Add Orca production prompt and routing**

Route `media_relevance_review` to the production role. Require the local pipeline runner and exact output paths. Forbid fabricated categories, provider fallback, restricted news downloads, and success when the artifact fails schema validation.

- [ ] **Step 5: Run GREEN and integration tests**

Run: `.venv/bin/python -m pytest tests/backlot/test_auto_dispatch_jobs.py tests/backlot/test_auto_dispatch_worker.py tests/backlot/test_orca_auto_dispatch.py tests/contracts/test_orca_model_routing.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add backlot tools/video/media_review_pipeline.py schemas config pipeline_defs skills/pipelines/youtube-factory/media-relevance-review-director.md tests/backlot tests/contracts/test_orca_model_routing.py
git commit -m "feat: require review after every media collection"
```

### Task 5: Reviewed inventory for dashboard and OpenMontage

**Files:**
- Create: `lib/reviewed_media_inventory.py`
- Modify: `backlot/media_library.py`
- Modify: `backlot/mobile_state.py`
- Modify: `backlot/ui/mobile.js`
- Modify: `backlot/ui/mobile.css`
- Test: `tests/backlot/test_mobile_state.py`
- Test: `tests/backlot/test_mobile_api.py`
- Test: `tests/contracts/test_mobile_dashboard_contract.py`
- Create: `tests/lib/test_reviewed_media_inventory.py`

**Interfaces:**
- Consumes: base manifest plus canonical media relevance review.
- Produces: `all_reviewed_items(project)` for dashboard and `eligible_items_for_openmontage(project, allow_generic=False)` for production selection.

- [ ] **Step 1: Write failing inventory tests**

```python
def test_openmontage_inventory_excludes_unrelated_unknown_and_generic_by_default(project):
    ids = {item["id"] for item in eligible_items_for_openmontage(project)}
    assert ids == {"MEDIA_EVENT", "MEDIA_NEWS", "MEDIA_OFFICIAL", "MEDIA_EXPLAIN"}

def test_dashboard_defaults_to_recommended_but_preserves_excluded_filter(project):
    state = build_mobile_state(project)
    assert state["asset_library"]["default_filter"] == "recommended"
    assert state["asset_library"]["counts"]["excluded"] == 3
```

- [ ] **Step 2: Run RED**

Run: `.venv/bin/python -m pytest tests/lib/test_reviewed_media_inventory.py tests/backlot/test_mobile_state.py -v`  
Expected: FAIL because reviewed inventory and categories do not exist.

- [ ] **Step 3: Implement inventory and UI filters**

Merge base and supplement records by exact media ID and hash. Project category, eligibility, short usefulness reason, and preview URLs without exposing internal license fields in the normal UI. Add filters 추천 자료, 사건 직접, 뉴스·보도, 공식 기록, 설명 자료, 일반 B-roll, 보류·제외. Default to recommended. Add `수집 자료 검수` and coverage to 현황.

- [ ] **Step 4: Run GREEN**

Run: `.venv/bin/python -m pytest tests/lib/test_reviewed_media_inventory.py tests/backlot/test_mobile_state.py tests/backlot/test_mobile_api.py tests/contracts/test_mobile_dashboard_contract.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add lib/reviewed_media_inventory.py backlot tests/lib/test_reviewed_media_inventory.py tests/backlot tests/contracts/test_mobile_dashboard_contract.py
git commit -m "feat: show only reviewed production assets by default"
```

### Task 6: Migrate and verify the Rana Plaza pilot

**Files:**
- Create: `scripts/review-existing-media.py`
- Create: `docs/verification/2026-08-13-rana-plaza-media-review.md`
- Test: `tests/integration/test_rana_plaza_media_review_migration.py`
- Runtime only: `projects/collapse-topic-pilot-2026-08-12/artifacts/media_relevance_review.json`
- Runtime only: `projects/collapse-topic-pilot-2026-08-12/checkpoint_media_relevance_review.json`

**Interfaces:**
- Consumes: current 75-item manifest and source bytes.
- Produces: reviewed/quarantined pool, optional reusable archive supplement, coverage report, and refreshed dashboard state; no Human Gate action.

- [ ] **Step 1: Record immutable baseline**

Compute and store the base manifest SHA-256 and all 75 source-file SHA-256 values in the integration fixture. Assert the migration script cannot modify those paths.

- [ ] **Step 2: Write and run migration RED**

```python
def test_known_wrong_event_assets_are_not_recommended(migrated_review):
    excluded = {d["media_id"] for d in migrated_review["decisions"] if d["eligibility"] != "eligible"}
    assert "MEDIA_PEXELS_12734648" in excluded
    assert "MEDIA_PEXELS_15554614" in excluded
    assert "MEDIA_PEXELS_14673884" in excluded
```

Run: `.venv/bin/python -m pytest tests/integration/test_rana_plaza_media_review_migration.py -v`  
Expected: FAIL because the migration script and review artifact do not exist.

- [ ] **Step 3: Implement migration CLI and run dry review**

The default mode writes only a temporary report. `--apply` atomically writes the canonical review/progress/checkpoint and may download only rights-cleared archive supplement bytes. It never deletes or rewrites the original 75 files.

- [ ] **Step 4: Run current-project migration**

Run: `.venv/bin/python scripts/review-existing-media.py --project projects/collapse-topic-pilot-2026-08-12 --apply`  
Expected: a schema-valid review, known wrong-event items excluded, no original hash changes, and no Human Gate approval.

- [ ] **Step 5: Verify dashboard and media playback**

Confirm the deployed Tailscale dashboard defaults to recommended items, category counts match the artifact, excluded items remain viewable, one recommended image preview loads, one recommended video loads when present, and browser logs contain no errors.

- [ ] **Step 6: Run complete verification**

Run: `make test`  
Expected: all tests pass with zero failures.

Run: `node --check backlot/ui/mobile.js && git diff --check`  
Expected: exit 0.

- [ ] **Step 7: Write verification report and commit**

Record baseline/final hashes, category counts, archive source outcomes, coverage gaps, tests, dashboard checks, and confirmation that no paid call or Human Gate approval occurred.

```bash
git add scripts/review-existing-media.py tests/integration/test_rana_plaza_media_review_migration.py docs/verification/2026-08-13-rana-plaza-media-review.md
git commit -m "test: verify automatic media relevance review"
```

### Task 7: Deploy and update the existing PR

**Files:**
- Modify only if required by deployment: `scripts/install-mobile-dashboard-services.py`

**Interfaces:**
- Consumes: verified runtime branch.
- Produces: restarted local dashboard service and updated existing Draft PR #3.

- [ ] **Step 1: Fast-forward the verified implementation into `agent/youtube-factory-runtime`**

Confirm both worktrees are clean, the runtime branch is an ancestor of the implementation branch, and merge with `--ff-only`.

- [ ] **Step 2: Restart and check local service**

Run the existing launchd restart path and verify `http://127.0.0.1:8787/api/health` returns `{"ok":true,"app":"backlot"}`.

- [ ] **Step 3: Push without force**

Run: `git push origin agent/youtube-factory-runtime`  
Expected: remote branch advances without rewriting history.

- [ ] **Step 4: Confirm PR**

Verify Draft PR #3 still targets `main`, its head is `agent/youtube-factory-runtime`, and it includes the final verification commit.
