---
card_id: tool.face_enhance
type: tool
title: face_enhance
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: face_enhance
capability: enhancement
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# face_enhance

## Capability

enhancement

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg

## Canonical record

```json
{
  "name": "face_enhance",
  "version": "0.1.0",
  "tier": "core",
  "capability": "enhancement",
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
