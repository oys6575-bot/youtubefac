# Visual Technique Catalog Design

**Date:** 2026-08-12  
**Status:** Approved for implementation by the user  
**Scope:** YouTube Factory only

## Goal

Keep the full filmmaking-method library available without flooding every scene with
conflicting instructions. OpenMontage remains the control plane. MK Visual Director
selects a small, traceable technique set for each sequence or shot, then the approved
production route executes it.

## Decision

Use a **catalog-all, activate-selectively** model:

- `ACTIVE`: safe local knowledge that may be selected automatically.
- `ON_DEMAND`: preserved and searchable, but activated only for an explicit shot need.
- `REFERENCE_ONLY`: research or architecture evidence; never an execution instruction.
- `BLOCKED`: licensing, provenance, provider drift, or safety prevents activation.

The selector returns three to seven techniques by default. Generic filmmaking methods
may accompany any route. Provider-specific methods may only accompany their exact
manual provider scope. `TOPVIEW_MANUAL` never permits Higgsfield- or Seedance-specific
instructions to leak into a TopView work order.

## Components

1. `config/visual-technique-registry.yaml`
   - Canonical technique records, tags, phase, provider scope, runtime scope, source,
     status, and activation conditions.
2. `schemas/visual-technique-registry.schema.json`
   - Structural contract for the registry.
3. `lib/visual_technique_registry.py`
   - Deterministic load, audit, search, and selection functions. It performs no network
     request, download, generation, or provider call.
4. `vendor/creative-sources/manifest.json`
   - Pinned GitHub commits and Hugging Face revisions for future activation. Large
     repositories and model weights are not copied into Git.
5. `scripts/visual-techniques.py`
   - Read-only list, search, select, and audit commands for humans and agents.
6. MK Visual Director and pipeline wiring
   - Planning must record selected technique IDs and rejected provider-specific
     candidates before VisualPlan is considered ready.
7. `examples/visual-technique-tests/`
   - A local HyperFrames micro-reel that demonstrates still-image motion, deliberate
     speed change, and a semantic photo-to-typography handoff.

## Selection Rules

- Meaning, evidence, and continuity outrank decorative novelty.
- Select at most one dominant camera treatment and one dominant transition family per
  shot unless a deliberate multi-phase move is documented.
- Exact names, dates, and quantities stay in HyperFrames or Remotion, never in a video
  generator.
- A selected technique must match the current planning phase and route scope.
- `ON_DEMAND` entries are searchable but excluded from normal selection.
- `REFERENCE_ONLY` and `BLOCKED` entries can never become selected merely because a
  query matches their tags.
- External activation requires its pinned revision, license state, and provider drift
  check to remain valid.

## Failure Handling

- Missing local source path: registry audit fails.
- Unknown intent: return a small generic direction set, never arbitrary provider advice.
- Provider mismatch: exclude the entry and report the exclusion reason.
- Too many matches: rank by exact intent overlap, phase fit, priority, then stable ID.
- No eligible matches: return a structured empty result; do not silently activate
  on-demand or blocked content.

## Verification

- JSON Schema compilation and registry validation.
- Every `ACTIVE` local source path exists inside the isolated factory.
- Documentary scenario selects three to seven relevant methods deterministically.
- TopView scope excludes Higgsfield and Seedance provider-specific entries.
- On-demand sources remain discoverable but inactive.
- Restricted or non-commercial research never becomes executable guidance.
- The HyperFrames reel passes lint/check, renders locally, passes `ffprobe`, and has
  representative frames visually inspected.

## Non-goals

- No TopView API, MCP, browser-click automation, automatic spending, or automatic
  candidate approval.
- No wholesale model or dataset download.
- No replacement of OpenMontage, VisualPlan, Human Gates, HyperFrames, or Remotion.
- No claim that an indexed external source is current forever; provider-specific
  material is rechecked when activated.
