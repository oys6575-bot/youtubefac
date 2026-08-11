---
card_id: tool.music_gen
type: tool
title: music_gen
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: music_gen
capability: music_generation
provider: elevenlabs
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# music_gen

## Capability

music_generation

## Factory use

Provider: `elevenlabs`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "music_gen",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "music_generation",
  "provider": "elevenlabs",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "music",
    "sound-effects",
    "elevenlabs"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/optional/music|music]]
- [[07-SKILLS/required/sound-effects|sound-effects]]
- [[07-SKILLS/disabled-by-default/elevenlabs|elevenlabs]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
