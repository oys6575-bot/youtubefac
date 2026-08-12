---
card_id: tool.video_downloader
type: tool
title: video_downloader
status: EXPLICIT_OPT_IN
knowledge_schema: '1.0'
generated: true
tool_name: video_downloader
capability: source_ingest
provider: yt-dlp
runtime: local
network_required: true
canonical_source: config/tool-inventory.json
---

# video_downloader

## Capability

source_ingest

## Factory use

Provider: `yt-dlp`  
Runtime: `local`

## Dependencies

- python:yt_dlp

## Canonical record

```json
{
  "name": "video_downloader",
  "version": "0.1.0",
  "tier": "source",
  "capability": "source_ingest",
  "provider": "yt-dlp",
  "runtime": "local",
  "captured_status": "unavailable",
  "stability": "production",
  "dependencies": [
    "python:yt_dlp"
  ],
  "agent_skills": [
    "video-download"
  ],
  "network_required": true,
  "factory_status": "EXPLICIT_OPT_IN"
}
```

## Related knowledge

- [[07-SKILLS/required/video-download|video-download]]

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
