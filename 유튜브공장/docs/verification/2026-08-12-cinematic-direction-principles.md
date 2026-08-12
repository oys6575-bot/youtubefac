# Cinematic Direction Principles — Verification Record

Date: 2026-08-12  
Branch: `agent/youtube-factory-runtime`  
Scope: provider-neutral direction principles, VisualPlan contract, TopView manual handoff, Obsidian research synthesis, and MK Visual Director procedure.

## Verdict

**PASS for the scoped cinematic-direction integration.** All 53 directly related contract and tool tests pass, both deterministic audits are clean, all three research inputs match their recorded SHA-256 values, and the TopView route remains manual-only.

The repository-wide suite retains one unrelated baseline failure that existed before this implementation: the vendored ComfyUI tree contains 958 counted files while `vendor/comfyui/source-lock.json` records 1006. This task did not alter the ComfyUI vendor tree or its lock and does not claim that repository-wide issue is resolved.

## Executed evidence

### Focused contracts

Command:

```bash
.venv/bin/python -m pytest \
  tests/contracts/test_visual_technique_registry.py \
  tests/contracts/test_youtube_factory_visual_plan.py \
  tests/contracts/test_knowledge_vault.py \
  tests/tools/test_topview_manual_handoff.py \
  tests/tools/test_topview_manual_ingest.py -q
```

Result: `53 passed in 5.94s`.

Verified behavior includes:

- six generic cinematic techniques are selectable on `TOPVIEW_MANUAL` without other-provider leakage;
- generated-motion routes require typed `cinematic_direction` data;
- timed beats cannot overlap or exceed shot duration;
- generation reference paths and role bindings must match exactly;
- a material-only shot remains valid without a performance block;
- the TopView job pack preserves cinematic direction and role-specific reference controls;
- a missing reference role fails before an outbox is created;
- the returned TopView result remains only an asset candidate;
- four research syntheses are searchable but absent from normal pack `load_order`;
- research coverage drift is detected without rewriting the hand-authored note.

### Repository-wide regression

Command:

```bash
.venv/bin/python -m pytest -q
```

Result: `1044 passed, 10 skipped, 1 subtests passed, 1 failed in 144.80s`.

Only failure:

```text
tests/contracts/test_factory_toolchain_audit.py::
test_vendored_comfyui_source_is_exact_and_has_local_video_blueprints
assert 958 == 1006
```

The same test failed on the pre-change baseline with the same `958 == 1006` mismatch. No cinematic-direction file participates in that contract.

### Deterministic audits

Commands:

```bash
.venv/bin/python scripts/visual-techniques.py audit
.venv/bin/python scripts/knowledge-vault.py audit
```

Results:

```json
{"ok": true, "findings": []}
```

for both audits.

The synchronized vault reports 390 indexed entities:

- 49 techniques
- 107 skills
- 104 tools
- 16 creative sources
- 23 research URLs
- 6 local models
- 10 toolchain records
- 59 TopView capabilities
- 12 TopView model-family records
- 4 research syntheses

The three domain notes cover 66 unique research checks: 28 camera/spatial/physics, 20 behavioral-performance, and 18 image/reference/asset checks. The fourth note is the navigation and execution-boundary map.

### Research input integrity

Recalculated SHA-256 values:

```text
7b0e4f8dad1515631f54b6b6401b333adbdbbe3b8832a71c6ac78fe5d20b95f8  cinedance-skill.md
8841c5d1155ee9347d5fc302a2f0fdac76fed21070c94bf01741821ea1c42365  acting-skill.md
329240f47888689e16576682c5de52dd2c1075b1fe5482068c647dad9f03544a  lira-skill.md
```

They equal `config/cinematic-direction-coverage.yaml`. The external Markdown payloads were not copied into the repository. The Obsidian notes are project-authored Korean paraphrases with `REFERENCE_ONLY` and `paraphrase_only` metadata.

## Policy assertions

The following constraints remain unchanged and are exercised by the handoff tests:

- TopView integration mode is `manual_ui`.
- `api_allowed`, `mcp_allowed`, and `browser_automation_allowed` are false.
- a human captures the current UI label and cost before submission;
- budget and asset-selection Human Gates remain required;
- no implementation step calls a provider, initiates billing, approves a gate, or publishes media;
- exact facts and disclosure labels are added in the controlled composition layer rather than generated inside provider video.

## Completion boundary

This verification establishes that the directing principles are stored, selectable, typed, handed to a human TopView operator, searchable in Obsidian, and protected by automated contracts. It does not establish the visual quality of a paid or external generated clip. That requires a later approved pilot with real media inspection and remains outside this implementation.
