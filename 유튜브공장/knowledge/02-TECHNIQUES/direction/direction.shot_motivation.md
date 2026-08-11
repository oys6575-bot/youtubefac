---
card_id: direction.shot_motivation
type: visual-technique
title: Motivated shot design
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: direction.shot_motivation
category: direction
selectable: true
priority: 96
phases:
- visual_plan
- animatic
intents:
- shot_motivation
- narrative_function
- composition
tags:
- shot_design
- hierarchy
- documentary
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: .agents/skills/shot-composition/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Motivated shot design

## Purpose

Give each shot one narrative function and let composition follow that function.

## Selection cues

- shot_motivation
- narrative_function
- composition

## Directing instructions

- State what the viewer learns or feels before naming lens, angle, or motion.
- Keep one dominant visual idea per shot.

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
  "label": "Shot Composition",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/shot-composition/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "direction.shot_motivation",
  "name": "Motivated shot design",
  "description": "Give each shot one narrative function and let composition follow that function.",
  "category": "direction",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 96,
  "phases": [
    "visual_plan",
    "animatic"
  ],
  "intents": [
    "shot_motivation",
    "narrative_function",
    "composition"
  ],
  "tags": [
    "shot_design",
    "hierarchy",
    "documentary"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "local_skill",
    "label": "Shot Composition",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/shot-composition/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "State what the viewer learns or feels before naming lens, angle, or motion.",
    "Keep one dominant visual idea per shot."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/shot-composition|shot-composition]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
