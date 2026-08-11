---
card_id: tool.green_screen_composite
type: tool
title: green_screen_composite
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: green_screen_composite
capability: video_post
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# green_screen_composite

## Capability

video_post

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg
- python:numpy
- python:PIL

## Canonical record

```json
{
  "name": "green_screen_composite",
  "version": "0.1.0",
  "tier": "core",
  "capability": "video_post",
  "provider": "ffmpeg",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [
    "cmd:ffmpeg",
    "python:numpy",
    "python:PIL"
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
