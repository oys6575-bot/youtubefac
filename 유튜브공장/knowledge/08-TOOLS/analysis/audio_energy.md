---
card_id: tool.audio_energy
type: tool
title: audio_energy
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: audio_energy
capability: analysis
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# audio_energy

## Capability

analysis

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- binary:ffmpeg

## Canonical record

```json
{
  "name": "audio_energy",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
  "provider": "ffmpeg",
  "runtime": "local",
  "captured_status": "available",
  "stability": "production",
  "dependencies": [
    "binary:ffmpeg"
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
