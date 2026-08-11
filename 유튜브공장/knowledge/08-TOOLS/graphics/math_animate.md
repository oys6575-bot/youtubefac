---
card_id: tool.math_animate
type: tool
title: math_animate
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: math_animate
capability: graphics
provider: manim
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# math_animate

## Capability

graphics

## Factory use

Provider: `manim`  
Runtime: `local`

## Dependencies

- cmd:manim

## Canonical record

```json
{
  "name": "math_animate",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "graphics",
  "provider": "manim",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [
    "cmd:manim"
  ],
  "agent_skills": [
    "manimce-best-practices",
    "manim-composer"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/optional/manimce-best-practices|manimce-best-practices]]
- [[07-SKILLS/optional/manim-composer|manim-composer]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
