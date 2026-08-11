---
card_id: tool.screen_recorder
type: tool
title: screen_recorder
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: screen_recorder
capability: screen_capture
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# screen_recorder

## Capability

screen_capture

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- binary:ffmpeg

## Canonical record

```json
{
  "name": "screen_recorder",
  "version": "0.1.0",
  "tier": "source",
  "capability": "screen_capture",
  "provider": "ffmpeg",
  "runtime": "local",
  "captured_status": "available",
  "stability": "beta",
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
