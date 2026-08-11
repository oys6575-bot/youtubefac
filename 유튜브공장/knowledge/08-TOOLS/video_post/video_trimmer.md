---
card_id: tool.video_trimmer
type: tool
title: video_trimmer
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: video_trimmer
capability: video_post
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# video_trimmer

## Capability

video_post

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg

## Canonical record

```json
{
  "name": "video_trimmer",
  "version": "0.1.0",
  "tier": "core",
  "capability": "video_post",
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
