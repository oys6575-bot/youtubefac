---
card_id: tool.bg_remove
type: tool
title: bg_remove
status: OPTIONAL
knowledge_schema: '1.0'
generated: true
tool_name: bg_remove
capability: enhancement
provider: rembg
runtime: hybrid
network_required: false
canonical_source: config/tool-inventory.json
---

# bg_remove

## Capability

enhancement

## Factory use

Provider: `rembg`  
Runtime: `hybrid`

## Dependencies

- python:rembg
- python:PIL

## Canonical record

```json
{
  "name": "bg_remove",
  "version": "0.1.0",
  "tier": "enhance",
  "capability": "enhancement",
  "provider": "rembg",
  "runtime": "hybrid",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "python:rembg",
    "python:PIL"
  ],
  "agent_skills": [
    "ffmpeg"
  ],
  "network_required": false,
  "factory_status": "OPTIONAL"
}
```

## Related knowledge

- [[07-SKILLS/required/ffmpeg|ffmpeg]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
