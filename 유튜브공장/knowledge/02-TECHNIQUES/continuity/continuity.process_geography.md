---
card_id: continuity.process_geography
type: visual-technique
title: Establish process geography
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: continuity.process_geography
category: continuity
selectable: true
priority: 98
phases:
- visual_plan
- production
- edit
intents:
- process_geography
- spatial_orientation
- craft_process
tags:
- wide_shot
- geography
- process
- continuity
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: .agents/skills/shot-composition/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Establish process geography

## Purpose

Show the relationship among maker, tool, material, and workspace before fragmenting into details.

## Selection cues

- process_geography
- spatial_orientation
- craft_process

## Directing instructions

- Use an establishing relationship shot before a run of macros.
- Re-establish geography after a meaningful location or process-axis change.

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
  "id": "continuity.process_geography",
  "name": "Establish process geography",
  "description": "Show the relationship among maker, tool, material, and workspace before fragmenting into details.",
  "category": "continuity",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 98,
  "phases": [
    "visual_plan",
    "production",
    "edit"
  ],
  "intents": [
    "process_geography",
    "spatial_orientation",
    "craft_process"
  ],
  "tags": [
    "wide_shot",
    "geography",
    "process",
    "continuity"
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
    "Use an establishing relationship shot before a run of macros.",
    "Re-establish geography after a meaningful location or process-axis change."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/shot-composition|shot-composition]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
