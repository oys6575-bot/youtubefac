---
card_id: tool.face_restore
type: tool
title: face_restore
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: face_restore
capability: enhancement
provider: codeformer
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# face_restore

## Capability

enhancement

## Factory use

Provider: `codeformer`  
Runtime: `local_gpu`

## Dependencies

- python:gfpgan
- python:torch

## Canonical record

```json
{
  "name": "face_restore",
  "version": "0.1.0",
  "tier": "enhance",
  "capability": "enhancement",
  "provider": "codeformer",
  "runtime": "local_gpu",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "python:gfpgan",
    "python:torch"
  ],
  "agent_skills": [
    "ffmpeg"
  ],
  "network_required": false,
  "factory_status": "OPTIONAL"
}
```

## Related knowledge

- [[07-SKILLS/required/ffmpeg|ffmpeg]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
