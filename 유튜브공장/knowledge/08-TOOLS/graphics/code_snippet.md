---
card_id: tool.code_snippet
type: tool
title: code_snippet
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: code_snippet
capability: graphics
provider: pygments
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# code_snippet

## Capability

graphics

## Factory use

Provider: `pygments`  
Runtime: `local`

## Dependencies

- python:pygments
- python:PIL

## Canonical record

```json
{
  "name": "code_snippet",
  "version": "0.1.0",
  "tier": "core",
  "capability": "graphics",
  "provider": "pygments",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [
    "python:pygments",
    "python:PIL"
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
