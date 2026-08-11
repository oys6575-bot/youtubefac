# YouTube Factory Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an isolated, runnable `유튜브공장` OpenMontage repository with MK Visual Director contracts and a non-API TopView manual handoff loop.

**Architecture:** Start from the exact clean OpenMontage upstream SHA, then add factory-specific contracts as small tested layers. OpenMontage remains the control plane; TopView is represented by deterministic local job-pack and ingest tools around a human-operated web UI.

**Tech Stack:** Python 3.11, pytest, JSON Schema 2020-12, PyYAML, FFmpeg/ffprobe, OpenMontage, Remotion 4.0.484 baseline, HyperFrames 0.7.106.

## Global Constraints

- Target repository is `/Users/mk-macbook/Documents/Codex/2026-08-11/referenced-chatgpt-conversation-this-is-an/유튜브공장`.
- OpenMontage source baseline is exactly `4eab34c5cfcccaa4f1970554928feccce73ee930`.
- Never copy `/Users/mk-macbook/Desktop/openmontage/.git`, `.env`, `.venv`, `node_modules`, caches, old `projects`, renders, or downloaded media.
- TopView is manual UI handoff only: no API credentials, submission, polling, browser-click automation, or automated credit billing.
- OpenMontage checkpoints are the single source of Human Gate approval truth.
- No paid provider call, publish action, Human Gate approval, or modification of the existing OpenMontage repository is allowed.
- New Python behavior follows test-first red-green-refactor.
- Configuration and imported source are verified by contract and contamination tests.

---

### Task 1: Clean Independent Foundation

**Files:**
- Create: `vendor/openmontage/source-lock.json`
- Create: `vendor/skills/manifest.json`
- Modify: `.gitignore`
- Test: `tests/contracts/test_youtube_factory_isolation.py`

**Interfaces:**
- Consumes: upstream Git object `4eab34c5cfcccaa4f1970554928feccce73ee930`.
- Produces: an independent Git repository with a machine-readable source lock and no inherited runtime data.

- [ ] **Step 1: Import the exact upstream tree**

Use `git archive` against the verified local Git object, extract it to a temporary directory, copy only archive members into the target, and initialize a fresh `main` branch. Record the upstream URL, SHA, import timestamp, license, and archive file count in `vendor/openmontage/source-lock.json`.

- [ ] **Step 2: Write the isolation contract test**

```python
def test_factory_tree_excludes_runtime_and_secret_material(factory_root):
    forbidden = [
        ".env", ".venv", "node_modules", ".cache", ".remotion",
        ".pytest_cache", "tmp", "pexels_6684209.jpg",
    ]
    assert not [name for name in forbidden if (factory_root / name).exists()]
    assert not (factory_root / "projects" / "aurora").exists()
```

- [ ] **Step 3: Run the isolation test and verify the baseline fails for missing factory lock**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_isolation.py -v`  
Expected: FAIL because the new source lock assertions are not implemented yet.

- [ ] **Step 4: Add source-lock and ignore rules**

The test must validate the exact SHA, official URL, `AGPL-3.0`, and forbidden path set. Add `.runtime/`, `.cache/`, `.remotion/`, `.superpowers/`, `tmp/`, local `.env`, generated `projects/*`, and TopView inbox media to `.gitignore` while retaining `.gitkeep` files.

- [ ] **Step 5: Re-run the isolation contract**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_isolation.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit foundation**

```bash
git add . ':!.env'
git commit -m "chore: import clean OpenMontage foundation"
```

### Task 2: Runtime Isolation and Bootstrap

**Files:**
- Create: `config/youtube-factory.env.example`
- Create: `scripts/bootstrap-youtube-factory.sh`
- Create: `scripts/activate-youtube-factory.sh`
- Modify: `.env.example`
- Test: `tests/contracts/test_youtube_factory_runtime_paths.py`

**Interfaces:**
- Consumes: repository root returned by `lib.paths.get_repo_root()`.
- Produces: repository-local paths for projects, clip cache, media cache, music, and manual handoff.

- [ ] **Step 1: Write failing runtime-path tests**

```python
def test_factory_environment_keeps_runtime_inside_repo(factory_root):
    env = parse_env_example(factory_root / "config/youtube-factory.env.example")
    assert env["OPENMONTAGE_PROJECTS_DIR"] == "${FACTORY_ROOT}/projects"
    assert env["OPENMONTAGE_CACHE_DIR"] == "${FACTORY_ROOT}/.runtime/clips_cache"
    assert env["MEDIA_CACHE_DIR"] == "${FACTORY_ROOT}/.runtime/media_cache"
    assert env["MUSIC_LIBRARY_DIR"] == "${FACTORY_ROOT}/music_library"
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_runtime_paths.py -v`  
Expected: FAIL because the factory environment template does not exist.

- [ ] **Step 3: Add local-only environment and bootstrap scripts**

The bootstrap script must require Python 3.11, create `.venv`, install Python dependencies, use `npm ci` in `remotion-composer`, create ignored runtime folders, and never read or copy the existing OpenMontage `.env`.

- [ ] **Step 4: Run and verify GREEN**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_runtime_paths.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit runtime isolation**

```bash
git add config scripts .env.example tests/contracts/test_youtube_factory_runtime_paths.py
git commit -m "chore: isolate factory runtime paths"
```

### Task 3: VisualPlan and Evidence Contracts

**Files:**
- Create: `schemas/artifacts/evidence_registry.schema.json`
- Create: `schemas/artifacts/visual_plan.schema.json`
- Create: `schemas/artifacts/animatic_review.schema.json`
- Create: `schemas/artifacts/budget_approval.schema.json`
- Create: `schemas/artifacts/asset_selection.schema.json`
- Create: `lib/visual_plan_validator.py`
- Create: `lib/visual_plan_bridge.py`
- Create: `tests/fixtures/youtube_factory/visual_plan.valid.json`
- Create: `tests/fixtures/youtube_factory/visual_plan.invalid_literal_bypass.json`
- Create: `tests/fixtures/youtube_factory/visual_plan.invalid_ai_disclosure.json`
- Test: `tests/contracts/test_youtube_factory_visual_plan.py`

**Interfaces:**
- Consumes: `validate_visual_plan(plan: dict, evidence_registry: dict) -> list[str]`.
- Produces: `compile_scene_plan(plan: dict) -> dict` compatible with `schemas/artifacts/scene_plan.schema.json`.

- [ ] **Step 1: Write schema and semantic-validator behavior tests**

```python
def test_exact_overlay_must_resolve_to_claim(valid_plan, registry):
    broken = deepcopy(valid_plan)
    broken["sequences"][0]["shots"][0]["overlay"]["items"][0].pop("claim_id")
    assert "exact overlay requires claim_id" in validate_visual_plan(broken, registry)

def test_ai_reconstruction_requires_disclosure(valid_plan, registry):
    broken = deepcopy(valid_plan)
    broken["sequences"][0]["shots"][1]["contains_ai"] = False
    assert "AI representation requires contains_ai=true" in validate_visual_plan(broken, registry)
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_visual_plan.py -v`  
Expected: FAIL because validator and schemas do not exist.

- [ ] **Step 3: Implement minimal schemas and semantic validator**

The route enum must be exactly `REAL_INGEST`, `TOPVIEW_HANDOFF`, `LOCAL_LTX`, `HYPERFRAMES`. Exact literals must equal their referenced claim value. `AI_RECONSTRUCTION` and AI-bearing `HYBRID` shots must set `contains_ai=true`, `disclosure.required=true`, and a controlled Korean label.

- [ ] **Step 4: Add scene-plan bridge test**

```python
def test_bridge_preserves_shot_order_and_routes(valid_plan):
    scene_plan = compile_scene_plan(valid_plan)
    assert [s["id"] for s in scene_plan["scenes"]] == ["SHOT_001", "SHOT_002"]
    assert scene_plan["scenes"][1]["production_route"] == "TOPVIEW_HANDOFF"
```

- [ ] **Step 5: Implement the minimal bridge and validate against OpenMontage schema**

Map every shot to one scene, preserve timing and overlay text, and store the provider route in the scene treatment without recording approval state in VisualPlan.

- [ ] **Step 6: Run and verify GREEN**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_visual_plan.py -v`  
Expected: PASS for valid fixture and intended failures for both invalid fixtures.

- [ ] **Step 7: Commit contracts**

```bash
git add schemas/artifacts lib/visual_plan_validator.py lib/visual_plan_bridge.py tests/contracts/test_youtube_factory_visual_plan.py tests/fixtures/youtube_factory
git commit -m "feat: add evidence-bound VisualPlan contracts"
```

### Task 4: TopView Manual Job Pack

**Files:**
- Create: `schemas/artifacts/topview_job_pack.schema.json`
- Create: `tools/video/topview_manual_handoff.py`
- Create: `.agents/skills/topview-manual-handoff/SKILL.md`
- Test: `tests/tools/test_topview_manual_handoff.py`

**Interfaces:**
- Consumes: `TopViewManualHandoff.execute({project_dir, visual_plan_path, batch_id})`.
- Produces: `handoff/topview/outbox/<batch_id>/job.json`, `INSTRUCTIONS.md`, and frozen references.

- [ ] **Step 1: Write the failing job-pack test**

```python
def test_job_pack_contains_only_topview_handoff_shots(tmp_path, visual_plan_path):
    result = TopViewManualHandoff().execute({
        "project_dir": str(tmp_path),
        "visual_plan_path": str(visual_plan_path),
        "batch_id": "BATCH_001",
    })
    job = json.loads(Path(result.output_path).read_text())
    assert [item["shot_id"] for item in job["jobs"]] == ["SHOT_002"]
    assert job["integration_mode"] == "manual_ui"
    assert "api" not in json.dumps(job).lower()
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.11 -m pytest tests/tools/test_topview_manual_handoff.py -v`  
Expected: FAIL because the tool is missing.

- [ ] **Step 3: Implement deterministic job-pack creation**

Copy references by content hash, reject paths outside the project, create stable expected filenames, produce Korean instructions, and report zero automated API cost. Never open or control a browser.

- [ ] **Step 4: Add idempotency and traversal tests**

```python
def test_same_batch_and_plan_are_idempotent(tmp_path, visual_plan_path):
    assert first_job_sha256 == second_job_sha256

def test_reference_outside_project_is_rejected(tmp_path, visual_plan_with_external_reference):
    assert result.success is False
    assert "outside project" in result.error
```

- [ ] **Step 5: Run and verify GREEN**

Run: `python3.11 -m pytest tests/tools/test_topview_manual_handoff.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit job-pack tool**

```bash
git add schemas/artifacts/topview_job_pack.schema.json tools/video/topview_manual_handoff.py .agents/skills/topview-manual-handoff tests/tools/test_topview_manual_handoff.py
git commit -m "feat: add TopView manual job packs"
```

### Task 5: TopView Result Ingest and Asset Selection Barrier

**Files:**
- Create: `tools/video/topview_manual_ingest.py`
- Modify: `schemas/artifacts/asset_manifest.schema.json`
- Test: `tests/tools/test_topview_manual_ingest.py`

**Interfaces:**
- Consumes: `TopViewManualIngest.execute({project_dir, batch_id, metadata_path})`.
- Produces: immutable candidate files plus manifest records with checksum, ffprobe metadata, provenance, and `selection_status="candidate"`.

- [ ] **Step 1: Write failing ingest behavior tests**

```python
def test_valid_video_is_registered_as_candidate(project_with_video):
    result = TopViewManualIngest().execute(project_with_video.inputs)
    record = load_manifest(result.output_path)["assets"][0]
    assert record["selection_status"] == "candidate"
    assert record["provenance"]["provider"] == "topview_manual"
    assert len(record["sha256"]) == 64

def test_unexpected_filename_is_rejected_without_moving_file(project_with_wrong_filename):
    assert result.success is False
    assert inbox_file.exists()
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.11 -m pytest tests/tools/test_topview_manual_ingest.py -v`  
Expected: FAIL because the ingest tool is missing.

- [ ] **Step 3: Implement minimal validated ingest**

Require user-supplied actual model and optional credits, run ffprobe, compare duration/aspect tolerance, hash the file, copy to a content-addressed candidate directory, and append idempotently to the manifest. Do not mark the asset selected or approved.

- [ ] **Step 4: Add corrupt-file, mismatch, and duplicate tests**

Use a locally generated one-second FFmpeg fixture. A corrupt file, wrong shot filename, or material duration mismatch must create a rejection report and leave the inbox input untouched. Re-ingesting the same checksum must not duplicate records.

- [ ] **Step 5: Run and verify GREEN**

Run: `python3.11 -m pytest tests/tools/test_topview_manual_ingest.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit ingest tool**

```bash
git add tools/video/topview_manual_ingest.py schemas/artifacts/asset_manifest.schema.json tests/tools/test_topview_manual_ingest.py
git commit -m "feat: validate TopView manual results"
```

### Task 6: YouTube Factory Pipeline and Directors

**Files:**
- Create: `pipeline_defs/youtube-factory.yaml`
- Create: `skills/pipelines/youtube-factory/executive-producer.md`
- Create: `skills/pipelines/youtube-factory/evidence-director.md`
- Create: `skills/pipelines/youtube-factory/proposal-director.md`
- Create: `skills/pipelines/youtube-factory/script-director.md`
- Create: `skills/pipelines/youtube-factory/mk-visual-director.md`
- Create: `skills/pipelines/youtube-factory/animatic-director.md`
- Create: `skills/pipelines/youtube-factory/budget-director.md`
- Create: `skills/pipelines/youtube-factory/asset-director.md`
- Create: `skills/pipelines/youtube-factory/edit-director.md`
- Create: `skills/pipelines/youtube-factory/compose-director.md`
- Create: `skills/pipelines/youtube-factory/publish-director.md`
- Create: `config/visual-grammars/HERITAGE_FORGE.yaml`
- Test: `tests/contracts/test_youtube_factory_pipeline.py`

**Interfaces:**
- Consumes: existing `lib.pipeline_loader.load_pipeline("youtube-factory")`.
- Produces: ordered stages and Human Gates that expose the manual TopView wait state without bypassing asset selection.

- [ ] **Step 1: Write failing pipeline contract tests**

```python
def test_pipeline_orders_manual_generation_between_budget_and_asset_selection():
    manifest = load_pipeline("youtube-factory")
    names = [stage["name"] for stage in manifest["stages"]]
    assert names.index("budget") < names.index("assets") < names.index("asset_selection")
    assert manifest["stages"][names.index("asset_selection")]["human_approval_default"] is True
```

- [ ] **Step 2: Run and verify RED**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_pipeline.py -v`  
Expected: FAIL because the manifest does not exist.

- [ ] **Step 3: Add manifest, directors, grammar, and explicit gates**

The assets stage may create TopView job packs and enter `awaiting_manual_external`; the edit stage must require `asset_selection`. Final review, title/thumbnail packaging, and publish remain user-gated.

- [ ] **Step 4: Run manifest schema and contract tests**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_pipeline.py tests/contracts/test_phase0_contracts.py -v`  
Expected: PASS.

- [ ] **Step 5: Commit pipeline**

```bash
git add pipeline_defs/youtube-factory.yaml skills/pipelines/youtube-factory config/visual-grammars/HERITAGE_FORGE.yaml tests/contracts/test_youtube_factory_pipeline.py
git commit -m "feat: add YouTube Factory production pipeline"
```

### Task 7: Skill and Runtime Refresh

**Files:**
- Create: `vendor/skills/manifest.json`
- Modify: `.agents/skills/hyperframes*/**`
- Create: `.agents/skills/beat-sync-editing/**`
- Create: `.agents/skills/color-motion/**`
- Create: `.agents/skills/diagram-animation/**`
- Create: `.agents/skills/isometric-animation/**`
- Create: `.agents/skills/kinetic-typography/**`
- Create: `.agents/skills/map-animation/**`
- Create: `.agents/skills/motion-art-direction/**`
- Create: `.agents/skills/remotion-bits/**`
- Create: `.agents/skills/shot-composition/**`
- Test: `tests/contracts/test_youtube_factory_skill_manifest.py`

**Interfaces:**
- Consumes: verified local skill directories and HyperFrames `0.7.106` installation metadata.
- Produces: traceable skills whose entrypoints are referenced by MK Visual Director and Compose Director.

- [ ] **Step 1: Write failing provenance tests**

Each copied skill must have a manifest record containing local source path, file-tree SHA-256, license status, imported timestamp, and the director that consumes it. HyperFrames entries must identify `0.7.106`.

- [ ] **Step 2: Run and verify RED**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_skill_manifest.py -v`  
Expected: FAIL because the provenance manifest is incomplete.

- [ ] **Step 3: Copy and refresh skills without copying caches**

Use directory-level allowlists. Keep all official tracked OpenMontage skills, add the nine reviewed local skills, install missing `hyperframes-keyframes`, `faceless-explainer`, `embedded-captions`, and `general-video`, and connect relevant names in director documentation.

- [ ] **Step 4: Run skill integrity tests and HyperFrames doctor**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_skill_manifest.py -v`  
Run: `npx --yes hyperframes@0.7.106 doctor`  
Expected: contract PASS; doctor exits 0 or reports only missing optional cloud credentials.

- [ ] **Step 5: Commit skill refresh**

```bash
git add .agents/skills vendor/skills/manifest.json skills/pipelines/youtube-factory
git commit -m "chore: refresh factory motion skills"
```

### Task 8: Operator Guide and Verified Local Dry Run

**Files:**
- Create: `README_KO.md`
- Create: `docs/operations/TOPVIEW_MANUAL_WORKFLOW.md`
- Create: `docs/operations/START_HERE.md`
- Create: `examples/youtube-factory/demo-project/**`
- Test: `tests/integration/test_youtube_factory_dry_run.py`

**Interfaces:**
- Consumes: factory manifest, VisualPlan validator/bridge, TopView tools, FFmpeg, and local runtime paths.
- Produces: a no-paid-call demonstration from plan validation through manual job pack and candidate ingest.

- [ ] **Step 1: Write the failing dry-run integration test**

The test must create a temporary project, validate the demo VisualPlan, compile scene_plan, create a TopView job pack, synthesize a one-second local video with FFmpeg, ingest it, and assert the final record is still `candidate`.

- [ ] **Step 2: Run and verify RED**

Run: `python3.11 -m pytest tests/integration/test_youtube_factory_dry_run.py -v`  
Expected: FAIL at the first missing integration behavior.

- [ ] **Step 3: Add operator documentation and demo fixtures**

Document one command at a time in Korean: bootstrap, activate, create project, produce TopView outbox, perform manual generation, place the download in inbox, ingest, review candidates, approve through OpenMontage, and render a local review build.

- [ ] **Step 4: Run focused and full verification**

Run: `python3.11 -m pytest tests/contracts/test_youtube_factory_*.py tests/tools/test_topview_manual_*.py tests/integration/test_youtube_factory_dry_run.py -v`  
Run: `python3.11 -m pytest tests/contracts tests/lib tests/tools -q`  
Run: `python3.11 tools/tool_registry.py --list`  
Expected: all factory tests pass, upstream contract/lib/tool tests have zero failures, and both TopView manual tools are discoverable.

- [ ] **Step 5: Inspect the generated media and repository boundaries**

Run ffprobe on the smoke fixture, inspect at least one extracted frame, scan tracked paths for secret/runtime patterns, and verify `git status --short` contains only intentional files.

- [ ] **Step 6: Commit documentation and dry run**

```bash
git add README_KO.md docs/operations examples/youtube-factory tests/integration/test_youtube_factory_dry_run.py
git commit -m "docs: add verified YouTube Factory workflow"
```
