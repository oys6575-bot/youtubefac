---
card_id: camera.static_evidence_hold
type: visual-technique
title: Static evidence hold
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: camera.static_evidence_hold
category: camera
selectable: true
priority: 94
phases:
- visual_plan
- animatic
- edit
intents:
- evidence_hold
- exact_fact
- document_reading
tags:
- static
- evidence
- readability
- proof
provider_scopes:
- GENERIC
render_runtimes:
- ANY
source_path: config/visual-grammars/HERITAGE_FORGE.yaml
canonical_source: config/visual-technique-registry.yaml
---

# Static evidence hold

## Purpose

Stop camera motion when movement would compete with verification of a document, artifact, date, or measurement.

## Selection cues

- evidence_hold
- exact_fact
- document_reading

## Directing instructions

- Hold the frame for the actual reading task, not for a generic cinematic pause.
- Cut directly into evidence when narration makes a verifiable claim.

## Constraints and failure modes

- Status: `ACTIVE`
- Selectable: `true`
- Human opt-in: `false`
- License review: `false`
- Network required: `false`

## Route and runtime use

Providers:
- GENERIC

Runtimes:
- ANY

## Source and provenance

```json
{
  "type": "project_doc",
  "label": "Heritage Forge grammar",
  "license": "PROJECT_LOCAL",
  "path": "config/visual-grammars/HERITAGE_FORGE.yaml"
}
```

## Canonical record

```json
{
  "id": "camera.static_evidence_hold",
  "name": "Static evidence hold",
  "description": "Stop camera motion when movement would compete with verification of a document, artifact, date, or measurement.",
  "category": "camera",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 94,
  "phases": [
    "visual_plan",
    "animatic",
    "edit"
  ],
  "intents": [
    "evidence_hold",
    "exact_fact",
    "document_reading"
  ],
  "tags": [
    "static",
    "evidence",
    "readability",
    "proof"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "project_doc",
    "label": "Heritage Forge grammar",
    "license": "PROJECT_LOCAL",
    "path": "config/visual-grammars/HERITAGE_FORGE.yaml"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Hold the frame for the actual reading task, not for a generic cinematic pause.",
    "Cut directly into evidence when narration makes a verifiable claim."
  ]
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
