---
card_id: library.directorskills.film_language
type: visual-technique
title: DirectorSkills film-language collection
status: REFERENCE_ONLY
knowledge_schema: '1.0'
generated: true
technique_id: library.directorskills.film_language
category: library
selectable: false
priority: 30
phases:
- research
- visual_plan
intents:
- film_language_library
- master_shots
- scene_transitions
tags:
- director
- cinematography
- source_library
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: ''
canonical_source: config/visual-technique-registry.yaml
---

# DirectorSkills film-language collection

## Purpose

Index of broad directing, master-shot, transition, color, and sound references for later item-level review.

## Selection cues

- film_language_library
- master_shots
- scene_transitions

## Directing instructions

- Use as a discovery index only until an individual module is reviewed.

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
  "label": "DirectorSkills",
  "license": "MIT_WITH_CONTENT_REVIEW",
  "manifest_id": "github.directorskills"
}
```

## Canonical record

```json
{
  "id": "library.directorskills.film_language",
  "name": "DirectorSkills film-language collection",
  "description": "Index of broad directing, master-shot, transition, color, and sound references for later item-level review.",
  "category": "library",
  "status": "REFERENCE_ONLY",
  "selectable": false,
  "priority": 30,
  "phases": [
    "research",
    "visual_plan"
  ],
  "intents": [
    "film_language_library",
    "master_shots",
    "scene_transitions"
  ],
  "tags": [
    "director",
    "cinematography",
    "source_library"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "external_repository",
    "label": "DirectorSkills",
    "license": "MIT_WITH_CONTENT_REVIEW",
    "manifest_id": "github.directorskills"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": true,
    "requires_network": true,
    "note": "Review every selected module for quotation and derivation risk before vendoring."
  },
  "directives": [
    "Use as a discovery index only until an individual module is reviewed."
  ]
}
```

## Related knowledge

- [[06-SOURCES/github/github.directorskills|github.directorskills]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
