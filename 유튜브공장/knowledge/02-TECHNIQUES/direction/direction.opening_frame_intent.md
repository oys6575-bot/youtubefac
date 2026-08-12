---
card_id: direction.opening_frame_intent
type: visual-technique
title: Deliberate opening-frame intent
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: direction.opening_frame_intent
category: direction
selectable: true
priority: 97
phases:
- visual_plan
- animatic
- production
intents:
- opening_frame
- first_frame
- delayed_reveal
tags:
- composition
- reveal
- visual_anchor
- shot_design
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: knowledge/10-RESEARCH/cinematic-direction/Camera-Spatial-Physics-Direction.md
canonical_source: config/visual-technique-registry.yaml
---

# Deliberate opening-frame intent

## Purpose

Define the first readable image, its visible subjects, and any delayed reveal before describing motion.

## Selection cues

- opening_frame
- first_frame
- delayed_reveal

## Directing instructions

- Describe what is visible before the first movement begins.
- Use an empty or partial opening only when the delayed reveal has a narrative purpose.

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
  "id": "direction.opening_frame_intent",
  "name": "Deliberate opening-frame intent",
  "description": "Define the first readable image, its visible subjects, and any delayed reveal before describing motion.",
  "category": "direction",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 97,
  "phases": [
    "visual_plan",
    "animatic",
    "production"
  ],
  "intents": [
    "opening_frame",
    "first_frame",
    "delayed_reveal"
  ],
  "tags": [
    "composition",
    "reveal",
    "visual_anchor",
    "shot_design"
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
    "Describe what is visible before the first movement begins.",
    "Use an empty or partial opening only when the delayed reveal has a narrative purpose."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
