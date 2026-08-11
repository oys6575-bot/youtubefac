---
card_id: camera.variable_velocity_push
type: visual-technique
title: Variable-velocity camera push
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: camera.variable_velocity_push
category: camera
selectable: true
priority: 99
phases:
- visual_plan
- animatic
- production
- compose
intents:
- variable_camera_speed
- photo_to_motion
- camera_motion
- attention_landing
tags:
- speed_ramp
- push_in
- slow_fast_slow
- easing
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
- REMOTION
source_path: .agents/skills/hyperframes-animation/rules/nudge-curve.md
canonical_source: config/visual-technique-registry.yaml
---

# Variable-velocity camera push

## Purpose

Accelerate through low-information space and decelerate into the factual or emotional focal point.

## Selection cues

- variable_camera_speed
- photo_to_motion
- camera_motion
- attention_landing

## Directing instructions

- Put the fastest motion between information beats, not across text that must be read.
- Let the landing hold long enough for recognition.

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
  "label": "HyperFrames nudge curve",
  "license": "Apache-2.0",
  "path": ".agents/skills/hyperframes-animation/rules/nudge-curve.md"
}
```

## Canonical record

```json
{
  "id": "camera.variable_velocity_push",
  "name": "Variable-velocity camera push",
  "description": "Accelerate through low-information space and decelerate into the factual or emotional focal point.",
  "category": "camera",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 99,
  "phases": [
    "visual_plan",
    "animatic",
    "production",
    "compose"
  ],
  "intents": [
    "variable_camera_speed",
    "photo_to_motion",
    "camera_motion",
    "attention_landing"
  ],
  "tags": [
    "speed_ramp",
    "push_in",
    "slow_fast_slow",
    "easing"
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
    "label": "HyperFrames nudge curve",
    "license": "Apache-2.0",
    "path": ".agents/skills/hyperframes-animation/rules/nudge-curve.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Put the fastest motion between information beats, not across text that must be read.",
    "Let the landing hold long enough for recognition."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/hyperframes-animation|hyperframes-animation]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
