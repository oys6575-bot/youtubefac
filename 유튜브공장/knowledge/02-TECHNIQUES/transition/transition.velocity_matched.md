---
card_id: transition.velocity_matched
type: visual-technique
title: Velocity-matched handoff
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: transition.velocity_matched
category: transition
selectable: true
priority: 90
phases:
- animatic
- edit
- compose
intents:
- velocity_match
- continuous_camera
- whip_transition
- camera_motion
tags:
- speed_match
- blur
- directional_cut
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
- REMOTION
source_path: .agents/skills/hyperframes-creative/references/beat-direction.md
canonical_source: config/visual-technique-registry.yaml
---

# Velocity-matched handoff

## Purpose

Meet an accelerating exit with a decelerating entrance so two shots read as one continuous move.

## Selection cues

- velocity_match
- continuous_camera
- whip_transition
- camera_motion

## Directing instructions

- Match exit and entry direction and approximate peak velocity.
- Resolve blur immediately at the new focal point.

## Constraints and failure modes

- Status: `ACTIVE`
- Selectable: `true`
- Human opt-in: `false`
- License review: `false`
- Network required: `false`

## Route and runtime use

Providers:
- GENERIC

Runtimes:
- HYPERFRAMES
- REMOTION

## Source and provenance

```json
{
  "type": "local_skill",
  "label": "HyperFrames beat direction",
  "license": "Apache-2.0",
  "path": ".agents/skills/hyperframes-creative/references/beat-direction.md"
}
```

## Canonical record

```json
{
  "id": "transition.velocity_matched",
  "name": "Velocity-matched handoff",
  "description": "Meet an accelerating exit with a decelerating entrance so two shots read as one continuous move.",
  "category": "transition",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 90,
  "phases": [
    "animatic",
    "edit",
    "compose"
  ],
  "intents": [
    "velocity_match",
    "continuous_camera",
    "whip_transition",
    "camera_motion"
  ],
  "tags": [
    "speed_match",
    "blur",
    "directional_cut"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "HYPERFRAMES",
    "REMOTION"
  ],
  "source": {
    "type": "local_skill",
    "label": "HyperFrames beat direction",
    "license": "Apache-2.0",
    "path": ".agents/skills/hyperframes-creative/references/beat-direction.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Match exit and entry direction and approximate peak velocity.",
    "Resolve blur immediately at the new focal point."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/hyperframes-creative|hyperframes-creative]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
