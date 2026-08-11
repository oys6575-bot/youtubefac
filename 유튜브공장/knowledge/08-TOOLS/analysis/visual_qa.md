---
card_id: tool.visual_qa
type: tool
title: visual_qa
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: visual_qa
capability: analysis
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# visual_qa

## Capability

analysis

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg
- cmd:ffprobe

## Canonical record

```json
{
  "name": "visual_qa",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
  "provider": "ffmpeg",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [
    "cmd:ffmpeg",
    "cmd:ffprobe"
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
