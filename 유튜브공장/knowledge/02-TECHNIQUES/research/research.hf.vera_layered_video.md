---
card_id: research.hf.vera_layered_video
type: visual-technique
title: Vera layered-video research pointer
status: REFERENCE_ONLY
knowledge_schema: '1.0'
generated: true
technique_id: research.hf.vera_layered_video
category: research
selectable: false
priority: 8
phases:
- research
intents:
- layered_video
- training_dataset
- video_editing_research
tags:
- huggingface
- large_dataset
- metadata_only
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# Vera layered-video research pointer

## Purpose

Large layered-video dataset retained as an architecture and evaluation reference without downloading its payload.

## Selection cues

- layered_video
- training_dataset
- video_editing_research

## Directing instructions

- Retain the revision pointer; do not download the full dataset into the factory.

## Constraints and failure modes

- Status: `REFERENCE_ONLY`
- Selectable: `false`
- Human opt-in: `true`
- License review: `false`
- Network required: `true`

## Route and runtime use

Providers:
- GENERIC

Runtimes:
- ANY

## Source and provenance

```json
{
  "type": "huggingface",
  "label": "Netflix Vera",
  "license": "Apache-2.0",
  "manifest_id": "hf.vera_layered_video"
}
```

## Canonical record

```json
{
  "id": "research.hf.vera_layered_video",
  "name": "Vera layered-video research pointer",
  "description": "Large layered-video dataset retained as an architecture and evaluation reference without downloading its payload.",
  "category": "research",
  "status": "REFERENCE_ONLY",
  "selectable": false,
  "priority": 8,
  "phases": [
    "research"
  ],
  "intents": [
    "layered_video",
    "training_dataset",
    "video_editing_research"
  ],
  "tags": [
    "huggingface",
    "large_dataset",
    "metadata_only"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "huggingface",
    "label": "Netflix Vera",
    "license": "Apache-2.0",
    "manifest_id": "hf.vera_layered_video"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": false,
    "requires_network": true
  },
  "directives": [
    "Retain the revision pointer; do not download the full dataset into the factory."
  ]
}
```

## Related knowledge

- [[06-SOURCES/hugging-face/hf.vera_layered_video|hf.vera_layered_video]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
