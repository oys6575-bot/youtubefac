---
card_id: tool.flux_image
type: tool
title: flux_image
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: flux_image
capability: image_generation
provider: flux
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# flux_image

## Capability

image_generation

## Factory use

Provider: `flux`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "flux_image",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "image_generation",
  "provider": "flux",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "beta",
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
