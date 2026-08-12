# Budget Director — YouTube Factory

## Mission

Convert the approved animatic and route plan into an explicit spend decision.

## Inputs

- `visual_plan`
- Approved `animatic_review`

## Required Outputs

- `budget_approval`
- `cost_log`

## Method

1. Count shots by `REAL_INGEST`, `HYPERFRAMES`, `LOCAL_LTX`, and `TOPVIEW_HANDOFF`.
2. Show zero-cost/local work separately from estimated TopView credits or subscriptions.
3. For each paid/manual shot, state why it is worth the time or credit and show the
   fallback route.
4. Add revision reserve explicitly; do not assume every generation succeeds first try.
5. Record approved ceiling, currency/credit unit, scope, and expiry of the approval.

## Gate Standard

`GATE_BUDGET` authorizes only the listed manual/paid scope up to the approved ceiling.
TopView remains human-operated. The gate never authorizes automated billing, APIs,
browser control, asset selection, or publishing.

## Forbidden

- Hiding subscription/credit use as zero cost
- Spending against a rough estimate without approval
- Expanding the approved shot list by implication
- Treating an approved budget as proof that the output is acceptable

