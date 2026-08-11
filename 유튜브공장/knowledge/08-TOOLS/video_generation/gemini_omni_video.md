---
card_id: tool.gemini_omni_video
type: tool
title: gemini_omni_video
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: gemini_omni_video
capability: video_generation
provider: gemini_omni
runtime: api
network_required: true
canonical_source: config/tool-inventory.json
---

# gemini_omni_video

## Capability

video_generation

## Factory use

Provider: `gemini_omni`  
Runtime: `api`

## Dependencies

_None recorded._

## Canonical record

```json
{
  "name": "gemini_omni_video",
  "version": "0.1.0",
  "tier": "generate",
  "capability": "video_generation",
  "provider": "gemini_omni",
  "runtime": "api",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [],
  "agent_skills": [
    "gemini-omni",
    "ai-video-gen"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/disabled-by-default/gemini-omni|gemini-omni]]
- [[07-SKILLS/required/ai-video-gen|ai-video-gen]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
