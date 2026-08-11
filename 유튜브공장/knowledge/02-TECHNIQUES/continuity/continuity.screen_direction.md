---
card_id: continuity.screen_direction
type: visual-technique
title: Preserve action and eye-line direction
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: continuity.screen_direction
category: continuity
selectable: true
priority: 91
phases:
- visual_plan
- production
- edit
intents:
- screen_direction
- action_continuity
- eye_line
tags:
- continuity
- match_action
- direction
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: .agents/skills/shot-composition/references/camera-and-grids.md
canonical_source: config/visual-technique-registry.yaml
---

# Preserve action and eye-line direction

## Purpose

Maintain tool travel, gaze, material flow, and screen direction unless the cut deliberately disrupts them.

## Selection cues

- screen_direction
- action_continuity
- eye_line

## Directing instructions

- Record the dominant vector for each process action.
- Cross the axis only with an orienting shot or a deliberate disorientation beat.

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
- ANY

## Source and provenance

```json
{
  "type": "local_skill",
  "label": "Shot Composition",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/shot-composition/references/camera-and-grids.md"
}
```

## Canonical record

```json
{
  "id": "continuity.screen_direction",
  "name": "Preserve action and eye-line direction",
  "description": "Maintain tool travel, gaze, material flow, and screen direction unless the cut deliberately disrupts them.",
  "category": "continuity",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 91,
  "phases": [
    "visual_plan",
    "production",
    "edit"
  ],
  "intents": [
    "screen_direction",
    "action_continuity",
    "eye_line"
  ],
  "tags": [
    "continuity",
    "match_action",
    "direction"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "local_skill",
    "label": "Shot Composition",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/shot-composition/references/camera-and-grids.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Record the dominant vector for each process action.",
    "Cross the axis only with an orienting shot or a deliberate disorientation beat."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/shot-composition|shot-composition]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
