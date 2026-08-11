---
card_id: tool.google_music
type: tool
title: google_music
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: google_music
capability: music_generation
provider: google
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# google_music

## Capability

music_generation

## Factory use

Provider: `google`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "google_music",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "music_generation",
  "provider": "google",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "lyria"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/lyria|lyria]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
