---
card_id: tool.tts_selector
type: tool
title: tts_selector
status: PLANNING_ONLY
knowledge_schema: '1.0'
generated: true
tool_name: tts_selector
capability: tts
provider: selector
runtime: hybrid
network_required: false
canonical_source: config/tool-inventory.json
---

# tts_selector

## Capability

tts

## Factory use

Provider: `selector`  
Runtime: `hybrid`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "tts_selector",
  "version": "0.2.0",
  "tier": "voice",
  "capability": "tts",
  "provider": "selector",
  "runtime": "hybrid",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "text-to-speech",
    "elevenlabs",
    "openai-docs"
  ],
  "network_required": false,
  "factory_status": "PLANNING_ONLY"
}
```

## Related knowledge

- [[07-SKILLS/required/text-to-speech|text-to-speech]]
- [[07-SKILLS/disabled-by-default/elevenlabs|elevenlabs]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
