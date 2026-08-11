---
card_id: tool.remotion_caption_burn
type: tool
title: remotion_caption_burn
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: remotion_caption_burn
capability: subtitle
provider: remotion
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# remotion_caption_burn

## Capability

subtitle

## Factory use

Provider: `remotion`  
Runtime: `local`

## Dependencies

- cmd:ffmpeg
- cmd:ffprobe

## Canonical record

```json
{
  "name": "remotion_caption_burn",
  "version": "0.1.0",
  "tier": "core",
  "capability": "subtitle",
  "provider": "remotion",
  "runtime": "local",
  "captured_status": "available",
  "stability": "experimental",
  "dependencies": [
    "cmd:ffmpeg",
    "cmd:ffprobe"
  ],
  "agent_skills": [
    "remotion-best-practices",
    "ffmpeg"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/required/remotion-best-practices|remotion-best-practices]]
- [[07-SKILLS/required/ffmpeg|ffmpeg]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
