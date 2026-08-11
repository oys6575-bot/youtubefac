---
card_id: tool.seedance_replicate
type: tool
title: seedance_replicate
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: seedance_replicate
capability: video_generation
provider: seedance
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# seedance_replicate

## Capability

video_generation

## Factory use

Provider: `seedance`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "seedance_replicate",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "seedance",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "seedance-2-0",
    "ai-video-gen"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/seedance-2-0|seedance-2-0]]
- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
