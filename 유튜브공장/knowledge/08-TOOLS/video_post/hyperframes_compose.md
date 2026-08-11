---
card_id: tool.hyperframes_compose
type: tool
title: hyperframes_compose
status: ACTIVE_LOCAL
knowledge_schema: '1.0'
generated: true
tool_name: hyperframes_compose
capability: video_post
provider: hyperframes
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# hyperframes_compose

## Capability

video_post

## Factory use

Provider: `hyperframes`  
Runtime: `local`

## Dependencies

- cmd:npx
- cmd:ffmpeg

## Canonical record

```json
{
  "name": "hyperframes_compose",
  "version": "0.1.1",
  "tier": "core",
  "capability": "video_post",
  "provider": "hyperframes",
  "runtime": "local",
  "captured_status": "available",
  "stability": "beta",
  "dependencies": [
    "cmd:npx",
    "cmd:ffmpeg"
  ],
  "agent_skills": [
    "hyperframes",
    "hyperframes-cli",
    "hyperframes-registry",
    "website-to-hyperframes",
    "gsap-core",
    "gsap-timeline"
  ],
  "network_required": false,
  "factory_status": "ACTIVE_LOCAL"
}
```

## Related knowledge

- [[07-SKILLS/required/hyperframes|hyperframes]]
- [[07-SKILLS/required/hyperframes-cli|hyperframes-cli]]
- [[07-SKILLS/required/hyperframes-registry|hyperframes-registry]]
- [[07-SKILLS/optional/gsap-core|gsap-core]]
- [[07-SKILLS/optional/gsap-timeline|gsap-timeline]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
