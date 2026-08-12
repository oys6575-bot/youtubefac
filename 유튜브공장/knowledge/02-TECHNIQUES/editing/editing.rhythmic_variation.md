---
card_id: editing.rhythmic_variation
type: visual-technique
title: Non-uniform edit rhythm
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: editing.rhythmic_variation
category: editing
selectable: true
priority: 89
phases:
- animatic
- edit
- compose
intents:
- rhythmic_variation
- avoid_ai_smoothness
- beat_sync
tags:
- rhythm
- hard_cut
- hold
- varied_easing
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: .agents/skills/beat-sync-editing/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Non-uniform edit rhythm

## Purpose

Mix hard cuts, short transitions, held frames, and varied easing so the edit does not feel uniformly synthetic.

## Selection cues

- rhythmic_variation
- avoid_ai_smoothness
- beat_sync

## Directing instructions

- Let content and sound accents determine cut density.
- Avoid applying one transition preset to every boundary.

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
  "type": "local_skill",
  "label": "Beat Sync Editing",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/beat-sync-editing/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "editing.rhythmic_variation",
  "name": "Non-uniform edit rhythm",
  "description": "Mix hard cuts, short transitions, held frames, and varied easing so the edit does not feel uniformly synthetic.",
  "category": "editing",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 89,
  "phases": [
    "animatic",
    "edit",
    "compose"
  ],
  "intents": [
    "rhythmic_variation",
    "avoid_ai_smoothness",
    "beat_sync"
  ],
  "tags": [
    "rhythm",
    "hard_cut",
    "hold",
    "varied_easing"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "local_skill",
    "label": "Beat Sync Editing",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/beat-sync-editing/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Let content and sound accents determine cut density.",
    "Avoid applying one transition preset to every boundary."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/beat-sync-editing|beat-sync-editing]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
