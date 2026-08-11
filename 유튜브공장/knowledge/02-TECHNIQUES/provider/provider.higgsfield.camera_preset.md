---
card_id: provider.higgsfield.camera_preset
type: visual-technique
title: Higgsfield-specific camera vocabulary
status: ON_DEMAND
knowledge_schema: '1.0'
generated: true
technique_id: provider.higgsfield.camera_preset
category: provider
selectable: true
priority: 60
phases:
- production
intents:
- camera_motion
- provider_prompting
- higgsfield_preset
tags:
- higgsfield
- provider_specific
- manual_ui
provider_scopes:
- HIGGSFIELD_MANUAL
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# Higgsfield-specific camera vocabulary

## Purpose

Preserve unofficial Higgsfield camera-preset terminology for a future explicitly chosen Higgsfield manual route.

## Selection cues

- camera_motion
- provider_prompting
- higgsfield_preset

## Directing instructions

- Never use these preset names in TopView, Seedance, or local LTX instructions.
- Recheck the live provider before constructing a job packet.

## Constraints and failure modes

- Status: `ON_DEMAND`
- Selectable: `true`
- Human opt-in: `true`
- License review: `false`
- Network required: `true`

## Route and runtime use

Providers:
- HIGGSFIELD_MANUAL

Runtimes:
- ANY

## Source and provenance

```json
{
  "type": "external_repository",
  "label": "Higgsfield AI Prompt Skill",
  "license": "MIT",
  "manifest_id": "github.higgsfield_prompt_skill"
}
```

## Canonical record

```json
{
  "id": "provider.higgsfield.camera_preset",
  "name": "Higgsfield-specific camera vocabulary",
  "description": "Preserve unofficial Higgsfield camera-preset terminology for a future explicitly chosen Higgsfield manual route.",
  "category": "provider",
  "status": "ON_DEMAND",
  "selectable": true,
  "priority": 60,
  "phases": [
    "production"
  ],
  "intents": [
    "camera_motion",
    "provider_prompting",
    "higgsfield_preset"
  ],
  "tags": [
    "higgsfield",
    "provider_specific",
    "manual_ui"
  ],
  "provider_scopes": [
    "HIGGSFIELD_MANUAL"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "external_repository",
    "label": "Higgsfield AI Prompt Skill",
    "license": "MIT",
    "manifest_id": "github.higgsfield_prompt_skill"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": false,
    "requires_network": true,
    "note": "Verify terminology against the current provider UI before use."
  },
  "directives": [
    "Never use these preset names in TopView, Seedance, or local LTX instructions.",
    "Recheck the live provider before constructing a job packet."
  ]
}
```

## Related knowledge

- [[06-SOURCES/github/github.higgsfield_prompt_skill|github.higgsfield_prompt_skill]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
