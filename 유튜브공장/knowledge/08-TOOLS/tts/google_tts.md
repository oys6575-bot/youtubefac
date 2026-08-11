---
card_id: tool.google_tts
type: tool
title: google_tts
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: google_tts
capability: tts
provider: google_tts
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# google_tts

## Capability

tts

## Factory use

Provider: `google_tts`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "google_tts",
  "version": "0.1.0",
  "tier": "voice",
  "capability": "tts",
  "provider": "google_tts",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "text-to-speech"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/required/text-to-speech|text-to-speech]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
