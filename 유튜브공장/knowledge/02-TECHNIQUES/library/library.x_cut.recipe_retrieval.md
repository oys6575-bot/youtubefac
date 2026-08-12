---
card_id: library.x_cut.recipe_retrieval
type: visual-technique
title: X-Cut recipe-retrieval architecture
status: REFERENCE_ONLY
knowledge_schema: '1.0'
generated: true
technique_id: library.x_cut.recipe_retrieval
category: library
selectable: false
priority: 20
phases:
- research
intents:
- recipe_retrieval
- editing_architecture
- long_form_automation
tags:
- architecture
- retrieval
- agpl
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# X-Cut recipe-retrieval architecture

## Purpose

Reference architecture for retrieving style recipes without making X-Cut a production dependency.

## Selection cues

- recipe_retrieval
- editing_architecture
- long_form_automation

## Directing instructions

- Borrow the retrieval boundary, not unverified production behavior.

## Constraints and failure modes

- Status: `REFERENCE_ONLY`
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
  "type": "external_repository",
  "label": "X-Cut",
  "license": "AGPL-3.0",
  "manifest_id": "github.x_cut"
}
```

## Canonical record

```json
{
  "id": "library.x_cut.recipe_retrieval",
  "name": "X-Cut recipe-retrieval architecture",
  "description": "Reference architecture for retrieving style recipes without making X-Cut a production dependency.",
  "category": "library",
  "status": "REFERENCE_ONLY",
  "selectable": false,
  "priority": 20,
  "phases": [
    "research"
  ],
  "intents": [
    "recipe_retrieval",
    "editing_architecture",
    "long_form_automation"
  ],
  "tags": [
    "architecture",
    "retrieval",
    "agpl"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "external_repository",
    "label": "X-Cut",
    "license": "AGPL-3.0",
    "manifest_id": "github.x_cut"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": true,
    "requires_network": true
  },
  "directives": [
    "Borrow the retrieval boundary, not unverified production behavior."
  ]
}
```

## Related knowledge

- [[06-SOURCES/github/github.x_cut|github.x_cut]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
