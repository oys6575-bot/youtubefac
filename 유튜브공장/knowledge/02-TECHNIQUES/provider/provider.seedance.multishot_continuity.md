---
card_id: provider.seedance.multishot_continuity
type: visual-technique
title: Seedance-specific multi-shot continuity
status: ON_DEMAND
knowledge_schema: '1.0'
generated: true
technique_id: provider.seedance.multishot_continuity
category: provider
selectable: true
priority: 62
phases:
- production
intents:
- multi_reference
- first_last_frame
- provider_prompting
- multishot
tags:
- seedance
- provider_specific
- continuity
provider_scopes:
- SEEDANCE_MANUAL
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# Seedance-specific multi-shot continuity

## Purpose

Preserve Seedance-oriented multi-shot and frame-reference guidance for a future explicitly selected Seedance route.

## Selection cues

- multi_reference
- first_last_frame
- provider_prompting
- multishot

## Directing instructions

- Never present Seedance-specific syntax as a generic TopView instruction.
- Treat multi-shot output as candidates requiring continuity review.

## Constraints and failure modes

- Status: `ON_DEMAND`
- Selectable: `true`
- Human opt-in: `true`
- License review: `false`
- Network required: `true`

## Route and runtime use

Providers:
- SEEDANCE_MANUAL

Runtimes:
- ANY

## Source and provenance

```json
{
  "type": "external_repository",
  "label": "Seedance 2.0 skill",
  "license": "MIT",
  "manifest_id": "github.seedance_prompt_skill"
}
```

## Canonical record

```json
{
  "id": "provider.seedance.multishot_continuity",
  "name": "Seedance-specific multi-shot continuity",
  "description": "Preserve Seedance-oriented multi-shot and frame-reference guidance for a future explicitly selected Seedance route.",
  "category": "provider",
  "status": "ON_DEMAND",
  "selectable": true,
  "priority": 62,
  "phases": [
    "production"
  ],
  "intents": [
    "multi_reference",
    "first_last_frame",
    "provider_prompting",
    "multishot"
  ],
  "tags": [
    "seedance",
    "provider_specific",
    "continuity"
  ],
  "provider_scopes": [
    "SEEDANCE_MANUAL"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "external_repository",
    "label": "Seedance 2.0 skill",
    "license": "MIT",
    "manifest_id": "github.seedance_prompt_skill"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": false,
    "requires_network": true,
    "note": "Verify current model labels and limitations before use."
  },
  "directives": [
    "Never present Seedance-specific syntax as a generic TopView instruction.",
    "Treat multi-shot output as candidates requiring continuity review."
  ]
}
```

## Related knowledge

- [[06-SOURCES/github/github.seedance_prompt_skill|github.seedance_prompt_skill]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
