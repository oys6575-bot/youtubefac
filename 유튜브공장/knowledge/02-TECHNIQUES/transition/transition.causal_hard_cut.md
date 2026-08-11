---
card_id: transition.causal_hard_cut
type: visual-technique
title: Causal hard cut
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: transition.causal_hard_cut
category: transition
selectable: true
priority: 93
phases:
- visual_plan
- animatic
- edit
intents:
- causal_cut
- proof_cut
- disruption
tags:
- hard_cut
- causality
- evidence
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: .agents/skills/beat-sync-editing/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Causal hard cut

## Purpose

Cut without decoration when the next image is the direct consequence, proof, or contradiction of the current statement.

## Selection cues

- causal_cut
- proof_cut
- disruption

## Directing instructions

- Prefer the cut itself when the idea supplies enough force.
- Use a hard cut to change register, reveal proof, or interrupt complacency.

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
  "path": ".agents/skills/beat-sync-editing/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "transition.causal_hard_cut",
  "name": "Causal hard cut",
  "description": "Cut without decoration when the next image is the direct consequence, proof, or contradiction of the current statement.",
  "category": "transition",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 93,
  "phases": [
    "visual_plan",
    "animatic",
    "edit"
  ],
  "intents": [
    "causal_cut",
    "proof_cut",
    "disruption"
  ],
  "tags": [
    "hard_cut",
    "causality",
    "evidence"
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
    "path": ".agents/skills/beat-sync-editing/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Prefer the cut itself when the idea supplies enough force.",
    "Use a hard cut to change register, reveal proof, or interrupt complacency."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/beat-sync-editing|beat-sync-editing]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
