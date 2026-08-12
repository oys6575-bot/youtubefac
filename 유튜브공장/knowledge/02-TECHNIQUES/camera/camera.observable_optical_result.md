---
card_id: camera.observable_optical_result
type: visual-technique
title: Observable optical result
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: camera.observable_optical_result
category: camera
selectable: true
priority: 95
phases:
- visual_plan
- animatic
- production
intents:
- optical_result
- lens_intent
- perspective
tags:
- optics
- depth
- compression
- focus
- subject_scale
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: knowledge/10-RESEARCH/cinematic-direction/Camera-Spatial-Physics-Direction.md
canonical_source: config/visual-technique-registry.yaml
---

# Observable optical result

## Purpose

Specify how perspective, subject scale, background, and focus should look instead of relying on lens jargon alone.

## Selection cues

- optical_result
- lens_intent
- perspective

## Directing instructions

- State the intended perspective, background behavior, focus behavior, and subject scale in visible terms.
- Treat focal length as an optional implementation hint, never as a substitute for the result.

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
  "label": "Camera spatial physics synthesis",
  "license": "PROJECT_LOCAL",
  "path": "knowledge/10-RESEARCH/cinematic-direction/Camera-Spatial-Physics-Direction.md"
}
```

## Canonical record

```json
{
  "id": "camera.observable_optical_result",
  "name": "Observable optical result",
  "description": "Specify how perspective, subject scale, background, and focus should look instead of relying on lens jargon alone.",
  "category": "camera",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 95,
  "phases": [
    "visual_plan",
    "animatic",
    "production"
  ],
  "intents": [
    "optical_result",
    "lens_intent",
    "perspective"
  ],
  "tags": [
    "optics",
    "depth",
    "compression",
    "focus",
    "subject_scale"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "project_doc",
    "label": "Camera spatial physics synthesis",
    "license": "PROJECT_LOCAL",
    "path": "knowledge/10-RESEARCH/cinematic-direction/Camera-Spatial-Physics-Direction.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "State the intended perspective, background behavior, focus behavior, and subject scale in visible terms.",
    "Treat focal length as an optional implementation hint, never as a substitute for the result."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
