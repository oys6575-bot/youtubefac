---
card_id: research.hf.av_skills
type: visual-technique
title: AV-Skills non-commercial research pointer
status: BLOCKED
knowledge_schema: '1.0'
generated: true
technique_id: research.hf.av_skills
category: research
selectable: false
priority: 5
phases:
- research
intents:
- noncommercial_research
- training_dataset
- camera_motion
tags:
- huggingface
- audiovisual
- blocked
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# AV-Skills non-commercial research pointer

## Purpose

Audio-visual skill research retained only as a metadata pointer because its terms are non-commercial.

## Selection cues

- noncommercial_research
- training_dataset
- camera_motion

## Directing instructions

- Never activate in the normal commercial production path.

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
  "label": "NVIDIA AV-Skills",
  "license": "OTHER-NONCOMMERCIAL",
  "manifest_id": "hf.av_skills"
}
```

## Canonical record

```json
{
  "id": "research.hf.av_skills",
  "name": "AV-Skills non-commercial research pointer",
  "description": "Audio-visual skill research retained only as a metadata pointer because its terms are non-commercial.",
  "category": "research",
  "status": "BLOCKED",
  "selectable": false,
  "priority": 5,
  "phases": [
    "research"
  ],
  "intents": [
    "noncommercial_research",
    "training_dataset",
    "camera_motion"
  ],
  "tags": [
    "huggingface",
    "audiovisual",
    "blocked"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "huggingface",
    "label": "NVIDIA AV-Skills",
    "license": "OTHER-NONCOMMERCIAL",
    "manifest_id": "hf.av_skills"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": true,
    "requires_network": true
  },
  "directives": [
    "Never activate in the normal commercial production path."
  ]
}
```

## Related knowledge

- [[06-SOURCES/hugging-face/hf.av_skills|hf.av_skills]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
