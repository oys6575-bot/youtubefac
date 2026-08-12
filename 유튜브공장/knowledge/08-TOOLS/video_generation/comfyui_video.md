---
card_id: tool.comfyui_video
type: tool
title: comfyui_video
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: comfyui_video
capability: video_generation
provider: comfyui
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# comfyui_video

## Capability

video_generation

## Factory use

Provider: `comfyui`  
Runtime: `local_gpu`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "comfyui_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "comfyui",
  "runtime": "local_gpu",
  "captured_status": "degraded",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "comfyui",
    "ai-video-gen",
    "ltx2"
  ],
  "network_required": false,
  "factory_status": "OPTIONAL"
}
```

## Related knowledge

- [[07-SKILLS/required/comfyui|comfyui]]
- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]
- [[07-SKILLS/required/ltx2|ltx2]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
