---
card_id: research.hf.shotplan
type: visual-technique
title: ShotPlan restricted research pointer
status: BLOCKED
knowledge_schema: '1.0'
generated: true
technique_id: research.hf.shotplan
category: research
selectable: false
priority: 5
phases:
- research
intents:
- shot_planning
- noncommercial_research
- training_dataset
tags:
- huggingface
- license_review
- blocked
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# ShotPlan restricted research pointer

## Purpose

Shot-planning research retained only for later legal and usefulness review.

## Selection cues

- shot_planning
- noncommercial_research
- training_dataset

## Directing instructions

- Do not activate until legal terms and concrete value are reviewed.

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
  "label": "ShotPlan",
  "license": "OTHER",
  "manifest_id": "hf.shotplan"
}
```

## Canonical record

```json
{
  "id": "research.hf.shotplan",
  "name": "ShotPlan restricted research pointer",
  "description": "Shot-planning research retained only for later legal and usefulness review.",
  "category": "research",
  "status": "BLOCKED",
  "selectable": false,
  "priority": 5,
  "phases": [
    "research"
  ],
  "intents": [
    "shot_planning",
    "noncommercial_research",
    "training_dataset"
  ],
  "tags": [
    "huggingface",
    "license_review",
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
    "label": "ShotPlan",
    "license": "OTHER",
    "manifest_id": "hf.shotplan"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": true,
    "requires_network": true
  },
  "directives": [
    "Do not activate until legal terms and concrete value are reviewed."
  ]
}
```

## Related knowledge

- [[06-SOURCES/hugging-face/hf.shotplan|hf.shotplan]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
