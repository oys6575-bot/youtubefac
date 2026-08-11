---
card_id: tool.jimeng_video
type: tool
title: jimeng_video
status: DISABLED_BY_DEFAULT
knowledge_schema: '1.0'
generated: true
tool_name: jimeng_video
capability: video_generation
provider: volcengine
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# jimeng_video

## Capability

video_generation

## Factory use

Provider: `volcengine`  
Runtime: `api`

## Dependencies

- env:VOLC_ACCESSKEY
- env:VOLC_SECRETKEY

## Canonical record

```json
{
  "name": "jimeng_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "volcengine",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "env:VOLC_ACCESSKEY",
    "env:VOLC_SECRETKEY"
  ],
  "agent_skills": [
    "ai-video-gen"
  ],
  "network_required": true,
  "factory_status": "DISABLED_BY_DEFAULT"
}
```

## Related knowledge

- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
