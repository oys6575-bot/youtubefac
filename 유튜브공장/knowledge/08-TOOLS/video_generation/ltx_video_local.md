---
card_id: tool.ltx_video_local
type: tool
title: ltx_video_local
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: ltx_video_local
capability: video_generation
provider: ltx
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# ltx_video_local

## Capability

video_generation

## Factory use

Provider: `ltx`  
Runtime: `local_gpu`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "ltx_video_local",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "ltx",
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
