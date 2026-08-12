---
card_id: tool.kling_official_video
type: tool
title: kling_official_video
status: DISABLED_BY_DEFAULT
knowledge_schema: '1.0'
generated: true
tool_name: kling_official_video
capability: video_generation
provider: kling_official
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# kling_official_video

## Capability

video_generation

## Factory use

Provider: `kling_official`  
Runtime: `api`

## Dependencies

- env:KLING_API_KEY

## Canonical record

```json
{
  "name": "kling_official_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "kling_official",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "env:KLING_API_KEY"
  ],
  "agent_skills": [
    "ai-video-gen",
    "kling-official"
  ],
  "network_required": true,
  "factory_status": "DISABLED_BY_DEFAULT"
}
```

## Related knowledge

- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]
- [[07-SKILLS/disabled-by-default/kling-official|kling-official]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
