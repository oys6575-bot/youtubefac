---
card_id: tool.face_tracker
type: tool
title: face_tracker
status: LOCAL_SETUP_REQUIRED
knowledge_schema: '1.0'
generated: true
tool_name: face_tracker
capability: analysis
provider: mediapipe
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# face_tracker

## Capability

analysis

## Factory use

Provider: `mediapipe`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg

## Canonical record

```json
{
  "name": "face_tracker",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
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
