---
card_id: tool.audio_enhance
type: tool
title: audio_enhance
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: audio_enhance
capability: audio_processing
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# audio_enhance

## Capability

audio_processing

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg

## Canonical record

```json
{
  "name": "audio_enhance",
  "version": "0.1.0",
  "tier": "core",
  "capability": "audio_processing",
  "provider": "ffmpeg",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [
    "cmd:ffmpeg"
  ],
  "agent_skills": [
    "ffmpeg",
    "elevenlabs"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/required/ffmpeg|ffmpeg]]
- [[07-SKILLS/disabled-by-default/elevenlabs|elevenlabs]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
