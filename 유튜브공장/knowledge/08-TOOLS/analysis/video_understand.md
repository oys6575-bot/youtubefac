---
card_id: tool.video_understand
type: tool
title: video_understand
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: video_understand
capability: analysis
provider: transformers
runtime: local_gpu
network_required: false
canonical_source: config/tool-inventory.json
---

# video_understand

## Capability

analysis

## Factory use

Provider: `transformers`  
Runtime: `local_gpu`

## Dependencies

- python:transformers
- python:torch

## Canonical record

```json
{
  "name": "video_understand",
  "version": "0.1.0",
  "tier": "analyze",
  "capability": "analysis",
  "provider": "transformers",
  "runtime": "local_gpu",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "python:transformers",
    "python:torch"
  ],
  "agent_skills": [
    "video-understand"
  ],
  "network_required": false,
  "factory_status": "OPTIONAL"
}
```

## Related knowledge

- [[07-SKILLS/required/video-understand|video-understand]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
