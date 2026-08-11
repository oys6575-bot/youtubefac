---
card_id: tool.grok_image
type: tool
title: grok_image
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: grok_image
capability: image_generation
provider: grok
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# grok_image

## Capability

image_generation

## Factory use

Provider: `grok`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "grok_image",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "image_generation",
  "provider": "grok",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "grok-media"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/grok-media|grok-media]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
