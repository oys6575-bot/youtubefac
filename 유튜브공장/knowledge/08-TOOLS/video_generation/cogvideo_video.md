---
card_id: tool.cogvideo_video
type: tool
title: cogvideo_video
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: cogvideo_video
capability: video_generation
provider: cogvideo
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# cogvideo_video

## Capability

video_generation

## Factory use

Provider: `cogvideo`  
Runtime: `local_gpu`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "cogvideo_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "cogvideo",
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
