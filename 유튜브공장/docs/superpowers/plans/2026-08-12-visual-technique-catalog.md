# Visual Technique Catalog Implementation Plan

> **For agentic workers:** Execute task-by-task with red-green-refactor and verify
> every external source boundary before activation.

**Goal:** Make all reviewed filmmaking-method sources retrievable later while loading
only three to seven relevant, route-safe techniques during normal production.

**Architecture:** A strict YAML registry is the canonical knowledge index. A local
Python selector filters by status, phase, provider, runtime, and intent; it never
downloads or executes external content. OpenMontage stays above MK Visual Director,
and selected technique IDs become planning evidence rather than new approval state.

**Tech Stack:** Python 3.11, PyYAML, JSON Schema 2020-12, pytest, HyperFrames, GSAP,
FFmpeg/ffprobe.

### Task 1: Registry Contract and RED Tests

**Files:**
- Create: `tests/contracts/test_visual_technique_registry.py`
- Create: `schemas/visual-technique-registry.schema.json`

- [x] Test schema compilation and valid-registry loading.
- [x] Test that every active local path is present and inside the factory.
- [x] Test deterministic three-to-seven selection for a documentary shot.
- [x] Test provider isolation and inactive-source behavior.
- [x] Run the tests and confirm failure because the registry and loader do not exist.

### Task 2: Catalog, Source Locks, and Selector

**Files:**
- Create: `config/visual-technique-registry.yaml`
- Create: `vendor/creative-sources/manifest.json`
- Create: `lib/visual_technique_registry.py`
- Create: `scripts/visual-techniques.py`
- Modify: `.gitignore`

- [x] Add active local directing, camera, transition, timing, type, graphics, and sound
      entries.
- [x] Add pinned on-demand and reference-only GitHub/Hugging Face sources.
- [x] Implement deterministic audit, search, and selection.
- [x] Keep source staging cache ignored and require explicit future activation.
- [x] Run focused tests until green.

### Task 3: Director and Pipeline Wiring

**Files:**
- Modify: `skills/pipelines/youtube-factory/mk-visual-director.md`
- Modify: `pipeline_defs/youtube-factory.yaml`
- Modify: `tests/contracts/test_youtube_factory_pipeline.py`

- [x] Require registry audit and selection before shot decoration.
- [x] Record chosen IDs, rejected provider-specific candidates, and technique purpose.
- [x] Keep TopView manual-only and all existing Human Gates unchanged.
- [x] Verify the pipeline manifest still validates and stage order is unchanged.

### Task 4: Practical Micro-Reel

**Files:**
- Create: `videos/visual-technique-tests/index.html`
- Create: `videos/visual-technique-tests/index.motion.json`
- Create: `videos/visual-technique-tests/hyperframes.json`
- Create: `videos/visual-technique-tests/README.md`

- [x] Demonstrate a still-image depth push.
- [x] Demonstrate fast-to-slow virtual-camera motion.
- [x] Demonstrate a meaning-preserving photo-to-exact-typography handoff.
- [x] Run HyperFrames lint/check with snapshots, inspect frames, then render the
      user-requested test reel to `.runtime/visual-tests/`.
- [x] Verify the MP4 with ffprobe and representative-frame inspection.

### Task 5: Final Verification and GitHub Save

- [x] Run focused registry, pipeline, TopView-boundary, and HyperFrames tests.
- [x] Run relevant full contract tests (one pre-existing ComfyUI inventory mismatch
      recorded in the verification report).
- [x] Inspect `git diff --check` and the complete diff for accidental scope changes.
- [x] Commit intentionally and push `agent/youtube-factory-runtime`.
