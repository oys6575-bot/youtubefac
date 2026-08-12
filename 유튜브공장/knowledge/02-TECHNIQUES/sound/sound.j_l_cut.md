---
card_id: sound.j_l_cut
type: visual-technique
title: J-cut and L-cut narration flow
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: sound.j_l_cut
category: sound
selectable: true
priority: 87
phases:
- animatic
- edit
intents:
- j_cut
- l_cut
- narration_flow
tags:
- audio_edit
- transition
- anticipation
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: skills/creative/sound-design.md
canonical_source: config/visual-technique-registry.yaml
---

# J-cut and L-cut narration flow

## Purpose

Offset picture and sound boundaries to create anticipation or preserve emotional consequence.

## Selection cues

- j_cut
- l_cut
- narration_flow

## Directing instructions

- Use early sound to pose the next question and late sound to preserve the prior consequence.
- Do not let the music bed erase meaningful production sound.

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
  "id": "sound.j_l_cut",
  "name": "J-cut and L-cut narration flow",
  "description": "Offset picture and sound boundaries to create anticipation or preserve emotional consequence.",
  "category": "sound",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 87,
  "phases": [
    "animatic",
    "edit"
  ],
  "intents": [
    "j_cut",
    "l_cut",
    "narration_flow"
  ],
  "tags": [
    "audio_edit",
    "transition",
    "anticipation"
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
    "Use early sound to pose the next question and late sound to preserve the prior consequence.",
    "Do not let the music bed erase meaningful production sound."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
