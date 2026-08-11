---
card_id: tool.wan_video
type: tool
title: wan_video
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: wan_video
capability: video_generation
provider: wan
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# wan_video

## Capability

video_generation

## Factory use

Provider: `wan`  
Runtime: `local_gpu`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "wan_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "wan",
  "runtime": "local_gpu",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "ltx2"
  ],
  "network_required": false,
  "factory_status": "OPTIONAL"
}
```

## Related knowledge

- [[07-SKILLS/required/ltx2|ltx2]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
