---
card_id: tool.diagram_gen
type: tool
title: diagram_gen
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: diagram_gen
capability: graphics
provider: mermaid
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# diagram_gen

## Capability

graphics

## Factory use

Provider: `mermaid`  
Runtime: `local`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "diagram_gen",
  "version": "0.1.0",
  "tier": "core",
  "capability": "graphics",
  "provider": "mermaid",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "beautiful-mermaid",
    "d3-viz"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/optional/beautiful-mermaid|beautiful-mermaid]]
- [[07-SKILLS/optional/d3-viz|d3-viz]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
