# Obsidian Knowledge Vault Verification — 2026-08-12

## Verdict

PASS for the implemented scope. The isolated YouTube Factory now has a portable,
offline Obsidian vault that indexes all audited knowledge, detects drift, searches
every status, and resolves a bounded route-safe pack for MK Visual Director.

This verdict does not approve a Human Gate, start provider execution, or make the
Draft PR ready for merge.

## Materialized inventory

| Entity family | Canonical count | Materialized count |
|---|---:|---:|
| Visual techniques | 43 | 43 |
| Skills | 107 | 107 |
| Tools | 104 | 104 |
| Pinned creative sources | 16 | 16 |
| Research URLs | 23 | 23 |
| Local models | 6 | 6 |
| Toolchain locks | 10 | 10 |
| TopView capabilities | 59 | 59 |
| TopView model families | 12 | 12 |
| **Entity cards** | **380** | **380** |

The vault contains 411 tracked/generated files: 406 Markdown files plus the generated
catalog and portable Obsidian configuration. The extra 26 Markdown files are maps,
playbooks, provider/runtime guides, templates, and inbox/start pages.

## Real sync and audit

Commands:

```bash
.venv/bin/python scripts/knowledge-vault.py sync
.venv/bin/python scripts/knowledge-vault.py audit
.venv/bin/python scripts/knowledge-vault.py sync
```

Observed on both syncs:

```text
created=0 updated=0 unchanged=411 entity_cards=380 orphans=[]
```

Observed audit result:

```json
{"ok": true, "findings": []}
```

The isolated test also changes generated frontmatter, creates an orphan, and inserts a
broken wikilink. Audit reports all three without deleting the orphan. A second sync
preserves text inside every `USER-NOTES` section byte-for-byte.

## Search checks

`photo_to_motion` ranked these structured matches first:

1. `camera.material_macro_parallax` — ACTIVE
2. `camera.variable_velocity_push` — ACTIVE
3. `provider.topview.first_last_frame_bridge` — ON_DEMAND

The search deliberately exposes dormant knowledge while retaining its status. It does
not activate `ON_DEMAND`, `REFERENCE_ONLY`, or `BLOCKED` records.

`unlimited plans` returned the Reddit card `research-url.2062eee96756` with both status
and evidence class set to `ANECDOTAL_SIGNAL`. It is searchable discovery material, not
factual or executable production guidance.

## Bounded pack check

The fixed TopView-manual/HyperFrames selector fixture produced, in order:

1. `camera.variable_velocity_push`
2. `typography.exact_fact_overlay`
3. `transition.semantic_match_cut`
4. `camera.material_macro_parallax`
5. `camera.static_evidence_hold`

Resolved support counts were 7 skill cards, 6 tool/toolchain cards, and 0 external
source cards. The zero source-card count is expected because these five techniques use
project-local skills and the local Heritage Forge grammar. Their exact source paths are
still included in the pack.

Negative tests reject:

- fewer than 3 or more than 7 techniques;
- `ON_DEMAND` without explicit opt-in;
- `BLOCKED` and unknown technique IDs;
- provider-scope or render-runtime mismatch;
- a missing materialized card.

The TopView fixture contains no Higgsfield, Seedance, Local LTX, blocked, or Reddit
factual guidance. TopView remains manual UI only; the pack includes the manual handoff
and ingest bridge instructions, not an API or browser action.

## Regression result

Command:

```bash
.venv/bin/python -m pytest \
  tests/contracts/test_knowledge_vault.py \
  tests/contracts/test_visual_technique_registry.py \
  tests/contracts/test_youtube_factory_pipeline.py \
  tests/contracts/test_youtube_factory_visual_plan.py \
  tests/tools/test_topview_manual_handoff.py \
  tests/tools/test_topview_manual_ingest.py -q
```

Result: **47 passed in 4.42 seconds**.

This focused suite covers the vault, 3–7 technique selector, Visual Director pipeline,
VisualPlan validation, existing Human Gates, and TopView manual handoff/ingest. The
larger repository suite was not claimed as newly green; an earlier full-suite baseline
had one unrelated vendored ComfyUI tracked-file-count mismatch.

## Repository hygiene

- `git diff --check`: PASS
- Obsidian workspace files: none
- Obsidian community-plugin state: none
- Common API-token/private-key patterns under `knowledge/`: none
- Model weights, provider outputs, cookies, API keys, and personal Obsidian state: none
- Existing external production folders: not read into or modified by vault sync

## Authority and safety

- OpenMontage remains the control plane and source of truth.
- Canonical YAML/JSON registries remain policy authority; Markdown cards are derived.
- MK Visual Director must audit, select 3–7 techniques, resolve the pack, and read its
  `load_order` before planning a shot.
- Search visibility is not activation.
- The vault cannot select a provider, call a tool, spend credits, write checkpoint
  approval, or complete a Human Gate.
- TopView remains a human-operated UI after animatic and budget approval.

## Known limitation

No independent LLM-behavior pressure test was run in this session because delegated
subagent execution was not available for this implementation. The executable CLI,
pipeline manifest, fixed selector fixture, negative cases, and focused regressions were
verified instead. New external methods still require an explicit canonical registry or
manifest update followed by sync and audit; dropping a URL into Obsidian does not make
it production-safe.
