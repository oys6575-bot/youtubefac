---
card_id: tool.azure_stt
type: tool
title: azure_stt
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: azure_stt
capability: analysis
provider: azure
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# azure_stt

## Capability

analysis

## Factory use

Provider: `azure`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "azure_stt",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
  "provider": "azure",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "azure-speech-to-text"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/azure-speech-to-text|azure-speech-to-text]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
