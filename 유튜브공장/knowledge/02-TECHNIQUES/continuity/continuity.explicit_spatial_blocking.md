---
card_id: continuity.explicit_spatial_blocking
type: visual-technique
title: Explicit spatial blocking
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: continuity.explicit_spatial_blocking
category: continuity
selectable: true
priority: 96
phases:
- visual_plan
- animatic
- production
intents:
- spatial_blocking
- subject_placement
- action_continuity
tags:
- blocking
- geography
- eye_line
- screen_direction
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: knowledge/10-RESEARCH/cinematic-direction/Camera-Spatial-Physics-Direction.md
canonical_source: config/visual-technique-registry.yaml
---

# Explicit spatial blocking

## Purpose

Anchor every important subject in screen space and world space, including orientation, attention, and movement path.

## Selection cues

- spatial_blocking
- subject_placement
- action_continuity

## Directing instructions

- State where each subject begins, faces, looks, and travels relative to a stable anchor.
- Preserve the declared relationships across cuts unless the change itself is the story beat.

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
  "id": "continuity.explicit_spatial_blocking",
  "name": "Explicit spatial blocking",
  "description": "Anchor every important subject in screen space and world space, including orientation, attention, and movement path.",
  "category": "continuity",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 96,
  "phases": [
    "visual_plan",
    "animatic",
    "production"
  ],
  "intents": [
    "spatial_blocking",
    "subject_placement",
    "action_continuity"
  ],
  "tags": [
    "blocking",
    "geography",
    "eye_line",
    "screen_direction"
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
    "State where each subject begins, faces, looks, and travels relative to a stable anchor.",
    "Preserve the declared relationships across cuts unless the change itself is the story beat."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
