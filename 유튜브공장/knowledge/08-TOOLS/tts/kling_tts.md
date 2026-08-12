---
card_id: tool.kling_tts
type: tool
title: kling_tts
status: DISABLED_BY_DEFAULT
knowledge_schema: '1.0'
generated: true
tool_name: kling_tts
capability: tts
provider: kling_official
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# kling_tts

## Capability

tts

## Factory use

Provider: `kling_official`  
Runtime: `api`

## Dependencies

- env:KLING_API_KEY

## Canonical record

```json
{
  "name": "kling_tts",
  "version": "0.1.0",
  "tier": "voice",
  "capability": "tts",
  "provider": "kling_official",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "env:KLING_API_KEY"
  ],
  "agent_skills": [
    "kling-official",
    "text-to-speech"
  ],
  "network_required": true,
  "factory_status": "DISABLED_BY_DEFAULT"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/kling-official|kling-official]]
- [[07-SKILLS/required/text-to-speech|text-to-speech]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
