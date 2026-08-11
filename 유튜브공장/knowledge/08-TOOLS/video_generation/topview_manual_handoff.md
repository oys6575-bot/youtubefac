---
card_id: tool.topview_manual_handoff
type: tool
title: topview_manual_handoff
status: MANUAL_BRIDGE
knowledge_schema: '1.0'
generated: true
tool_name: topview_manual_handoff
capability: video_generation
provider: topview_manual
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# topview_manual_handoff

## Capability

video_generation

## Factory use

Provider: `topview_manual`  
Runtime: `local`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "topview_manual_handoff",
  "version": "1.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "topview_manual",
  "runtime": "local",
  "captured_status": "available",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "topview-manual-handoff"
  ],
  "network_required": false,
  "factory_status": "MANUAL_BRIDGE"
}
```

## Related knowledge

- [[07-SKILLS/required/topview-manual-handoff|topview-manual-handoff]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
