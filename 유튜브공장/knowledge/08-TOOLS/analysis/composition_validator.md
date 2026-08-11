---
card_id: tool.composition_validator
type: tool
title: composition_validator
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: composition_validator
capability: analysis
provider: local
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# composition_validator

## Capability

analysis

## Factory use

Provider: `local`  
Runtime: `local`

## Dependencies

- binary:ffprobe

## Canonical record

```json
{
  "name": "composition_validator",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
  "provider": "local",
  "runtime": "local",
  "captured_status": "available",
  "stability": "production",
  "dependencies": [
    "binary:ffprobe"
  ],
  "agent_skills": [],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
