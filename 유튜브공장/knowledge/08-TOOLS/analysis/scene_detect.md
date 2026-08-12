---
card_id: tool.scene_detect
type: tool
title: scene_detect
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: scene_detect
capability: analysis
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# scene_detect

## Capability

analysis

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg

## Canonical record

```json
{
  "name": "scene_detect",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
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
