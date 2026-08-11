---
card_id: tool.minimax_video
type: tool
title: minimax_video
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: minimax_video
capability: video_generation
provider: minimax
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# minimax_video

## Capability

video_generation

## Factory use

Provider: `minimax`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "minimax_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "minimax",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "ai-video-gen"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
