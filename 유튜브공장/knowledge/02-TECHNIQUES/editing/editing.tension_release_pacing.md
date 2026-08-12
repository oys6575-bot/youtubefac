---
card_id: editing.tension_release_pacing
type: visual-technique
title: Tension and release pacing
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: editing.tension_release_pacing
category: editing
selectable: true
priority: 92
phases:
- visual_plan
- animatic
- edit
intents:
- tension_release
- pacing_arc
- rhythm
tags:
- pace
- hold
- acceleration
- payoff
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: .agents/skills/motion-art-direction/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Tension and release pacing

## Purpose

Alternate compression, acceleration, stillness, and payoff instead of maintaining one smooth tempo.

## Selection cues

- tension_release
- pacing_arc
- rhythm

## Directing instructions

- Name the sequence rhythm before assigning shot durations.
- Use stillness after intense motion as a deliberate release.

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
  "label": "Motion Art Direction",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/motion-art-direction/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "editing.tension_release_pacing",
  "name": "Tension and release pacing",
  "description": "Alternate compression, acceleration, stillness, and payoff instead of maintaining one smooth tempo.",
  "category": "editing",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 92,
  "phases": [
    "visual_plan",
    "animatic",
    "edit"
  ],
  "intents": [
    "tension_release",
    "pacing_arc",
    "rhythm"
  ],
  "tags": [
    "pace",
    "hold",
    "acceleration",
    "payoff"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "local_skill",
    "label": "Motion Art Direction",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/motion-art-direction/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Name the sequence rhythm before assigning shot durations.",
    "Use stillness after intense motion as a deliberate release."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/motion-art-direction|motion-art-direction]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
