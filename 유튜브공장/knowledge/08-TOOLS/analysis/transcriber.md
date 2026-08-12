---
card_id: tool.transcriber
type: tool
title: transcriber
status: LOCAL_SETUP_REQUIRED
knowledge_schema: '1.0'
generated: true
tool_name: transcriber
capability: analysis
provider: whisperx
runtime: local
network_required: false
canonical_source: config/tool-inventory.json
---

# transcriber

## Capability

analysis

## Factory use

Provider: `whisperx`  
Runtime: `local`

## Dependencies

- python:faster_whisper

## Canonical record

```json
{
  "name": "transcriber",
  "version": "0.1.0",
  "tier": "core",
  "capability": "analysis",
  "provider": "whisperx",
  "runtime": "local",
  "captured_status": "unavailable",
  "stability": "experimental",
  "dependencies": [
    "python:faster_whisper"
  ],
  "agent_skills": [
    "speech-to-text"
  ],
  "network_required": false,
  "factory_status": "LOCAL_SETUP_REQUIRED"
}
```

## Related knowledge

- [[07-SKILLS/required/speech-to-text|speech-to-text]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
