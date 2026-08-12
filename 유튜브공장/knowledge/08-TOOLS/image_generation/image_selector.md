---
card_id: tool.image_selector
type: tool
title: image_selector
status: PLANNING_ONLY
knowledge_schema: '1.0'
generated: true
tool_name: image_selector
capability: image_generation
provider: selector
runtime: hybrid
network_required: false
canonical_source: config/tool-inventory.json
---

# image_selector

## Capability

image_generation

## Factory use

Provider: `selector`  
Runtime: `hybrid`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "image_selector",
  "version": "0.2.0",
  "tier": "generate",
  "capability": "image_generation",
  "provider": "selector",
  "runtime": "hybrid",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "flux-best-practices",
    "bfl-api"
  ],
  "network_required": false,
  "factory_status": "PLANNING_ONLY"
}
```

## Related knowledge

- [[07-SKILLS/required/flux-best-practices|flux-best-practices]]
- [[07-SKILLS/disabled-by-default/bfl-api|bfl-api]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
