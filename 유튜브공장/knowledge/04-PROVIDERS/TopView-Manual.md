# TopView Manual

TopView is a semi-automated production workstation, not the factory control plane.

## Allowed flow

1. OpenMontage records the approved work order.
2. MK Visual Director exports shot intent, references, negative constraints, duration, aspect ratio, and exact fact overlays.
3. A human selects the current TopView UI feature and exact visible model label.
4. A human submits and downloads the result.
5. The result is ingested back into OpenMontage with provenance and selection state.

## Forbidden flow

- No TopView API calls
- No TopView MCP execution
- No browser automation or hidden paid dispatch
- No replacement of Visual Director decisions
- No automatic approval of generated assets

See [[01-MAPS/Providers]] for all indexed capabilities and model families.
