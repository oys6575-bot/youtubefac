---
card_id: editing.radio_paper_cut
type: visual-technique
title: Story-first radio and paper edit
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: editing.radio_paper_cut
category: editing
selectable: true
priority: 100
phases:
- script
- visual_plan
- animatic
- edit
intents:
- radio_edit
- paper_edit
- story_structure
tags:
- documentary
- a_roll
- story_lock
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: skills/creative/long-form.md
canonical_source: config/visual-technique-registry.yaml
---

# Story-first radio and paper edit

## Purpose

Lock the argument and emotional order with narration and evidence before filling coverage gaps with B-roll.

## Selection cues

- radio_edit
- paper_edit
- story_structure

## Directing instructions

- Build the story without decorative coverage first.
- Treat missing visual proof as a story hole, not an excuse for generic B-roll.

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
  "label": "Long-form editing",
  "license": "PROJECT_LOCAL",
  "path": "skills/creative/long-form.md"
}
```

## Canonical record

```json
{
  "id": "editing.radio_paper_cut",
  "name": "Story-first radio and paper edit",
  "description": "Lock the argument and emotional order with narration and evidence before filling coverage gaps with B-roll.",
  "category": "editing",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 100,
  "phases": [
    "script",
    "visual_plan",
    "animatic",
    "edit"
  ],
  "intents": [
    "radio_edit",
    "paper_edit",
    "story_structure"
  ],
  "tags": [
    "documentary",
    "a_roll",
    "story_lock"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "project_doc",
    "label": "Long-form editing",
    "license": "PROJECT_LOCAL",
    "path": "skills/creative/long-form.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Build the story without decorative coverage first.",
    "Treat missing visual proof as a story hole, not an excuse for generic B-roll."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
