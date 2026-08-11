---
card_id: tool.auto_reframe
type: tool
title: auto_reframe
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: auto_reframe
capability: video_post
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# auto_reframe

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
  "name": "auto_reframe",
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
    "ffmpeg"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/required/ffmpeg|ffmpeg]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
