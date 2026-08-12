---
card_id: typography.kinetic_emphasis
type: visual-technique
title: Kinetic emphasis with semantic restraint
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: typography.kinetic_emphasis
category: typography
selectable: true
priority: 79
phases:
- visual_plan
- animatic
- compose
intents:
- kinetic_typography
- word_emphasis
- title_motion
tags:
- type
- emphasis
- timing
- hierarchy
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
- REMOTION
source_path: .agents/skills/kinetic-typography/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Kinetic emphasis with semantic restraint

## Purpose

Animate only the words whose timing or physical behavior clarifies meaning.

## Selection cues

- kinetic_typography
- word_emphasis
- title_motion

## Directing instructions

- Choose a motion verb for the emphasized word.
- Resolve to a stable readable state rather than constant motion.

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
  "label": "Kinetic Typography",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/kinetic-typography/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "typography.kinetic_emphasis",
  "name": "Kinetic emphasis with semantic restraint",
  "description": "Animate only the words whose timing or physical behavior clarifies meaning.",
  "category": "typography",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 79,
  "phases": [
    "visual_plan",
    "animatic",
    "compose"
  ],
  "intents": [
    "kinetic_typography",
    "word_emphasis",
    "title_motion"
  ],
  "tags": [
    "type",
    "emphasis",
    "timing",
    "hierarchy"
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
    "label": "Kinetic Typography",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/kinetic-typography/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Choose a motion verb for the emphasized word.",
    "Resolve to a stable readable state rather than constant motion."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/kinetic-typography|kinetic-typography]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
