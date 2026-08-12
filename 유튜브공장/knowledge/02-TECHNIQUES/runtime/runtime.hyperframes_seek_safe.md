---
card_id: runtime.hyperframes_seek_safe
type: visual-technique
title: Seek-safe authored motion
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: runtime.hyperframes_seek_safe
category: runtime
selectable: true
priority: 95
phases:
- animatic
- compose
- qc
intents:
- seek_safe_motion
- exact_timing
- hyperframes
tags:
- gsap
- deterministic
- motion_graphics
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
source_path: .agents/skills/hyperframes-core/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Seek-safe authored motion

## Purpose

Use a single deterministic paused timeline for exact motion graphics and virtual-camera treatments.

## Selection cues

- seek_safe_motion
- exact_timing
- hyperframes

## Directing instructions

- Keep all render-critical state a pure function of timeline time.
- Verify snapshots and final MP4 frames, not only lint output.

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
- HYPERFRAMES

## Source and provenance

```json
{
  "type": "local_skill",
  "label": "HyperFrames Core",
  "license": "Apache-2.0",
  "path": ".agents/skills/hyperframes-core/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "runtime.hyperframes_seek_safe",
  "name": "Seek-safe authored motion",
  "description": "Use a single deterministic paused timeline for exact motion graphics and virtual-camera treatments.",
  "category": "runtime",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 95,
  "phases": [
    "animatic",
    "compose",
    "qc"
  ],
  "intents": [
    "seek_safe_motion",
    "exact_timing",
    "hyperframes"
  ],
  "tags": [
    "gsap",
    "deterministic",
    "motion_graphics"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "HYPERFRAMES"
  ],
  "source": {
    "type": "local_skill",
    "label": "HyperFrames Core",
    "license": "Apache-2.0",
    "path": ".agents/skills/hyperframes-core/SKILL.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Keep all render-critical state a pure function of timeline time.",
    "Verify snapshots and final MP4 frames, not only lint output."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/hyperframes-core|hyperframes-core]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
