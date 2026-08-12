# Topic Approval Auto-Dispatch Design

**Status:** User-approved design candidate  
**Date:** 2026-08-12  
**Scope:** `youtube-factory` pipeline from topic approval through proposal review

## Problem

The authenticated mobile dashboard currently records a topic approval but does not start the next pipeline stage. The user must then send a second instruction to an agent. That duplicates the same Human Gate and weakens the dashboard's purpose.

The approval HTTP request must not run research inline. Mobile connections can close, research can take minutes, and retrying the request could start duplicate work. Approval and execution therefore remain separate processes while becoming one user action.

## Goals

- A valid `approve_topic` receipt automatically schedules the safe post-approval stages.
- Work continues after the phone disconnects or the dashboard closes.
- The system performs research, independent evidence verification, and proposal authoring without another user message.
- Each failed stage is retried once using the same assigned runtime and model.
- The pipeline stops at the proposal Human Gate.
- The dashboard shows queued, running, retrying, failed, and awaiting-human states.
- Replayed approval requests and worker restarts never duplicate a stage run.

## Non-Goals

- No paid API calls.
- No TopView dispatch; TopView remains manual and semi-automatic.
- No asset generation, script generation, visual-plan generation, render, upload, or publish.
- No automatic approval of the proposal or any later Human Gate.
- No silent provider or model fallback.

## Chosen Architecture

Use a durable transactional outbox plus one local Coordinator worker.

```text
Mobile topic approval
  -> atomically save checkpoint + receipt + queued job
  -> return success to the phone

Coordinator worker
  -> claim the queued job exactly once
  -> research (Hermes / Qwen)
  -> evidence lock and independent verification (Codex)
  -> proposal (Claude / Story-Visual role)
  -> write proposal checkpoint as awaiting_human
```

The web server never launches agents directly. The approval transaction writes the job beside the canonical project state. A separately supervised worker claims and executes it.

## Durable Job Contract

Each successful topic approval creates one file:

`projects/<project-id>/automation/jobs/<approval-receipt-id>.json`

Required fields:

- `version`: `1.0`
- `job_id`: approval receipt UUID
- `project_id`
- `trigger_receipt_path`
- `trigger_checkpoint_sha256`
- `selected_candidate_id`
- `state`: `queued | running | retrying | awaiting_human | failed | completed`
- `current_stage`: `research | evidence_lock | proposal`
- `attempt`: integer, beginning at `0`
- `max_retries`: exactly `1`
- `created_at`, `updated_at`
- `stage_results`: exact artifact paths, SHA-256 values, source commits, and verdicts
- `last_error`: null or a structured error with stage, class, message, and timestamp

The approval receipt ID is the job ID. Existing approval idempotency therefore also prevents duplicate jobs. The approval checkpoint, receipt, and queued job are written by the existing prepared-journal transaction.

## Worker and Recovery

The Coordinator worker runs as a dedicated user LaunchAgent and polls only the canonical `projects/` root. It processes one job at a time per project.

Claiming uses the existing per-project lock and an atomic job-state update. Before every stage, the worker verifies:

1. The trigger receipt exists and validates.
2. The topic approval checkpoint is completed and `human_approved` is true.
3. The selected candidate matches the canonical `topic_selection` artifact.
4. The expected prerequisite artifact hashes still match.
5. The requested stage is on the safe auto-dispatch allowlist.

On restart, a `running` or `retrying` job with no live worker lease is recovered from its last settled stage result. A completed stage with matching artifact hashes is not rerun.

## Stage Routing

### 1. Research

- Runtime: Hermes
- Model: `qwen3.6-35b-a3b-mlx`
- Director: `skills/pipelines/youtube-factory/evidence-director.md`
- Outputs: schema-valid `research_brief` and `evidence_registry`
- Constraints: official and primary sources first; no paid providers; no media generation

### 2. Evidence Lock and Independent Verification

- Runtime: Codex
- Model: `gpt-5.6-sol`
- Inputs are bound to the exact research artifact SHA-256 values and source commit.
- Outputs: verified `evidence_registry`, `decision_log`, and machine-readable PASS/FAIL review.
- `evidence_lock` changes from a separate Human Gate to a machine gate that completes only on independent PASS.
- Disputed or unsupported claims remain visibly marked or block progression; the verifier cannot silently rewrite the research source.

### 3. Proposal

- Runtime: Claude Story-Visual role
- Model: configured Claude model from `config/orca-model-routing.yaml`
- Outputs: schema-valid `proposal_packet` and `decision_log`
- The proposal includes the evidence summary, disputed claims, source-rights warnings, runtime options, and cost boundary.
- The proposal checkpoint is written `awaiting_human` with `human_approved: false`.

The effective automatic flow is:

`topic_approval -> research -> evidence_lock(PASS) -> proposal(awaiting_human)`

## Retry and Failure Policy

- A failed stage is retried automatically once.
- Retry uses the same role, runtime, model, input hashes, and stage instructions.
- Authentication failure, missing prerequisite, hash mismatch, invalid schema, or policy violation is not retried; it fails immediately.
- After the second ordinary failure, the job becomes `failed` and no later stage starts.
- The dashboard shows the failed stage, concise cause, attempt count, and an allowlisted `다시 실행` action.
- Manual retry creates a new retry receipt and resumes from the last settled stage; it never rewrites the original job history.

## Dashboard Behavior

Immediately after topic approval, the confirmation dialog closes and the dashboard shows `자료조사 시작 대기`. Server-sent events update it to:

- `자료조사 실행 중`
- `사실검증 실행 중`
- `기획안 작성 중`
- `기획안 승인 대기`
- or `실패 · 다시 실행 가능`

The dashboard reads job state from disk and does not hold an in-memory execution queue. Closing the app has no effect on the worker.

## Configuration Changes

- `control_plane.pilot_stop_gate` becomes `proposal`.
- Add a safe auto-dispatch policy covering only `research`, `evidence_lock`, and `proposal`.
- Preserve `topview.automatic_dispatch: false`.
- Preserve all paid-call, asset-selection, final-review, and publish gates.
- Preserve resource-lane limits and the prohibition on silent model switching.

## Security and Safety

- Only an authenticated, authorized topic approval receipt can create the initial job.
- Job payloads cannot contain shell commands, arbitrary paths, providers, models, or stage names outside the allowlist.
- The web process cannot execute Orca or shell commands.
- The worker writes only to the canonical project root and coordination records allowed by its role.
- Every transition is append-only or transactionally journaled and remains auditable.
- No job transition is treated as Human Gate approval.

## Acceptance Criteria

1. One topic approval creates exactly one receipt and one queued job.
2. Replaying the same approval returns the existing receipt and creates no second job.
3. The approval response returns without waiting for research.
4. A stopped and restarted worker resumes without duplicating completed stages.
5. Research and verification artifacts are exact-hash bound.
6. One injected ordinary failure produces one automatic retry and then succeeds or settles failed.
7. Policy failures do not retry.
8. Proposal completion stops at `awaiting_human` with no later checkpoint created.
9. Paid tools, TopView, assets, generation, render, and publish are never invoked.
10. The mobile dashboard accurately reflects the durable job state and can request a controlled retry.

