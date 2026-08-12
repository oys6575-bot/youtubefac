---
card_id: sound.material_motif
type: visual-technique
title: Material sound motif
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: sound.material_motif
category: sound
selectable: true
priority: 84
phases:
- visual_plan
- animatic
- edit
intents:
- material_motif
- tactile_sound
- craft_process
tags:
- hammer
- scrape
- heat
- resonance
- motif
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: skills/creative/sound-design.md
canonical_source: config/visual-technique-registry.yaml
---

# Material sound motif

## Purpose

Recur a specific tactile sound to bind process stages without repeating the same image.

## Selection cues

- material_motif
- tactile_sound
- craft_process

## Directing instructions

- Preserve real source sound when available and label designed substitutes.
- Vary distance and intensity while keeping the motif recognizable.

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
  "label": "Sound Design",
  "license": "PROJECT_LOCAL",
  "path": "skills/creative/sound-design.md"
}
```

## Canonical record

```json
{
  "id": "sound.material_motif",
  "name": "Material sound motif",
  "description": "Recur a specific tactile sound to bind process stages without repeating the same image.",
  "category": "sound",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 84,
  "phases": [
    "visual_plan",
    "animatic",
    "edit"
  ],
  "intents": [
    "material_motif",
    "tactile_sound",
    "craft_process"
  ],
  "tags": [
    "hammer",
    "scrape",
    "heat",
    "resonance",
    "motif"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "project_doc",
    "label": "Sound Design",
    "license": "PROJECT_LOCAL",
    "path": "skills/creative/sound-design.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Preserve real source sound when available and label designed substitutes.",
    "Vary distance and intensity while keeping the motif recognizable."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
