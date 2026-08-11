---
card_id: runtime.remotion_scene_reuse
type: visual-technique
title: Reuse a verified Remotion scene pattern
status: ON_DEMAND
knowledge_schema: '1.0'
generated: true
technique_id: runtime.remotion_scene_reuse
category: runtime
selectable: true
priority: 74
phases:
- compose
intents:
- remotion_scene
- react_composition
- reusable_scene
tags:
- remotion
- component
- scene_library
provider_scopes:
- GENERIC
render_runtimes:
- REMOTION
source_path: .agents/skills/remotion-bits/SKILL.md
canonical_source: config/visual-technique-registry.yaml
---

# Reuse a verified Remotion scene pattern

## Purpose

Adapt the closest tested React scene when the runtime and shot design are already locked to Remotion.

## Selection cues

- remotion_scene
- react_composition
- reusable_scene

## Directing instructions

- Adapt a close pattern rather than assembling unrelated templates.
- Verify component wiring, props, Root registration, type check, and render.

## Constraints and failure modes

- Status: `ON_DEMAND`
- Selectable: `true`
- Human opt-in: `true`
- License review: `true`
- Network required: `false`

## Route and runtime use

Providers:
- GENERIC

Runtimes:
- REMOTION

## Source and provenance

```json
{
  "type": "local_skill",
  "label": "Remotion Bits",
  "license": "UNVERIFIED_UPSTREAM",
  "path": ".agents/skills/remotion-bits/SKILL.md"
}
```

## Canonical record

```json
{
  "id": "runtime.remotion_scene_reuse",
  "name": "Reuse a verified Remotion scene pattern",
  "description": "Adapt the closest tested React scene when the runtime and shot design are already locked to Remotion.",
  "category": "runtime",
  "status": "ON_DEMAND",
  "selectable": true,
  "priority": 74,
  "phases": [
    "compose"
  ],
  "intents": [
    "remotion_scene",
    "react_composition",
    "reusable_scene"
  ],
  "tags": [
    "remotion",
    "component",
    "scene_library"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "REMOTION"
  ],
  "source": {
    "type": "local_skill",
    "label": "Remotion Bits",
    "license": "UNVERIFIED_UPSTREAM",
    "path": ".agents/skills/remotion-bits/SKILL.md"
  },
  "activation": {
    "default_allowed": false,
    "requires_human_opt_in": true,
    "requires_license_review": true,
    "requires_network": false,
    "note": "Recheck the upstream example license before copying code."
  },
  "directives": [
    "Adapt a close pattern rather than assembling unrelated templates.",
    "Verify component wiring, props, Root registration, type check, and render."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/remotion-bits|remotion-bits]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
