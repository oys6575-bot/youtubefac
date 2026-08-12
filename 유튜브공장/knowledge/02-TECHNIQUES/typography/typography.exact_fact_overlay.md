---
card_id: typography.exact_fact_overlay
type: visual-technique
title: Evidence-bound exact typography
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: typography.exact_fact_overlay
category: typography
selectable: true
priority: 100
phases:
- visual_plan
- animatic
- compose
- qc
intents:
- exact_fact
- evidence_overlay
- readable_typography
tags:
- date
- statistic
- quotation
- claim_id
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
- REMOTION
source_path: .agents/skills/kinetic-typography/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Evidence-bound exact typography

## Purpose

Render exact dates, names, quotations, and quantities in authored graphics bound to verified claims.

## Selection cues

- exact_fact
- evidence_overlay
- readable_typography

## Directing instructions

- Copy the verified literal exactly and record its claim ID.
- Hold the resolved factual state long enough to read and verify.

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
  "id": "typography.exact_fact_overlay",
  "name": "Evidence-bound exact typography",
  "description": "Render exact dates, names, quotations, and quantities in authored graphics bound to verified claims.",
  "category": "typography",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 100,
  "phases": [
    "visual_plan",
    "animatic",
    "compose",
    "qc"
  ],
  "intents": [
    "exact_fact",
    "evidence_overlay",
    "readable_typography"
  ],
  "tags": [
    "date",
    "statistic",
    "quotation",
    "claim_id"
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
    "Copy the verified literal exactly and record its claim ID.",
    "Hold the resolved factual state long enough to read and verify."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/kinetic-typography|kinetic-typography]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
