---
card_id: camera.material_macro_parallax
type: visual-technique
title: Material macro with restrained parallax
status: ACTIVE
knowledge_schema: '1.0'
generated: true
technique_id: camera.material_macro_parallax
category: camera
selectable: true
priority: 97
phases:
- visual_plan
- animatic
- production
- compose
intents:
- material_macro
- photo_to_motion
- tactile_detail
tags:
- macro
- parallax
- still_image
- texture
- craft
provider_scopes:
- GENERIC
render_runtimes:
- HYPERFRAMES
- REMOTION
source_path: .agents/skills/motion-art-direction/references/direction-playbook.md
canonical_source: config/visual-technique-registry.yaml
---

# Material macro with restrained parallax

## Purpose

Turn a still material detail into depth by separating foreground, subject plane, and background motion.

## Selection cues

- material_macro
- photo_to_motion
- tactile_detail

## Directing instructions

- Move planes at different rates and keep the material fact readable.
- Limit a macro to one tactile fact rather than decorative closeness.

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
- REMOTION

## Source and provenance

```json
{
  "type": "local_skill",
  "label": "Motion Art Direction",
  "license": "PROJECT_LOCAL",
  "path": ".agents/skills/motion-art-direction/references/direction-playbook.md"
}
```

## Canonical record

```json
{
  "id": "camera.material_macro_parallax",
  "name": "Material macro with restrained parallax",
  "description": "Turn a still material detail into depth by separating foreground, subject plane, and background motion.",
  "category": "camera",
  "status": "ACTIVE",
  "selectable": true,
  "priority": 97,
  "phases": [
    "visual_plan",
    "animatic",
    "production",
    "compose"
  ],
  "intents": [
    "material_macro",
    "photo_to_motion",
    "tactile_detail"
  ],
  "tags": [
    "macro",
    "parallax",
    "still_image",
    "texture",
    "craft"
  ],
  "provider_scopes": [
    "GENERIC"
  ],
  "render_runtimes": [
    "HYPERFRAMES",
    "REMOTION"
  ],
  "source": {
    "type": "local_skill",
    "label": "Motion Art Direction",
    "license": "PROJECT_LOCAL",
    "path": ".agents/skills/motion-art-direction/references/direction-playbook.md"
  },
  "activation": {
    "default_allowed": true,
    "requires_human_opt_in": false,
    "requires_license_review": false,
    "requires_network": false
  },
  "directives": [
    "Move planes at different rates and keep the material fact readable.",
    "Limit a macro to one tactile fact rather than decorative closeness."
  ]
}
```

## Related knowledge

- [[07-SKILLS/required/motion-art-direction|motion-art-direction]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
