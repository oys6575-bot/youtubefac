---
card_id: tool.upscale
type: tool
title: upscale
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: upscale
capability: enhancement
provider: realesrgan
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# upscale

## Capability

enhancement

## Factory use

Provider: `realesrgan`  
Runtime: `local_gpu`

## Dependencies

- python:realesrgan
- python:torch
- cmd:ffmpeg

## Canonical record

```json
{
  "name": "upscale",
  "version": "0.1.0",
  "tier": "enhance",
  "capability": "enhancement",
  "provider": "realesrgan",
  "runtime": "local_gpu",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "python:realesrgan",
    "python:torch",
    "cmd:ffmpeg"
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
