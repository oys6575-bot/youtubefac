---
card_id: tool.transcript_fetcher
type: tool
title: transcript_fetcher
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: transcript_fetcher
capability: analysis
provider: youtube-transcript-api
runtime: local
network_required: true
canonical_source: config/tool-inventory.json
---

# transcript_fetcher

## Capability

analysis

## Factory use

Provider: `youtube-transcript-api`  
Runtime: `local`

## Dependencies

- python:youtube_transcript_api

## Canonical record

```json
{
  "name": "transcript_fetcher",
  "version": "0.1.0",
  "tier": "analyze",
  "capability": "analysis",
  "provider": "youtube-transcript-api",
  "runtime": "local",
  "captured_status": "unavailable",
  "stability": "production",
  "dependencies": [
    "python:youtube_transcript_api"
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
