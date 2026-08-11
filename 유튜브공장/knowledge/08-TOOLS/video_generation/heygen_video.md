---
card_id: tool.heygen_video
type: tool
title: heygen_video
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: heygen_video
capability: video_generation
provider: heygen
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# heygen_video

## Capability

video_generation

## Factory use

Provider: `heygen`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "heygen_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "heygen",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "ai-video-gen",
    "create-video"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]
- [[07-SKILLS/disabled-by-default/create-video|create-video]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
