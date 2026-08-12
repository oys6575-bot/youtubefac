---
card_id: provider.topview.multi_reference_continuity
type: visual-technique
title: TopView multi-reference continuity
status: ON_DEMAND
knowledge_schema: '1.0'
generated: true
technique_id: provider.topview.multi_reference_continuity
category: provider
selectable: true
priority: 87
phases:
- production
intents:
- multi_reference
- identity_continuity
- provider_prompting
- camera_motion
tags:
- topview
- omni_reference
- manual_ui
provider_scopes:
- TOPVIEW_MANUAL
render_runtimes:
- ANY
source_path: config/topview-capabilities.yaml
canonical_source: config/visual-technique-registry.yaml
---

# TopView multi-reference continuity

## Purpose

Use manual Omni/Multi Reference only for a shot whose identity or environment continuity cannot be carried by one frame.

## Selection cues

- multi_reference
- identity_continuity
- provider_prompting
- camera_motion

## Directing instructions

- Assign one explicit role to each reference and remove redundant references.
- Compare returned candidates in OpenMontage before asset selection.

## Constraints and failure modes

- Status: `ON_DEMAND`
- Selectable: `true`
- Human opt-in: `true`
- License review: `false`
- Network required: `true`

## Route and runtime use

Providers:
- TOPVIEW_MANUAL

Runtimes:
- ANY

## Source and provenance

```json
{
  "type": "project_doc",
  "label": "TopView capability catalog",
  "license": "PROJECT_LOCAL",
  "path": "config/topview-capabilities.yaml"
}
```

## Canonical record

```json
{
  "id": "provider.topview.multi_reference_continuity",
  "name": "TopView multi-reference continuity",
  "description": "Use manual Omni/Multi Reference only for a shot whose identity or environment continuity cannot be carried by one frame.",
  "category": "provider",
  "status": "ON_DEMAND",
  "selectable": true,
  "priority": 87,
  "phases": [
    "production"
  ],
  "intents": [
    "multi_reference",
    "identity_continuity",
    "provider_prompting",
    "camera_motion"
  ],
  "tags": [
    "topview",
    "omni_reference",
    "manual_ui"
  ],
  "provider_scopes": [
    "TOPVIEW_MANUAL"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "project_doc",
    "label": "TopView capability catalog",
    "license": "PROJECT_LOCAL",
    "path": "config/topview-capabilities.yaml"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": false,
    "requires_network": true,
    "note": "Human operates the TopView UI after budget approval."
  },
  "directives": [
    "Assign one explicit role to each reference and remove redundant references.",
    "Compare returned candidates in OpenMontage before asset selection."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
