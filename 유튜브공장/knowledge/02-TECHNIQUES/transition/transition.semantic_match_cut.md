---
card_id: transition.semantic_match_cut
type: visual-technique
title: Semantic match cut
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: transition.semantic_match_cut
category: transition
selectable: true
priority: 99
phases:
- visual_plan
- animatic
- edit
- compose
intents:
- semantic_transition
- match_cut
- visual_bridge
tags:
- shape_match
- gesture_match
- material_match
- meaning
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: .agents/skills/beat-sync-editing/references/editing-techniques.md
canonical_source: config/visual-technique-registry.yaml
---

# Semantic match cut

## Purpose

Join shots through a shared shape, gesture, material state, light vector, or action meaning.

## Selection cues

- semantic_transition
- match_cut
- visual_bridge

## Directing instructions

- Name the shared visual or causal property before approving the cut.
- Reject a morph that falsely implies factual continuity.

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
  "path": ".agents/skills/beat-sync-editing/references/editing-techniques.md"
}
```

## Canonical record

```json
{
  "id": "transition.semantic_match_cut",
  "name": "Semantic match cut",
  "description": "Join shots through a shared shape, gesture, material state, light vector, or action meaning.",
  "category": "transition",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 99,
  "phases": [
    "visual_plan",
    "animatic",
    "edit",
    "compose"
  ],
  "intents": [
    "semantic_transition",
    "match_cut",
    "visual_bridge"
  ],
  "tags": [
    "shape_match",
    "gesture_match",
    "material_match",
    "meaning"
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
    "path": ".agents/skills/beat-sync-editing/references/editing-techniques.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Name the shared visual or causal property before approving the cut.",
    "Reject a morph that falsely implies factual continuity."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/beat-sync-editing|beat-sync-editing]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
