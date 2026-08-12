---
card_id: tool.piper_tts
type: tool
title: piper_tts
status: LOCAL_SETUP_REQUIRED
knowledge_schema: '1.0'
generated: true
tool_name: piper_tts
capability: tts
provider: piper
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# piper_tts

## Capability

tts

## Factory use

Provider: `piper`  
Runtime: `local`

## Dependencies

- cmd:piper

## Canonical record

```json
{
  "name": "piper_tts",
  "version": "0.1.0",
  "tier": "voice",
  "capability": "tts",
  "provider": "piper",
  "runtime": "local",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "cmd:piper"
  ],
  "agent_skills": [
    "text-to-speech"
  ],
  "network_required": false,
  "factory_status": "LOCAL_SETUP_REQUIRED"
}
```

## Related knowledge

- [[07-SKILLS/required/text-to-speech|text-to-speech]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
