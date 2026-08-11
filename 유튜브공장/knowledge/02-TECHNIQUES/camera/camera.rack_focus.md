---
card_id: camera.rack_focus
type: visual-technique
title: Two-plane rack focus
status: ON_DEMAND
knowledge_schema: '1.0'
generated: true
technique_id: camera.rack_focus
category: camera
selectable: true
priority: 70
phases:
- visual_plan
- compose
intents:
- rack_focus
- depth_shift
- attention_shift
tags:
- blur
- depth_of_field
- focus
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
source_path: .agents/skills/hyperframes-animation/rules/depth-of-field-blur.md
canonical_source: config/visual-technique-registry.yaml
---

# Two-plane rack focus

## Purpose

Shift sharpness between authored depth planes to redirect attention without moving the whole frame.

## Selection cues

- rack_focus
- depth_shift
- attention_shift

## Directing instructions

- Keep one plane genuinely sharp at all times.
- Use one motivated focus transfer rather than continuous focus hunting.

## Constraints and failure modes

- Status: `ON_DEMAND`
- Selectable: `true`
- Human opt-in: `true`
- License review: `false`
- Network required: `false`

## Route and runtime use

Providers:
- GENERIC

Runtimes:
- HYPERFRAMES

## Source and provenance

```json
{
  "type": "local_skill",
  "label": "HyperFrames depth-of-field rule",
  "license": "Apache-2.0",
  "path": ".agents/skills/hyperframes-animation/rules/depth-of-field-blur.md"
}
```

## Canonical record

```json
{
  "id": "camera.rack_focus",
  "name": "Two-plane rack focus",
  "description": "Shift sharpness between authored depth planes to redirect attention without moving the whole frame.",
  "category": "camera",
  "status": "ON_DEMAND",
  "selectable": true,
  "priority": 70,
  "phases": [
    "visual_plan",
    "compose"
  ],
  "intents": [
    "rack_focus",
    "depth_shift",
    "attention_shift"
  ],
  "tags": [
    "blur",
    "depth_of_field",
    "focus"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "HYPERFRAMES"
  ],
  "source": {
    "type": "local_skill",
    "label": "HyperFrames depth-of-field rule",
    "license": "Apache-2.0",
    "path": ".agents/skills/hyperframes-animation/rules/depth-of-field-blur.md"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": false,
    "requires_network": false,
    "note": "Use only when the shot has authored depth planes."
  },
  "directives": [
    "Keep one plane genuinely sharp at all times.",
    "Use one motivated focus transfer rather than continuous focus hunting."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/hyperframes-animation|hyperframes-animation]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
