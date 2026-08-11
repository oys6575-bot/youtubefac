---
card_id: tool.audio_mixer
type: tool
title: audio_mixer
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: audio_mixer
capability: audio_processing
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# audio_mixer

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
  "name": "audio_mixer",
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
    "video-toolkit"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/required/ffmpeg|ffmpeg]]
- [[07-SKILLS/optional/video-toolkit|video-toolkit]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
