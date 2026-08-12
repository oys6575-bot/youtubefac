---
card_id: tool.clip_search
type: tool
title: clip_search
status: LOCAL_SETUP_REQUIRED
knowledge_schema: '1.0'
generated: true
tool_name: clip_search
capability: clip_retrieval
provider: openmontage
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# clip_search

## Capability

clip_retrieval

## Factory use

Provider: `openmontage`  
Runtime: `local`

## Dependencies

- python:numpy
- python:transformers
- python:torch

## Canonical record

```json
{
  "name": "clip_search",
  "version": "0.1.0",
  "tier": "analyze",
  "capability": "clip_retrieval",
  "provider": "openmontage",
  "runtime": "local",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "python:numpy",
    "python:transformers",
    "python:torch"
  ],
  "agent_skills": [],
  "network_required": false,
  "factory_status": "LOCAL_SETUP_REQUIRED"
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
