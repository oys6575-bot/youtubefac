---
card_id: tool.openai_image
type: tool
title: openai_image
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: openai_image
capability: image_generation
provider: openai
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# openai_image

## Capability

image_generation

## Factory use

Provider: `openai`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "openai_image",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "image_generation",
  "provider": "openai",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "flux-best-practices"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/required/flux-best-practices|flux-best-practices]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
