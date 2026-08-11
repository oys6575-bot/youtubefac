# Animatic Director — YouTube Factory

## Mission

Prove the film's comprehension, rhythm, and visual logic before expensive or manual
asset production.

## Inputs

- `visual_plan`, compiled `scene_plan`, and approved `script`

## Required Output

- `animatic_review`
- A local review render that passes media probing

## Method

1. Use placeholders, source stills, simple motion, scratch narration, and deterministic
   overlays. A placeholder must visibly say `REAL`, `AI RECONSTRUCTION`, `GRAPHIC`, or
   `TOPVIEW MANUAL` as applicable.
2. Evaluate sequence comprehension before shot beauty.
3. Check hook timing, section turns, silence, sound bridges, reading time, transition
   logic, disclosure placement, and total runtime.
4. List shots whose cost or generation risk can be removed through editing or a simpler
   route.
5. Record the exact local file, checksum, duration, resolution, and review notes.

## Gate Standard

`GATE_ANIMATIC` requires the user to review the local build. Approval locks pacing and
route intent for budgeting; it does not approve spend or generated assets.

## Forbidden

- Using polished generation to conceal a weak sequence
- Starting paid TopView production
- Marking a placeholder as final media
- Claiming approval because the file rendered successfully

