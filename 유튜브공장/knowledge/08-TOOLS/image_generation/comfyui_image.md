---
card_id: tool.comfyui_image
type: tool
title: comfyui_image
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: comfyui_image
capability: image_generation
provider: comfyui
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# comfyui_image

## Capability

image_generation

## Factory use

Provider: `comfyui`  
Runtime: `local_gpu`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "comfyui_image",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "image_generation",
  "provider": "comfyui",
  "runtime": "local_gpu",
  "captured_status": "degraded",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "comfyui",
    "flux-best-practices"
  ],
  "network_required": false,
  "factory_status": "OPTIONAL"
}
```

## Related knowledge

- [[07-SKILLS/required/comfyui|comfyui]]
- [[07-SKILLS/required/flux-best-practices|flux-best-practices]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
