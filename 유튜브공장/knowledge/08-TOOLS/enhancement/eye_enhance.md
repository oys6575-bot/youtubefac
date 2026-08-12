---
card_id: tool.eye_enhance
type: tool
title: eye_enhance
status: LOCAL_SETUP_REQUIRED
knowledge_schema: '1.0'
generated: true
tool_name: eye_enhance
capability: enhancement
provider: mediapipe
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# eye_enhance

## Capability

enhancement

## Factory use

Provider: `mediapipe`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg

## Canonical record

```json
{
  "name": "eye_enhance",
  "version": "0.1.0",
  "tier": "enhance",
  "capability": "enhancement",
  "provider": "mediapipe",
  "runtime": "local",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "cmd:ffmpeg"
  ],
  "agent_skills": [
    "ffmpeg"
  ],
  "network_required": false,
  "factory_status": "LOCAL_SETUP_REQUIRED"
}
```

## Related knowledge

- [[07-SKILLS/required/ffmpeg|ffmpeg]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
