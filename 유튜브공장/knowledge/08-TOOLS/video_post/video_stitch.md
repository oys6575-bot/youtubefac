---
card_id: tool.video_stitch
type: tool
title: video_stitch
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: video_stitch
capability: video_post
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# video_stitch

## Capability

video_post

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg
- cmd:ffprobe

## Canonical record

```json
{
  "name": "video_stitch",
  "version": "0.1.0",
  "tier": "core",
  "capability": "video_post",
  "provider": "ffmpeg",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [
    "cmd:ffmpeg",
    "cmd:ffprobe"
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
