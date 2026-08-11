---
card_id: graphics.map_spatial_context
type: visual-technique
title: Map as spatial argument
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: graphics.map_spatial_context
category: graphics
selectable: true
priority: 83
phases:
- visual_plan
- animatic
- compose
intents:
- map_context
- geographic_stakes
- route_animation
tags:
- map
- location
- distance
- route
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
- REMOTION
source_path: .agents/skills/map-animation/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Map as spatial argument

## Purpose

Use a map to establish distance, movement, distribution, or geographic stakes rather than as decoration.

## Selection cues

- map_context
- geographic_stakes
- route_animation

## Directing instructions

- State the geographic question the map answers.
- Keep labels exact and source-bound.

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
  "label": "Map Animation",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/map-animation/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "graphics.map_spatial_context",
  "name": "Map as spatial argument",
  "description": "Use a map to establish distance, movement, distribution, or geographic stakes rather than as decoration.",
  "category": "graphics",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 83,
  "phases": [
    "visual_plan",
    "animatic",
    "compose"
  ],
  "intents": [
    "map_context",
    "geographic_stakes",
    "route_animation"
  ],
  "tags": [
    "map",
    "location",
    "distance",
    "route"
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
    "label": "Map Animation",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/map-animation/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "State the geographic question the map answers.",
    "Keep labels exact and source-bound."
  ]
}
```

## Related knowledge

- [[07-SKILLS/optional/map-animation|map-animation]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
