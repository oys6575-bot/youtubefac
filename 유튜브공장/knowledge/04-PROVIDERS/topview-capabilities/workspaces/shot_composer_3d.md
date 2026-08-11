---
card_id: topview-capability.workspaces.shot_composer_3d
type: topview-capability
title: 3D Shot Composer
status: OPTIONAL_MANUAL
knowledge_schema: '1.0'
generated: true
capability_id: shot_composer_3d
capability_group: workspaces
execution_mode: MANUAL_UI_ONLY
canonical_source: config/topview-capabilities.yaml
---

# 3D Shot Composer

## Capability

Place characters, props, and virtual camera before generating angles

## Use for

Complex spatial continuity or repeatable camera-angle exploration

## Do not use for

Ordinary single-reference shots where setup time exceeds value

## Execution boundary

TopView is operated manually in its UI after approval. No API, MCP, browser automation, paid call, or implicit dispatch is allowed.

## Canonical record

```json
{
  "group": "workspaces",
  "id": "shot_composer_3d",
  "official_name": "3D Shot Composer",
  "capability": "Place characters, props, and virtual camera before generating angles",
  "factory_status": "OPTIONAL_MANUAL",
  "use_for": "Complex spatial continuity or repeatable camera-angle exploration",
  "do_not_use_for": "Ordinary single-reference shots where setup time exceeds value"
}
```

## Related knowledge

_None recorded._

## Production notes

<!-- USER-NOTES:BEGIN -->
<!-- USER-NOTES:END -->
