---
card_id: tool.kling_lip_sync
type: tool
title: kling_lip_sync
status: DISABLED_BY_DEFAULT
knowledge_schema: '1.0'
generated: true
tool_name: kling_lip_sync
capability: avatar
provider: kling_official
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# kling_lip_sync

## Capability

avatar

## Factory use

Provider: `kling_official`  
Runtime: `api`

## Dependencies

- env:KLING_API_KEY

## Canonical record

```json
{
  "name": "kling_lip_sync",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "avatar",
  "provider": "kling_official",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "env:KLING_API_KEY"
  ],
  "agent_skills": [
    "kling-official",
    "avatar-video"
  ],
  "network_required": true,
  "factory_status": "DISABLED_BY_DEFAULT"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/kling-official|kling-official]]
- [[07-SKILLS/disabled-by-default/avatar-video|avatar-video]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
