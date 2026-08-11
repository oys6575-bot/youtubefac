---
card_id: provider.topview.first_last_frame_bridge
type: visual-technique
title: TopView first/last-frame bridge
status: ON_DEMAND
knowledge_schema: '1.0'
generated: true
technique_id: provider.topview.first_last_frame_bridge
category: provider
selectable: true
priority: 88
phases:
- production
intents:
- first_last_frame
- photo_to_motion
- camera_motion
- provider_prompting
tags:
- topview
- frame_bridge
- manual_ui
provider_scopes:
- TOPVIEW_MANUAL
render_runtimes:
- ANY
source_path: config/topview-capabilities.yaml
canonical_source: config/visual-technique-registry.yaml
---

# TopView first/last-frame bridge

## Purpose

Manually request a controlled transformation between approved start and end frames in TopView.

## Selection cues

- first_last_frame
- photo_to_motion
- camera_motion
- provider_prompting

## Directing instructions

- Freeze both reference frames and record their hashes in the manual job packet.
- Record the exact visible model label and cost before the user submits.

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
  "id": "provider.topview.first_last_frame_bridge",
  "name": "TopView first/last-frame bridge",
  "description": "Manually request a controlled transformation between approved start and end frames in TopView.",
  "category": "provider",
  "status": "ON_DEMAND",
  "selectable": true,
  "priority": 88,
  "phases": [
    "production"
  ],
  "intents": [
    "first_last_frame",
    "photo_to_motion",
    "camera_motion",
    "provider_prompting"
  ],
  "tags": [
    "topview",
    "frame_bridge",
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
    "Freeze both reference frames and record their hashes in the manual job packet.",
    "Record the exact visible model label and cost before the user submits."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
