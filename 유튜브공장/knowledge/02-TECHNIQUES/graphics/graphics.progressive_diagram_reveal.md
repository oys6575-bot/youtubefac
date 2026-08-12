---
card_id: graphics.progressive_diagram_reveal
type: visual-technique
title: Progressive mechanism reveal
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: graphics.progressive_diagram_reveal
category: graphics
selectable: true
priority: 90
phases:
- visual_plan
- animatic
- compose
intents:
- mechanism_explainer
- progressive_reveal
- process_diagram
tags:
- diagram
- connector
- sequence
- causality
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
- REMOTION
source_path: .agents/skills/diagram-animation/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Progressive mechanism reveal

## Purpose

Reveal a process diagram in the same order that narration explains parts and relationships.

## Selection cues

- mechanism_explainer
- progressive_reveal
- process_diagram

## Directing instructions

- Add each label only when its object or relationship becomes relevant.
- Freeze the completed diagram before leaving the scene.

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
  "label": "Diagram Animation",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/diagram-animation/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "graphics.progressive_diagram_reveal",
  "name": "Progressive mechanism reveal",
  "description": "Reveal a process diagram in the same order that narration explains parts and relationships.",
  "category": "graphics",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 90,
  "phases": [
    "visual_plan",
    "animatic",
    "compose"
  ],
  "intents": [
    "mechanism_explainer",
    "progressive_reveal",
    "process_diagram"
  ],
  "tags": [
    "diagram",
    "connector",
    "sequence",
    "causality"
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
    "label": "Diagram Animation",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/diagram-animation/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Add each label only when its object or relationship becomes relevant.",
    "Freeze the completed diagram before leaving the scene."
  ]
}
```

## Related knowledge

- [[07-SKILLS/optional/diagram-animation|diagram-animation]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
