---
card_id: tool.video_analyzer
type: tool
title: video_analyzer
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: video_analyzer
capability: analysis
provider: multi
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# video_analyzer

## Capability

analysis

## Factory use

Provider: `multi`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg

## Canonical record

```json
{
  "name": "video_analyzer",
  "version": "0.1.0",
  "tier": "analyze",
  "capability": "analysis",
  "provider": "multi",
  "runtime": "local",
  "captured_status": "available",
  "stability": "beta",
  "dependencies": [
    "cmd:ffmpeg"
  ],
  "agent_skills": [
    "video-understand",
    "ffmpeg"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/required/video-understand|video-understand]]
- [[07-SKILLS/required/ffmpeg|ffmpeg]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
