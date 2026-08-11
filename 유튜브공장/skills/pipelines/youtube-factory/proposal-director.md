# Proposal Director — YouTube Factory

## Mission

Turn locked evidence into a production choice the user can approve before scriptwriting.

## Inputs

- `research_brief`
- `evidence_registry`
- Optional reference-video and source-media analyses

## Required Output

- `proposal_packet`
- `decision_log` entry for the selected concept and renderer family

## Proposal Packet

Present the audience, one-sentence promise, central question, runtime range, narrative
arc, planned real-versus-reconstruction balance, expected route mix, and major risks.
Show at least one lean alternative when the proposed route could require paid TopView
work.

Renderer choice must be explicit:

- OpenMontage remains the control plane in every option.
- Present both viable `render_runtime` options to the user before locking either one.
- Remotion/OpenMontage is preferred for the full editorial timeline and packaging; explain
  that advantage rather than silently choosing it.
- `hyperframes` is preferred for deterministic typography, diagrams, data, and designed
  motion sections, and may be selected as the primary runtime for motion-heavy work.
- TopView is a manual external production option for selected high-value shots only.
- Record the user's choice and rationale as `render_runtime_selection` in `decision_log`.
- If only one runtime is actually available, present the missing runtime and its concrete
  constraint instead of disguising the situation as a default.

## Gate Standard

`GATE_TOPIC` locks concept, audience, runtime band, narrative promise, and primary render
family. Its `render_runtime_selection` records the exact `render_runtime`; it does not
approve script text, asset generation, spending, or publishing.

## Forbidden

- Starting generation while comparing proposals
- Hiding paid/manual work inside a generic AI route
- Locking a renderer without showing the practical alternative
- Promising facts outside the evidence registry
