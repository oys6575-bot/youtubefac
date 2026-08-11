---
card_id: research.hf.film_eval
type: visual-technique
title: FilmEval non-commercial research
status: BLOCKED
knowledge_schema: '1.0'
generated: true
technique_id: research.hf.film_eval
category: research
selectable: false
priority: 5
phases:
- research
- qc
intents:
- noncommercial_research
- film_evaluation
- training_dataset
tags:
- huggingface
- cc_by_nc
- blocked
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# FilmEval non-commercial research

## Purpose

Non-commercial film-evaluation dataset retained only as a pointer.

## Selection cues

- noncommercial_research
- film_evaluation
- training_dataset

## Directing instructions

- Never use in the normal commercial production path.

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
  "label": "FilmEval",
  "license": "CC-BY-NC-4.0",
  "manifest_id": "hf.film_eval"
}
```

## Canonical record

```json
{
  "id": "research.hf.film_eval",
  "name": "FilmEval non-commercial research",
  "description": "Non-commercial film-evaluation dataset retained only as a pointer.",
  "category": "research",
  "status": "BLOCKED",
  "selectable": false,
  "priority": 5,
  "phases": [
    "research",
    "qc"
  ],
  "intents": [
    "noncommercial_research",
    "film_evaluation",
    "training_dataset"
  ],
  "tags": [
    "huggingface",
    "cc_by_nc",
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
    "label": "FilmEval",
    "license": "CC-BY-NC-4.0",
    "manifest_id": "hf.film_eval"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": true,
    "requires_network": true
  },
  "directives": [
    "Never use in the normal commercial production path."
  ]
}
```

## Related knowledge

- [[06-SOURCES/hugging-face/hf.film_eval|hf.film_eval]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
