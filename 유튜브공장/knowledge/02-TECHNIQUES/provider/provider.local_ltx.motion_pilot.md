---
card_id: provider.local_ltx.motion_pilot
type: visual-technique
title: Local LTX motion pilot
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: provider.local_ltx.motion_pilot
category: provider
selectable: true
priority: 80
phases:
- production
intents:
- local_motion_pilot
- image_to_video
- low_cost_test
tags:
- ltx
- comfyui
- local
- mps
provider_scopes:
- LOCAL_LTX
render_runtimes:
- ANY
source_path: .agents/skills/ltx2/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Local LTX motion pilot

## Purpose

Test low-cost non-critical motion locally before considering an external generation pass.

## Selection cues

- local_motion_pilot
- image_to_video
- low_cost_test

## Directing instructions

- Start with a short fixed-seed draft and inspect actual frames for MPS corruption.
- Never promote a generated clip from candidate to selected without the asset gate.

## Constraints and failure modes

- Status: `ACTIVE`
- Selectable: `true`
- Human opt-in: `false`
- License review: `false`
- Network required: `false`

## Route and runtime use

Providers:
- LOCAL_LTX

Runtimes:
- ANY

## Source and provenance

```json
{
  "type": "local_skill",
  "label": "LTX2",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/ltx2/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "provider.local_ltx.motion_pilot",
  "name": "Local LTX motion pilot",
  "description": "Test low-cost non-critical motion locally before considering an external generation pass.",
  "category": "provider",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 80,
  "phases": [
    "production"
  ],
  "intents": [
    "local_motion_pilot",
    "image_to_video",
    "low_cost_test"
  ],
  "tags": [
    "ltx",
    "comfyui",
    "local",
    "mps"
  ],
  "provider_scopes": [
    "LOCAL_LTX"
  ],
  "render_runtimes": [
    "ANY"
  ],
  "source": {
    "type": "local_skill",
    "label": "LTX2",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/ltx2/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Start with a short fixed-seed draft and inspect actual frames for MPS corruption.",
    "Never promote a generated clip from candidate to selected without the asset gate."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/ltx2|ltx2]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
