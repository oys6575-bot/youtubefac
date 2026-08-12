# Production Dashboard Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the operator-oriented dashboard with a seven-category production dashboard that exposes current work, scripts, media previews, editing gaps, review routing, and approved finals.

**Architecture:** Extend the existing read-only `build_mobile_state()` projection with bounded production-view models and authenticated manifest-backed media routes. Replace the current empty panels with a responsive state-driven UI. Preserve canonical project files and existing action security; stale gates are suppressed in the projection rather than deleted.

**Tech Stack:** Python 3.11, FastAPI/Starlette, JSON artifacts and checkpoints, vanilla JavaScript, CSS, pytest, ffmpeg for local video preview derivatives.

## Global Constraints

- Top-level navigation is exactly `현황`, `주제`, `대본`, `에셋`, `편집`, `검수`, `최종`.
- Do not delete or rewrite canonical checkpoints or artifacts.
- Do not expose source URLs, licenses, credentials, or absolute local paths in the mobile projection.
- All media responses must resolve to a manifest-listed file inside the selected project.
- Final-review failure returns to edit only after a human decision.
- Publishing and external upload remain out of scope.

---

### Task 1: Stale gate and production projection

**Files:**
- Modify: `backlot/mobile_state.py`
- Test: `tests/backlot/test_mobile_state.py`

**Interfaces:**
- Consumes: canonical checkpoint timestamps and project artifacts
- Produces: `current_work`, `script_view`, `asset_library`, `edit_view`, `review_view`, `final_view`, and a current gate that excludes stale approvals

- [ ] Write a failing state test where `checkpoint_media_collection.json` is newer than an awaiting `checkpoint_proposal.json` and assert `current_gate is None`.
- [ ] Run the focused state test and confirm it fails because the old proposal gate is still projected.
- [ ] Add timestamp comparison that suppresses a proposal gate superseded by media collection without changing either checkpoint.
- [ ] Add failing tests for bounded script, media, edit, review, and final projections using literal fixtures.
- [ ] Implement minimal artifact readers that return empty-state models when artifacts are absent and never leak `local_path`, `direct_url`, or license fields.
- [ ] Run `pytest tests/backlot/test_mobile_state.py -q` and confirm the projection tests pass.

### Task 2: Authenticated media and preview routes

**Files:**
- Create: `backlot/media_library.py`
- Create: `scripts/build-media-previews.py`
- Modify: `backlot/server.py`
- Test: `tests/backlot/test_mobile_api.py`
- Test: `tests/backlot/test_mobile_security.py`

**Interfaces:**
- Consumes: `artifacts/media_collection_manifest.json`
- Produces: `GET /api/mobile/project/{project_id}/media/{asset_id}` and `/preview/{asset_id}`

- [ ] Write failing API tests for an authenticated manifest-listed image, unauthenticated access, an unknown id, and a manifest path outside the project.
- [ ] Run the route tests and confirm 404/401 failures are caused by the missing endpoints.
- [ ] Implement exact-id manifest lookup and safe path resolution under `projects/{project_id}/assets`.
- [ ] Return image/video bytes with a bounded MIME allowlist and no-store headers.
- [ ] Add a preview builder that copies or scales image thumbnails and extracts one representative JPEG frame from videos into `automation/previews/media_collection`.
- [ ] Expose only existing preview derivatives and use a media-type placeholder when no preview exists.
- [ ] Run the API and security tests and confirm all cases pass.

### Task 3: Seven-category responsive UI

**Files:**
- Modify: `backlot/ui/mobile.html`
- Modify: `backlot/ui/mobile.js`
- Modify: `backlot/ui/mobile.css`
- Test: `tests/contracts/test_mobile_dashboard_contract.py`
- Test: `tests/contracts/test_mobile_dashboard_operations.py`

**Interfaces:**
- Consumes: dashboard projection from Tasks 1 and 2
- Produces: responsive status, topic, script, asset, edit, review, and final panels

- [ ] Write failing browser-contract tests that query exactly seven navigation controls and the required panel/tab/media dialog elements.
- [ ] Run the contract tests and confirm they fail against the eight-menu operator UI.
- [ ] Replace sidebar and bottom navigation with the seven approved labels.
- [ ] Replace empty panels with deterministic rendering targets for script text, visual prompts, asset filters/grid, edit gaps, review findings/player, and final player/download.
- [ ] Render current work first on status and omit the Human Gate card entirely when `current_gate` is absent.
- [ ] Render image/video thumbnails with lazy loading; clicking opens an accessible media dialog and video controls.
- [ ] Render edit shortages and review-return actions only when backed by projection data.
- [ ] Run contract tests and focused dashboard tests until green.

### Task 4: Review-return action

**Files:**
- Modify: `backlot/mobile_actions.py`
- Modify: `backlot/server.py`
- Modify: `backlot/ui/mobile.js`
- Test: `tests/backlot/test_mobile_actions.py`
- Test: `tests/backlot/test_mobile_action_transaction.py`

**Interfaces:**
- Consumes: a current `final_review` gate and expected checkpoint SHA-256
- Produces: an append-only human revision decision that leaves canonical history intact and reactivates edit according to existing checkpoint policy

- [ ] Write a failing transaction test for `return_to_edit` requiring a reason and current final-review hash.
- [ ] Confirm the action fails before implementation and rejects stale hashes.
- [ ] Implement the action through the existing decision receipt and lock transaction path.
- [ ] Wire `편집으로 되돌리기` to the action only on a current review gate.
- [ ] Run mobile action and transaction tests and confirm success, concurrency rejection, and idempotent replay.

### Task 5: Live project previews and deployment verification

**Files:**
- Runtime output: `projects/collapse-topic-pilot-2026-08-12/automation/previews/media_collection/`
- Update: `docs/verification/production-dashboard-redesign.md`

**Interfaces:**
- Consumes: the existing 75-item collection manifest and completed implementation
- Produces: visible thumbnails on the Tailscale dashboard and a verification report

- [ ] Generate preview derivatives for the current project without altering source assets.
- [ ] Run focused tests, all contract tests, and the complete backlot test suite.
- [ ] Restart the dashboard service and request the live dashboard and sample media routes through Tailscale.
- [ ] Inspect the mobile layout, asset grid, image expansion, video playback, stale-gate absence, and each of the seven navigation panels.
- [ ] Record command results and visual findings in the verification document.
- [ ] Commit, push the existing feature branch, and update the existing draft PR without publishing or approving a Human Gate.

