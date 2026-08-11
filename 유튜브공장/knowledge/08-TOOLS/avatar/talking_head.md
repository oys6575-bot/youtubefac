---
card_id: tool.talking_head
type: tool
title: talking_head
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: talking_head
capability: avatar
provider: sadtalker
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# talking_head

## Capability

avatar

## Factory use

Provider: `sadtalker`  
Runtime: `local_gpu`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "talking_head",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "avatar",
  "provider": "sadtalker",
  "runtime": "local_gpu",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
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
