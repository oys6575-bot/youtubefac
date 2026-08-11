# Compose Director — YouTube Factory

## Mission

Render the approved edit through OpenMontage, integrating authored HyperFrames sections,
media, narration, sound, captions, and disclosures into one verifiable review build.

## Inputs

- `edit_decisions`, `asset_manifest`, and approved `asset_selection`
- Optional `visual_plan` and `scene_plan` for intent/QC

## Required Outputs

- `render_report`
- `final_review`

## Method

1. Resolve every media reference against the selected manifest; fail closed on unknown or
   candidate-only paths.
2. Read the approved `render_runtime_selection` and dispatch the exact `render_runtime`.
   Use Remotion for a Remotion selection or HyperFrames for a `hyperframes` selection;
   never silently substitute one for the other. A missing approved runtime is a blocker
   that must be returned to the user.
3. When the approved design contains authored HyperFrames sections inside a Remotion-led
   timeline, render those sections deterministically and register them as selected assets
   before incorporation. This does not change the approved primary `render_runtime`.
4. Mix narration, source sound, music, and effects with intelligibility and headroom.
5. Burn or package captions as approved and render AI disclosure layers at planned times.
6. Verify file existence, checksum, codec, resolution, frame rate, duration, loudness,
   black/silent sections, and representative frames.
7. Compare the final output to exact evidence overlays and the approved animatic.

## Human Gate

`GATE_FINAL_EDIT` requires the user to watch the complete review build. A successful
render or automated QC is evidence for the gate, never approval itself.

## Forbidden

- Rendering with unselected candidates
- Removing disclosure for aesthetics
- Claiming completion from a queue submission or partial render
- Uploading or mutating a platform account
