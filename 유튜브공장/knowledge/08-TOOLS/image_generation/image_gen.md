---
card_id: tool.image_gen
type: tool
title: image_gen
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: image_gen
capability: image_generation
provider: multi
runtime: hybrid
network_required: true
canonical_source: config/tool-inventory.json
---

# image_gen

## Capability

image_generation

## Factory use

Provider: `multi`  
Runtime: `hybrid`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "image_gen",
  "version": "0.1.0",
  "tier": "core",
  "capability": "image_generation",
  "provider": "multi",
  "runtime": "hybrid",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "flux-best-practices",
    "bfl-api"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/required/flux-best-practices|flux-best-practices]]
- [[07-SKILLS/disabled-by-default/bfl-api|bfl-api]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
