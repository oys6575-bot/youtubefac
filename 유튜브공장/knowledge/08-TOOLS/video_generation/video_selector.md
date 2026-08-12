---
card_id: tool.video_selector
type: tool
title: video_selector
status: PLANNING_ONLY
knowledge_schema: '1.0'
generated: true
tool_name: video_selector
capability: video_generation
provider: selector
runtime: hybrid
network_required: false
canonical_source: config/tool-inventory.json
---

# video_selector

## Capability

video_generation

## Factory use

Provider: `selector`  
Runtime: `hybrid`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "video_selector",
  "version": "0.3.1",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "selector",
  "runtime": "hybrid",
  "captured_status": "available",
  "stability": "beta",
  "dependencies": [],
  "agent_skills": [
    "ai-video-gen",
    "create-video",
    "ltx2",
    "gemini-omni"
  ],
  "network_required": false,
  "factory_status": "PLANNING_ONLY"
}
```

## Related knowledge

- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]
- [[07-SKILLS/disabled-by-default/create-video|create-video]]
- [[07-SKILLS/required/ltx2|ltx2]]
- [[07-SKILLS/disabled-by-default/gemini-omni|gemini-omni]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
