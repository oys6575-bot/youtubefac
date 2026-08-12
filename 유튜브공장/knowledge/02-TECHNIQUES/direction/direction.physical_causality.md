---
card_id: direction.physical_causality
type: visual-technique
title: Physical causality cues
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: direction.physical_causality
category: direction
selectable: true
priority: 93
phases:
- visual_plan
- animatic
- production
intents:
- physical_causality
- material_response
- believable_motion
tags:
- physics
- weight
- contact
- inertia
- environment
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: knowledge/10-RESEARCH/cinematic-direction/Camera-Spatial-Physics-Direction.md
canonical_source: config/visual-technique-registry.yaml
---

# Physical causality cues

## Purpose

Make motion obey contact, weight, inertia, resistance, airflow, and material response so cause and effect remain legible.

## Selection cues

- physical_causality
- material_response
- believable_motion

## Directing instructions

- Name the force, contact, and visible material response for every important movement.
- Reject motion that changes position without a plausible initiating cause or settling behavior.

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
  "id": "direction.physical_causality",
  "name": "Physical causality cues",
  "description": "Make motion obey contact, weight, inertia, resistance, airflow, and material response so cause and effect remain legible.",
  "category": "direction",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 93,
  "phases": [
    "visual_plan",
    "animatic",
    "production"
  ],
  "intents": [
    "physical_causality",
    "material_response",
    "believable_motion"
  ],
  "tags": [
    "physics",
    "weight",
    "contact",
    "inertia",
    "environment"
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
    "Name the force, contact, and visible material response for every important movement.",
    "Reject motion that changes position without a plausible initiating cause or settling behavior."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
