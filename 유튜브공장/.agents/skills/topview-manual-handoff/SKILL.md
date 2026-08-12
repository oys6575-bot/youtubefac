---
name: topview-manual-handoff
description: Prepare, operate, and recover human-run TopView web UI generation jobs for the YouTube Factory. Use when an approved VisualPlan routes a shot to TOPVIEW_HANDOFF, when a person needs exact Board, Canvas, or 3D Shot Composer instructions, or when downloaded TopView candidates and their model, credit, queue, settings, and timing provenance must be validated and returned to OpenMontage without API, MCP, browser automation, billing automation, or automatic asset approval.
---

# TopView Manual Handoff

Keep TopView outside the automated control plane. Use OpenMontage to freeze the work order and validate returned files; require a person to operate the TopView web UI.

## Required boundary

- Never call TopView API, MCP, Codex plugin, or official generation skill.
- Never automate browser clicks, sign-in, credit spending, retries, or downloads.
- Never interpret a generated result as approved. Register it as a candidate only.
- Never render exact dates, figures, quotations, or source labels inside a generative model. Add verified text later with HyperFrames or Remotion.
- Stop at the Budget Gate before any charge and at Asset Selection Gate before editing.

## Prepare a job

1. Confirm `GATE_ANIMATIC` and `GATE_BUDGET` are approved in OpenMontage checkpoints. Do not infer approval from VisualPlan fields.
2. Read `config/topview-capabilities.yaml`. Treat it as a capability catalog, not proof that a particular option is currently visible.
3. Choose the smallest suitable workspace and task mode using [capability-routing.md](references/capability-routing.md).
4. Run the registered `topview_manual_handoff` tool with the project directory, approved VisualPlan path, and a new batch ID.
5. Open the produced `INSTRUCTIONS.md`; verify purpose, references, camera, continuity, duration, aspect, budget ceiling, and expected filenames.
6. Give the entire outbox folder to the human operator. Do not paraphrase away required settings or provenance fields.

## Operate TopView manually

1. Open TopView in the user's normal browser and enter the specified workspace.
2. Confirm the exact model display label and every visible duration, resolution, aspect, reference, audio, and queue option.
3. Capture the settings and estimated credit charge before submitting.
4. Stop when the estimate exceeds the approved ceiling. Do not substitute a model silently.
5. Generate only up to the allowed attempt count. Record each paid attempt.
6. Compare candidates in Board when available. Download candidates with the prescribed filename.
7. Fill `operator-result.json` with the exact UI labels, credits, queue, plan tier, timestamps, settings-capture checksum, and notes.

## Recover results

1. Put downloads and `operator-result.json` in `handoff/topview/inbox/<BATCH_ID>/`.
2. Run the registered `topview_manual_ingest` tool.
3. Treat a validation error as a rejected ingest, not a reason to alter or delete the original download.
4. Review the registered candidates visually and audibly.
5. Ask for Human Gate selection in OpenMontage. Only selected candidate IDs may enter the edit stage.

## Verify

- Match file duration and resolution to the frozen job.
- Match `shot_id`, filename, batch, exact UI model label, and settings capture.
- Preserve checksum and TopView provenance in `asset_manifest.json`.
- Confirm the final composite adds the required `AI 재현` disclosure outside the generated pixels.
- Record actual credits in the cost log even though the local adapter itself reports zero API cost.

For detailed workspace and mode choice, read [capability-routing.md](references/capability-routing.md).
