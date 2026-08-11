---
card_id: tool.lip_sync
type: tool
title: lip_sync
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: lip_sync
capability: avatar
provider: wav2lip
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# lip_sync

## Capability

avatar

## Factory use

Provider: `wav2lip`  
Runtime: `local_gpu`

## Dependencies

- python:torch
- cmd:ffmpeg

## Canonical record

```json
{
  "name": "lip_sync",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "avatar",
  "provider": "wav2lip",
  "runtime": "local_gpu",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
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
