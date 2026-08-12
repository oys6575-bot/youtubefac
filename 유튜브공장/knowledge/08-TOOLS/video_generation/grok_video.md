---
card_id: tool.grok_video
type: tool
title: grok_video
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: grok_video
capability: video_generation
provider: grok
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# grok_video

## Capability

video_generation

## Factory use

Provider: `grok`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "grok_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "grok",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "grok-media",
    "ai-video-gen"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/grok-media|grok-media]]
- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
