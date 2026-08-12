---
card_id: camera.slow_observational_push
type: visual-technique
title: Slow observational push
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: camera.slow_observational_push
category: camera
selectable: true
priority: 82
phases:
- visual_plan
- animatic
- production
intents:
- observational_camera
- contemplation
- evidence_hold
tags:
- slow_push
- documentary
- inspection
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: config/visual-grammars/HERITAGE_FORGE.yaml
canonical_source: config/visual-technique-registry.yaml
---

# Slow observational push

## Purpose

Use a restrained push when the viewer needs time to inspect labor, texture, or evidence.

## Selection cues

- observational_camera
- contemplation
- evidence_hold

## Directing instructions

- Start from a composed readable frame and move only enough to focus attention.
- Do not repeat the same slow push across consecutive shots.

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
  "id": "camera.slow_observational_push",
  "name": "Slow observational push",
  "description": "Use a restrained push when the viewer needs time to inspect labor, texture, or evidence.",
  "category": "camera",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 82,
  "phases": [
    "visual_plan",
    "animatic",
    "production"
  ],
  "intents": [
    "observational_camera",
    "contemplation",
    "evidence_hold"
  ],
  "tags": [
    "slow_push",
    "documentary",
    "inspection"
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
    "Start from a composed readable frame and move only enough to focus attention.",
    "Do not repeat the same slow push across consecutive shots."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
