---
card_id: graphics.data_relationship_motion
type: visual-technique
title: Animate data relationships
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: graphics.data_relationship_motion
category: graphics
selectable: true
priority: 86
phases:
- visual_plan
- animatic
- compose
intents:
- data_relationship
- comparison
- statistic_motion
tags:
- chart
- data
- comparison
- exact_fact
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
- REMOTION
source_path: .agents/skills/color-motion/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Animate data relationships

## Purpose

Move position, scale, and connection to explain a relationship instead of decorating a number.

## Selection cues

- data_relationship
- comparison
- statistic_motion

## Directing instructions

- Keep no more than two information layers active at once.
- Make the final quantitative relationship inspectable in a stable hold.

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
  "label": "Color Motion",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/color-motion/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "graphics.data_relationship_motion",
  "name": "Animate data relationships",
  "description": "Move position, scale, and connection to explain a relationship instead of decorating a number.",
  "category": "graphics",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 86,
  "phases": [
    "visual_plan",
    "animatic",
    "compose"
  ],
  "intents": [
    "data_relationship",
    "comparison",
    "statistic_motion"
  ],
  "tags": [
    "chart",
    "data",
    "comparison",
    "exact_fact"
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
    "label": "Color Motion",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/color-motion/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Keep no more than two information layers active at once.",
    "Make the final quantitative relationship inspectable in a stable hold."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/color-motion|color-motion]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
