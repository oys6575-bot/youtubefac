---
card_id: tool.frame_sampler
type: tool
title: frame_sampler
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: frame_sampler
capability: analysis
provider: ffmpeg
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# frame_sampler

## Capability

analysis

## Factory use

Provider: `ffmpeg`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg

## Canonical record

```json
{
  "name": "frame_sampler",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
  "provider": "ffmpeg",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [
    "cmd:ffmpeg"
  ],
  "agent_skills": [
    "ffmpeg"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/required/ffmpeg|ffmpeg]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
