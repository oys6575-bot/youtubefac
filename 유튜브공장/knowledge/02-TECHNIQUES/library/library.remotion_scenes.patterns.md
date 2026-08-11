---
card_id: library.remotion_scenes.patterns
type: visual-technique
title: Remotion Scenes implementation library
status: ON_DEMAND
knowledge_schema: '1.0'
generated: true
technique_id: library.remotion_scenes.patterns
category: library
selectable: false
priority: 45
phases:
- compose
intents:
- remotion_scene_library
- motion_graphics_pattern
- implementation_reference
tags:
- remotion
- react
- source_library
provider_scopes:
- GENERIC
render_runtimes:
- REMOTION
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# Remotion Scenes implementation library

## Purpose

Large collection of ready-made React scene patterns retained for a future Remotion-locked shot.

## Selection cues

- remotion_scene_library
- motion_graphics_pattern
- implementation_reference

## Directing instructions

- Reuse mechanics, then redesign the scene for the approved visual grammar.

## Constraints and failure modes

- Status: `ON_DEMAND`
- Selectable: `false`
- Human opt-in: `true`
- License review: `false`
- Network required: `true`

## Route and runtime use

Providers:
- GENERIC

Runtimes:
- REMOTION

## Source and provenance

```json
{
  "type": "external_repository",
  "label": "Remotion Scenes",
  "license": "MIT",
  "manifest_id": "github.remotion_scenes"
}
```

## Canonical record

```json
{
  "id": "library.remotion_scenes.patterns",
  "name": "Remotion Scenes implementation library",
  "description": "Large collection of ready-made React scene patterns retained for a future Remotion-locked shot.",
  "category": "library",
  "status": "ON_DEMAND",
  "selectable": false,
  "priority": 45,
  "phases": [
    "compose"
  ],
  "intents": [
    "remotion_scene_library",
    "motion_graphics_pattern",
    "implementation_reference"
  ],
  "tags": [
    "remotion",
    "react",
    "source_library"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "REMOTION"
  ],
  "source": {
    "type": "external_repository",
    "label": "Remotion Scenes",
    "license": "MIT",
    "manifest_id": "github.remotion_scenes"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": false,
    "requires_network": true,
    "note": "Stage only after render_runtime is locked to Remotion."
  },
  "directives": [
    "Reuse mechanics, then redesign the scene for the approved visual grammar."
  ]
}
```

## Related knowledge

- [[06-SOURCES/github/github.remotion_scenes|github.remotion_scenes]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
