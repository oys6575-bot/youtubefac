---
card_id: tool.audio_probe
type: tool
title: audio_probe
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: audio_probe
capability: analysis
provider: ffprobe
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# audio_probe

## Capability

analysis

## Factory use

Provider: `ffprobe`  
Runtime: `local`

## Dependencies

- binary:ffprobe

## Canonical record

```json
{
  "name": "audio_probe",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
  "provider": "ffprobe",
  "runtime": "local",
  "captured_status": "available",
  "stability": "production",
  "dependencies": [
    "binary:ffprobe"
  ],
  "agent_skills": [],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
