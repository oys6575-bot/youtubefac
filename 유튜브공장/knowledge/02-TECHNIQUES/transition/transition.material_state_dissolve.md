---
card_id: transition.material_state_dissolve
type: visual-technique
title: Material-state dissolve
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: transition.material_state_dissolve
category: transition
selectable: true
priority: 77
phases:
- visual_plan
- animatic
- edit
intents:
- material_transformation
- elapsed_time
- memory
tags:
- dissolve
- patina
- heat
- time
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: config/visual-grammars/HERITAGE_FORGE.yaml
canonical_source: config/visual-technique-registry.yaml
---

# Material-state dissolve

## Purpose

Use a restrained dissolve only for elapsed time, memory, or a visible material transformation.

## Selection cues

- material_transformation
- elapsed_time
- memory

## Directing instructions

- Align the material feature that survives the dissolve.
- Do not use long dissolves as a universal polish layer.

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
  "type": "project_doc",
  "label": "Heritage Forge grammar",
  "license": "PROJECT_LOCAL",
  "path": "config/visual-grammars/HERITAGE_FORGE.yaml"
}
```

## Canonical record

```json
{
  "id": "transition.material_state_dissolve",
  "name": "Material-state dissolve",
  "description": "Use a restrained dissolve only for elapsed time, memory, or a visible material transformation.",
  "category": "transition",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 77,
  "phases": [
    "visual_plan",
    "animatic",
    "edit"
  ],
  "intents": [
    "material_transformation",
    "elapsed_time",
    "memory"
  ],
  "tags": [
    "dissolve",
    "patina",
    "heat",
    "time"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "project_doc",
    "label": "Heritage Forge grammar",
    "license": "PROJECT_LOCAL",
    "path": "config/visual-grammars/HERITAGE_FORGE.yaml"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Align the material feature that survives the dissolve.",
    "Do not use long dissolves as a universal polish layer."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
