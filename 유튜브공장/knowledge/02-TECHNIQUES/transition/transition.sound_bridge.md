---
card_id: transition.sound_bridge
type: visual-technique
title: Sound bridge across picture cuts
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: transition.sound_bridge
category: transition
selectable: true
priority: 88
phases:
- visual_plan
- animatic
- edit
intents:
- sound_bridge
- audio_continuity
- anticipation
tags:
- j_cut
- l_cut
- ambience
- transition
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: skills/creative/sound-design.md
canonical_source: config/visual-technique-registry.yaml
---

# Sound bridge across picture cuts

## Purpose

Carry a process sound, ambience, or narration edge across a visual boundary to preserve continuity or anticipation.

## Selection cues

- sound_bridge
- audio_continuity
- anticipation

## Directing instructions

- Start the next sound early to create anticipation or let the prior sound decay to preserve consequence.
- Keep documentary source sound distinct from designed effects.

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
  "id": "transition.sound_bridge",
  "name": "Sound bridge across picture cuts",
  "description": "Carry a process sound, ambience, or narration edge across a visual boundary to preserve continuity or anticipation.",
  "category": "transition",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 88,
  "phases": [
    "visual_plan",
    "animatic",
    "edit"
  ],
  "intents": [
    "sound_bridge",
    "audio_continuity",
    "anticipation"
  ],
  "tags": [
    "j_cut",
    "l_cut",
    "ambience",
    "transition"
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
    "Start the next sound early to create anticipation or let the prior sound decay to preserve consequence.",
    "Keep documentary source sound distinct from designed effects."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
