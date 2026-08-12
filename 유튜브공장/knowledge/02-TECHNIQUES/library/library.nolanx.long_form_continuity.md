---
card_id: library.nolanx.long_form_continuity
type: visual-technique
title: NolanX long-form continuity library
status: ON_DEMAND
knowledge_schema: '1.0'
generated: true
technique_id: library.nolanx.long_form_continuity
category: library
selectable: false
priority: 50
phases:
- research
- visual_plan
intents:
- continuity_bible
- scene_blocking
- storyboard_shot_design
tags:
- long_form
- continuity
- source_library
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# NolanX long-form continuity library

## Purpose

On-demand continuity bible, blocking, shot-design, and visual-language modules for complex productions.

## Selection cues

- continuity_bible
- scene_blocking
- storyboard_shot_design

## Directing instructions

- Search and review a specific module; never load the whole collection into every scene.

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
- ANY

## Source and provenance

```json
{
  "type": "external_repository",
  "label": "NolanX",
  "license": "MIT",
  "manifest_id": "github.nolanx"
}
```

## Canonical record

```json
{
  "id": "library.nolanx.long_form_continuity",
  "name": "NolanX long-form continuity library",
  "description": "On-demand continuity bible, blocking, shot-design, and visual-language modules for complex productions.",
  "category": "library",
  "status": "ON_DEMAND",
  "selectable": false,
  "priority": 50,
  "phases": [
    "research",
    "visual_plan"
  ],
  "intents": [
    "continuity_bible",
    "scene_blocking",
    "storyboard_shot_design"
  ],
  "tags": [
    "long_form",
    "continuity",
    "source_library"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "external_repository",
    "label": "NolanX",
    "license": "MIT",
    "manifest_id": "github.nolanx"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": false,
    "requires_network": true,
    "note": "Stage only the needed module into the isolated cache."
  },
  "directives": [
    "Search and review a specific module; never load the whole collection into every scene."
  ]
}
```

## Related knowledge

- [[06-SOURCES/github/github.nolanx|github.nolanx]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
