---
card_id: tool.doubao_tts
type: tool
title: doubao_tts
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: doubao_tts
capability: tts
provider: doubao
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# doubao_tts

## Capability

tts

## Factory use

Provider: `doubao`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "doubao_tts",
  "version": "0.1.0",
  "tier": "voice",
  "capability": "tts",
  "provider": "doubao",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "doubao-tts",
    "text-to-speech"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/doubao-tts|doubao-tts]]
- [[07-SKILLS/required/text-to-speech|text-to-speech]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
