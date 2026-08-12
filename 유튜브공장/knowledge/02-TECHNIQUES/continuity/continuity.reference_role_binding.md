---
card_id: continuity.reference_role_binding
type: visual-technique
title: Reference-role binding
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: continuity.reference_role_binding
category: continuity
selectable: true
priority: 92
phases:
- visual_plan
- production
intents:
- reference_role
- multi_reference
- identity_continuity
tags:
- reference
- identity
- environment
- object
- style
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: knowledge/10-RESEARCH/cinematic-direction/Image-Reference-Asset-Direction.md
canonical_source: config/visual-technique-registry.yaml
---

# Reference-role binding

## Purpose

Assign each reference one explicit control role and state what it must preserve and what it must not transfer.

## Selection cues

- reference_role
- multi_reference
- identity_continuity

## Directing instructions

- Bind each file to one primary role such as subject, environment, object, composition, lighting, or style.
- List both the attributes controlled by the reference and the attributes that must not leak from it.

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
  "label": "Image reference asset synthesis",
  "license": "PROJECT_LOCAL",
  "path": "knowledge/10-RESEARCH/cinematic-direction/Image-Reference-Asset-Direction.md"
}
```

## Canonical record

```json
{
  "id": "continuity.reference_role_binding",
  "name": "Reference-role binding",
  "description": "Assign each reference one explicit control role and state what it must preserve and what it must not transfer.",
  "category": "continuity",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 92,
  "phases": [
    "visual_plan",
    "production"
  ],
  "intents": [
    "reference_role",
    "multi_reference",
    "identity_continuity"
  ],
  "tags": [
    "reference",
    "identity",
    "environment",
    "object",
    "style"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "project_doc",
    "label": "Image reference asset synthesis",
    "license": "PROJECT_LOCAL",
    "path": "knowledge/10-RESEARCH/cinematic-direction/Image-Reference-Asset-Direction.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Bind each file to one primary role such as subject, environment, object, composition, lighting, or style.",
    "List both the attributes controlled by the reference and the attributes that must not leak from it."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
