---
card_id: research.hf.camera_motion_classifier
type: visual-technique
title: Camera-motion classifier research pointer
status: BLOCKED
knowledge_schema: '1.0'
generated: true
technique_id: research.hf.camera_motion_classifier
category: research
selectable: false
priority: 10
phases:
- research
- qc
intents:
- camera_motion
- motion_classifier
- training_dataset
tags:
- huggingface
- model
- license_unknown
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# Camera-motion classifier research pointer

## Purpose

Potential classifier for auditing motion categories, blocked until license terms are declared.

## Selection cues

- camera_motion
- motion_classifier
- training_dataset

## Directing instructions

- Do not download or execute until the license is resolved.

## Constraints and failure modes

- Status: `BLOCKED`
- Selectable: `false`
- Human opt-in: `true`
- License review: `true`
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
  "label": "Kandinsky VideoMAE camera motion",
  "license": "UNDECLARED",
  "manifest_id": "hf.camera_motion_classifier"
}
```

## Canonical record

```json
{
  "id": "research.hf.camera_motion_classifier",
  "name": "Camera-motion classifier research pointer",
  "description": "Potential classifier for auditing motion categories, blocked until license terms are declared.",
  "category": "research",
  "status": "BLOCKED",
  "selectable": false,
  "priority": 10,
  "phases": [
    "research",
    "qc"
  ],
  "intents": [
    "camera_motion",
    "motion_classifier",
    "training_dataset"
  ],
  "tags": [
    "huggingface",
    "model",
    "license_unknown"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "huggingface",
    "label": "Kandinsky VideoMAE camera motion",
    "license": "UNDECLARED",
    "manifest_id": "hf.camera_motion_classifier"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": true,
    "requires_network": true
  },
  "directives": [
    "Do not download or execute until the license is resolved."
  ]
}
```

## Related knowledge

- [[06-SOURCES/hugging-face/hf.camera_motion_classifier|hf.camera_motion_classifier]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
