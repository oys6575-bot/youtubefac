---
card_id: tool.corpus_builder
type: tool
title: corpus_builder
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: corpus_builder
capability: corpus_population
provider: openmontage
runtime: hybrid
network_required: true
canonical_source: config/tool-inventory.json
---

# corpus_builder

## Capability

corpus_population

## Factory use

Provider: `openmontage`  
Runtime: `hybrid`

## Dependencies

- python:cv2
- python:numpy
- python:requests
- python:PIL
- python:transformers
- python:torch

## Canonical record

```json
{
  "name": "corpus_builder",
  "version": "0.1.0",
  "tier": "source",
  "capability": "corpus_population",
  "provider": "openmontage",
  "runtime": "hybrid",
  "captured_status": "degraded",
  "stability": "experimental",
  "dependencies": [
    "python:cv2",
    "python:numpy",
    "python:requests",
    "python:PIL",
    "python:transformers",
    "python:torch"
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
