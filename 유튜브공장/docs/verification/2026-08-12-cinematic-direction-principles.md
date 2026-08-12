# Cinematic Direction Principles — Verification Record

Date: 2026-08-12  
Branch: `agent/youtube-factory-runtime`  
Scope: provider-neutral direction principles, VisualPlan contract, TopView manual handoff, Obsidian research synthesis, and MK Visual Director procedure.

## Verdict

**PASS.** All 53 directly related contract and tool tests pass, the complete repository suite passes, both deterministic audits are clean, all three research inputs match their recorded SHA-256 values, and the TopView route remains manual-only.

The first repository-wide run exposed a pre-existing incomplete ComfyUI vendor import: the lock correctly recorded 1006 files but only 958 had been committed. Comparison with the exact locked upstream commit proved that all 48 omissions matched Git ignore rules. The missing files were restored from that commit without overwriting the existing 958 files, then byte-for-byte directory comparison and the full suite were rerun.

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

Final result: `53 passed in 5.63s`.

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

Final result: `1045 passed, 10 skipped, 1 subtests passed in 144.31s`.

The initial run failed one pre-existing contract with `958 == 1006`. Root-cause evidence and repair:

- official `v0.31.0` checkout resolved to locked commit `43cb4fffc89bba20ab7bd61467a36d0339338dab`;
- upstream `git ls-files` count was 1006;
- the 48 missing paths were ignored by project `internal/` or vendored `/input/`, `/output/`, `/models/`, `/custom_nodes/`, and `extra_model_paths.yaml` patterns;
- only missing paths were copied; existing vendor files were not overwritten;
- `diff -qr --exclude=.git` between the repaired vendor tree and official checkout returned no differences;
- repaired local file count is 1006;
- the previously failing targeted contract passed, followed by the green full-suite result above.

The lock value was not weakened to match an incomplete copy.

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
