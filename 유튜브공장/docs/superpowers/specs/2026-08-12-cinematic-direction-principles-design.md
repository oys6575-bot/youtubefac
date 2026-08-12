# Provider-Neutral Cinematic Direction Principles

**Date:** 2026-08-12  
**Status:** Revised after user review, pending renewed approval  
**Scope:** Isolated YouTube Factory only

## Goal

Improve MK Visual Director's shot direction with the useful filmmaking principles found
in the reviewed CINEDANCE, ACTING, and LIRA materials without copying those files,
installing them as global skills, or importing provider-specific vocabulary.

The result must improve what a shot says about its opening frame, spatial arrangement,
visible performance, optical result, physical causality, timed action, and reference
roles. It must continue to work with the existing OpenMontage control plane and the
human-operated TopView handoff.

The Obsidian vault must also retain comprehensive coverage of all useful topics,
exceptions, failure patterns, and operating cautions found during the three-file review.
This full knowledge layer is paraphrased and searchable; it is not loaded wholesale into
every production prompt.

## Non-Goals

- Do not copy, vendor, quote, or redistribute the three source Markdown files.
- Do not add a Higgsfield or Seedance production route.
- Do not install a global Claude, Codex, or provider skill.
- Do not automate TopView, submit paid jobs, or weaken any Human Gate.
- Do not replace sequence meaning, evidence policy, or the existing visual grammar.
- Do not confuse comprehensive Obsidian retention with automatic technique activation.

## Chosen Approach

Use a project-authored, provider-neutral direction contract rather than a raw skill
import. This keeps the principles usable across TopView manual work, local generation,
real-footage selection, and composition while preventing one provider's prompt syntax
from taking control of the factory.

Two alternatives were rejected:

1. Installing the three files unchanged would create broad trigger conflicts, retain
   unverified licensing, and let provider prompt rules bypass OpenMontage planning.
2. Storing only prose in Obsidian would make the ideas searchable but would not ensure
   that a selected shot or TopView job packet carries the direction forward.

The chosen design therefore has two layers: comprehensive paraphrased knowledge in
Obsidian and a small operational contract containing only the principles selected for a
real sequence or shot.

## Principle Set

Add six original, compact principles:

1. **Opening-frame intent:** state what is already visible and happening in the first
   usable frame; do not begin with an empty or unrelated view unless that is deliberate.
2. **Explicit spatial blocking:** state screen position, world anchor, distance,
   orientation, gaze or action target, and movement path for every critical subject.
3. **Behavioral performance beats:** direct objectives and observable tactics through
   gaze, breath, posture, timing, physical business, reaction, and beat changes instead
   of naming an emotion alone.
4. **Observable optical result:** describe camera distance, perspective expansion or
   compression, background behavior, focus behavior, and subject scale; technical lens
   metadata may support but never replace the visible result.
5. **Physical causality:** specify mass, contact, resistance, weight transfer, inertia,
   follow-through, and material response only where they affect the shot.
6. **Reference-role binding:** give every supplied reference one explicit job and state
   which properties it controls and must not control; preserve distinct condition or
   time-state variants rather than treating them as interchangeable.

## Architecture and Data Flow

```text
Approved script and evidence
        |
        v
MK Visual Director
  - sequence meaning first
  - select 3-7 relevant techniques
  - write compact cinematic direction controls
        |
        v
visual_plan
  - existing route, evidence, camera, lighting, transition fields
  - new provider-neutral cinematic_direction block
        |
        +--> REAL_INGEST / HYPERFRAMES / LOCAL_LTX
        |
        `--> TOPVIEW_HANDOFF
               - carry the same direction block into the manual job pack
               - preserve explicit reference roles
               - human operates the TopView UI
        |
        v
OpenMontage candidate ingest, selection, edit, compose, and QC
```

## Comprehensive Obsidian Retention

Create a project-authored Obsidian collection under
`knowledge/10-RESEARCH/cinematic-direction/`:

1. `Camera-Spatial-Physics-Direction.md` covers the full reviewed camera-direction
   surface: current-shot isolation, opening-frame control, location mapping, blocking,
   gaze and body direction, landmark anchoring, single-take versus controlled cuts,
   continuity across cuts, optical-result language, camera operation, timing, physics,
   lighting, audio, prompt-density control, and final QA.
2. `Behavioral-Performance-Direction.md` covers objectives, obstacles, stakes, tactics,
   beats, subtext, listening, reaction timing, gaze, breath, posture, physical business,
   distance, status, speech rhythm, voice continuity, ensemble response, state inertia,
   failure patterns, and performance review.
3. `Image-Reference-Asset-Direction.md` covers image-task diagnosis, character/location/
   prop preparation, edit-versus-regenerate decisions, prompt density, positive
   description, palette and material control, reference identity, text and tattoo
   handling, surgical edits, preserved properties, location-view changes, state
   variants, and model-claim verification boundaries.
4. `Cinematic-Direction-Map.md` links the three full notes to the six active generic
   techniques and shows when to load each note.

All four notes use original project wording. Their metadata records:

- `type: research-synthesis`;
- `activation_status: REFERENCE_ONLY` for the full notes;
- `copyright_mode: paraphrase_only`;
- source URLs, retrieval date, and local audit hashes as provenance only;
- provider-specific statements as historical or unverified claims that require a live
  check before use;
- stable `coverage_ids` proving that every reviewed topic is represented.

The full notes are never placed in a normal 3–7 technique knowledge pack. Agents load a
full note only for research, a difficult shot, or maintenance of the derived active
techniques. This keeps the entire knowledge accessible without flooding ordinary shot
planning or allowing reference-only material to become executable policy.

## Contract Changes

Add one compact `cinematic_direction` object to a shot. It contains:

- `opening_frame`: the first usable visual state;
- `spatial_blocking[]`: critical subject placement and directed movement;
- `optical_result`: the visible perspective, scale, background, and focus behavior;
- `timed_beats[]`: ordered action/camera beats within the shot duration;
- `physical_cues[]`: only the causal movement or material rules needed for the shot;
- optional `performance`: objective, obstacle, current tactic, observable behavior,
  reaction cue, and beat change for character-driven shots;
- optional `reference_bindings[]`: path, role, controlled properties, and excluded
  properties for each supplied reference.

Require this block for generated motion routes (`TOPVIEW_HANDOFF` and `LOCAL_LTX`).
Allow it on other routes when it improves footage selection or composition. When a
generation brief contains references, require a one-to-one binding so the handoff tool
does not guess every reference is an environment image.

Carry the block unchanged into the TopView manual job packet and render its essential
instructions in `INSTRUCTIONS.md`. This transfer adds no network operation and changes
no approval state.

## Knowledge and Skill Integration

- Add the six principles as `ACTIVE`, `GENERIC` entries in the visual-technique
  registry so they are selected only when the shot intent matches.
- Update MK Visual Director to read and populate the contract, while preserving the
  existing limit of three to seven techniques per sequence and one to four per shot.
- Generate normal Obsidian technique cards from the registry. The vault remains a
  retrieval layer and cannot activate a provider or approve a gate.
- Preserve the four comprehensive cinematic-direction notes as hand-authored Obsidian
  knowledge. Vault synchronization must not overwrite them, and vault audit must verify
  their metadata, links, and coverage IDs.
- Keep Higgsfield- and Seedance-specific records isolated as `ON_DEMAND`; none of their
  syntax may appear in a TopView knowledge pack or job packet.

## Validation

Use tests to prove:

1. the six generic techniques are selectable by matching intents and remain
   provider-neutral;
2. a generated-motion shot without `cinematic_direction` is rejected;
3. performance is optional for a material-only shot but structurally validated when
   present;
4. timed beats are ordered, non-overlapping, and fit the shot duration;
5. every generation reference has exactly one explicit binding;
6. the TopView job packet preserves cinematic direction and reference roles without
   API, MCP, browser automation, or budget changes;
7. the Obsidian vault syncs and audits cleanly with the new technique count;
8. all declared source-topic coverage IDs occur exactly once in the three comprehensive
   notes, their Map links resolve, and none enters a normal production knowledge pack;
9. existing visual-plan, bridge, handoff, and factory contract suites remain green.

## Success Criteria

A future agent can plan a shot such as a craftsperson hammering metal and produce a
manual TopView packet that makes the opening state, hand/tool/material positions,
camera result, acceleration and landing, contact weight, material response, and any
human performance readable without using the reviewed files or provider-specific
terminology.

The same project must let a human open Obsidian and find the complete paraphrased camera,
performance, and image/reference knowledge—not merely the six currently active
principles—while keeping those long reference notes outside routine production context.
