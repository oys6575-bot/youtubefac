---
card_id: direction.sequence_meaning_first
type: visual-technique
title: Sequence meaning before decoration
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: direction.sequence_meaning_first
category: direction
selectable: true
priority: 100
phases:
- visual_plan
- animatic
intents:
- sequence_meaning
- evidence_first
- narrative_function
tags:
- documentary
- sequence
- proof
- story
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: .agents/skills/motion-art-direction/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Sequence meaning before decoration

## Purpose

Resolve the viewer question, dramatic turn, proof, and exit before choosing camera ornament.

## Selection cues

- sequence_meaning
- evidence_first
- narrative_function

## Directing instructions

- Write the sequence question and exit condition before listing shots.
- Reject a beautiful shot that does not add fact, feeling, or causality.

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
  "id": "direction.sequence_meaning_first",
  "name": "Sequence meaning before decoration",
  "description": "Resolve the viewer question, dramatic turn, proof, and exit before choosing camera ornament.",
  "category": "direction",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 100,
  "phases": [
    "visual_plan",
    "animatic"
  ],
  "intents": [
    "sequence_meaning",
    "evidence_first",
    "narrative_function"
  ],
  "tags": [
    "documentary",
    "sequence",
    "proof",
    "story"
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
    "Write the sequence question and exit condition before listing shots.",
    "Reject a beautiful shot that does not add fact, feeling, or causality."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/motion-art-direction|motion-art-direction]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
