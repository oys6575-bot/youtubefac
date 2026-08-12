---
card_id: tool.runway_video
type: tool
title: runway_video
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: runway_video
capability: video_generation
provider: runway
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# runway_video

## Capability

video_generation

## Factory use

Provider: `runway`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "runway_video",
  "version": "0.2.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "runway",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "seedance-2-0",
    "ai-video-gen"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/seedance-2-0|seedance-2-0]]
- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
