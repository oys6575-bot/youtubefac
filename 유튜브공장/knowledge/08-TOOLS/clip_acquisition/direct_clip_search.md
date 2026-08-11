---
card_id: tool.direct_clip_search
type: tool
title: direct_clip_search
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: direct_clip_search
capability: clip_acquisition
provider: openmontage
runtime: hybrid
network_required: true
canonical_source: config/tool-inventory.json
---

# direct_clip_search

## Capability

clip_acquisition

## Factory use

Provider: `openmontage`  
Runtime: `hybrid`

## Dependencies

- python:requests

## Canonical record

```json
{
  "name": "direct_clip_search",
  "version": "0.1.0",
  "tier": "source",
  "capability": "clip_acquisition",
  "provider": "openmontage",
  "runtime": "hybrid",
  "captured_status": "available",
  "stability": "beta",
  "dependencies": [
    "python:requests"
  ],
  "agent_skills": [],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
