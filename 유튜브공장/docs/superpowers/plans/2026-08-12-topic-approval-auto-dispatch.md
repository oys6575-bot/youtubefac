# Topic Approval Auto-Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make one authenticated topic approval durably start research, independent evidence verification, and proposal authoring, then stop at the proposal Human Gate.

**Architecture:** Extend the existing crash-recoverable approval transaction with a validated outbox job. A dedicated LaunchAgent worker claims jobs from canonical project storage and drives sequential Orca tasks through an injected command adapter. The dashboard remains a read-only projection plus allowlisted approval/retry actions.

**Tech Stack:** Python 3.11, JSON Schema Draft 2020-12, FastAPI, pytest, launchd, Orca CLI orchestration, vanilla JavaScript/CSS.

## Global Constraints

- Automatic stages are exactly `research`, `evidence_lock`, and `proposal`.
- Maximum automatic retries per stage is exactly `1`.
- The proposal checkpoint must stop at `awaiting_human` with `human_approved: false`.
- No paid API, TopView dispatch, asset generation, script generation, visual-plan generation, render, upload, or publish.
- TopView remains `manual_semi_automatic`, `api_enabled: false`, and `automatic_dispatch: false`.
- No silent provider/model fallback and no fabricated Human Gate approval.
- Canonical project state remains under `OPENMONTAGE_PROJECTS_DIR`.

---

### Task 1: Lock the safe automatic stage policy

**Files:**
- Modify: `config/orca-model-routing.yaml`
- Modify: `schemas/orchestration/orca-model-routing.schema.json`
- Modify: `lib/orca_model_routing.py`
- Modify: `pipeline_defs/youtube-factory.yaml`
- Modify: `tests/contracts/test_orca_model_routing.py`
- Modify: `tests/contracts/test_youtube_factory_pipeline.py`

**Interfaces:**
- Consumes: existing strict routing and pipeline validators.
- Produces: `routing["auto_dispatch"]` with `enabled`, `trigger_action`, `stages`, `max_retries`, and `stop_gate`; machine-gated `evidence_lock`.

- [ ] **Step 1: Write failing policy tests**

```python
def test_safe_auto_dispatch_is_exact_and_topview_remains_manual():
    routing = load_routing()
    assert routing["auto_dispatch"] == {
        "enabled": True,
        "trigger_action": "approve_topic",
        "stages": ["research", "evidence_lock", "proposal"],
        "max_retries": 1,
        "stop_gate": "proposal",
    }
    assert routing["topview"]["automatic_dispatch"] is False

def test_evidence_lock_is_machine_gate_and_proposal_is_human_gate():
    stages = {s["name"]: s for s in load_pipeline("youtube-factory")["stages"]}
    assert stages["evidence_lock"]["human_approval_default"] is False
    assert stages["proposal"]["human_approval_default"] is True
```

- [ ] **Step 2: Run tests and confirm failure on missing `auto_dispatch` and human-gated evidence lock**

Run: `.venv/bin/python -m pytest tests/contracts/test_orca_model_routing.py tests/contracts/test_youtube_factory_pipeline.py -q`

- [ ] **Step 3: Add the exact schema/config invariants and change only `evidence_lock` gating**

Implement `EXPECTED_AUTO_DISPATCH` in `lib/orca_model_routing.py`; reject any stage, retry count, stop gate, or trigger drift. Update the routing schema required list and set `control_plane.pilot_stop_gate` to `proposal`. Change the pipeline evidence-lock success criterion from Human Gate approval to independent PASS.

- [ ] **Step 4: Run the two contract files and confirm all pass**

Run: `.venv/bin/python -m pytest tests/contracts/test_orca_model_routing.py tests/contracts/test_youtube_factory_pipeline.py -q`

- [ ] **Step 5: Commit**

```bash
git add config/orca-model-routing.yaml schemas/orchestration/orca-model-routing.schema.json lib/orca_model_routing.py pipeline_defs/youtube-factory.yaml tests/contracts/test_orca_model_routing.py tests/contracts/test_youtube_factory_pipeline.py
git commit -m "feat: lock safe topic auto dispatch policy"
```

### Task 2: Add the transactional outbox job

**Files:**
- Create: `schemas/mobile-dashboard/auto-dispatch-job.schema.json`
- Create: `backlot/auto_dispatch.py`
- Modify: `backlot/mobile_actions.py`
- Create: `tests/backlot/test_auto_dispatch_jobs.py`
- Modify: `tests/backlot/test_mobile_action_transaction.py`

**Interfaces:**
- Consumes: approval receipt ID, canonical `topic_selection`, resulting topic checkpoint SHA-256.
- Produces: `build_topic_job(project, receipt, resulting_checkpoint_sha256, now) -> dict`, `load_job(path) -> dict`, `write_job_state(path, expected_state, updates) -> dict`.

- [ ] **Step 1: Write failing job and transaction tests**

```python
def test_topic_approval_atomically_creates_one_queued_job(tmp_path):
    project, candidate, expected = build_topic_gate(tmp_path)
    result = execute_action(tmp_path, payload(candidate, expected), ACTOR)
    jobs = list((project / "automation/jobs").glob("*.json"))
    assert len(jobs) == 1
    job = json.loads(jobs[0].read_text())
    assert job["job_id"] == result.receipt["receipt_id"]
    assert job["state"] == "queued"
    assert job["current_stage"] == "research"
    assert job["max_retries"] == 1

def test_idempotent_replay_creates_no_second_job(tmp_path):
    project, candidate, expected = build_topic_gate(tmp_path)
    action = payload(candidate, expected)
    first = execute_action(tmp_path, action, ACTOR)
    second = execute_action(tmp_path, action, ACTOR)
    assert second.replayed is True
    assert first.receipt == second.receipt
    assert len(list((project / "automation/jobs").glob("*.json"))) == 1
```

Add failpoint coverage proving recovery applies checkpoint, receipt, idempotency index, and job exactly once.

- [ ] **Step 2: Run tests and confirm failure because no job schema/module/target exists**

Run: `.venv/bin/python -m pytest tests/backlot/test_auto_dispatch_jobs.py tests/backlot/test_mobile_action_transaction.py -q`

- [ ] **Step 3: Implement the schema and immutable job builder**

The schema rejects commands, arbitrary paths, provider/model overrides, stages outside the allowlist, `max_retries` other than `1`, and unknown properties. `build_topic_job` derives every field server-side from the validated receipt and canonical topic selection.

- [ ] **Step 4: Append the job bytes to the existing approval prepared journal only for `approve_topic`**

The job target is `automation/jobs/<receipt_id>.json`. It is part of the same `targets` array as checkpoint, receipt, and idempotency index. Replayed requests return before creating any target.

- [ ] **Step 5: Run transaction tests and confirm pass**

Run: `.venv/bin/python -m pytest tests/backlot/test_auto_dispatch_jobs.py tests/backlot/test_mobile_action_transaction.py tests/backlot/test_mobile_actions.py -q`

- [ ] **Step 6: Commit**

```bash
git add schemas/mobile-dashboard/auto-dispatch-job.schema.json backlot/auto_dispatch.py backlot/mobile_actions.py tests/backlot/test_auto_dispatch_jobs.py tests/backlot/test_mobile_action_transaction.py
git commit -m "feat: enqueue topic work with approval transaction"
```

### Task 3: Implement the durable Coordinator state machine

**Files:**
- Create: `backlot/orca_auto_dispatch.py`
- Create: `backlot/auto_dispatch_worker.py`
- Create: `scripts/mobile-dashboard-coordinator.py`
- Create: `tests/backlot/test_auto_dispatch_worker.py`

**Interfaces:**
- Consumes: queued job files and `OrcaRunner.run_stage(project, job, stage) -> StageResult`.
- Produces: `Coordinator.process_next() -> bool`, durable transitions, Orca Run/Task/Dispatch IDs, and exact stage artifact bindings.
- `StageResult`: `outcome`, `artifact_paths`, `artifact_sha256`, `source_commit`, `verdict`, `run_id`, `task_id`, `dispatch_id`, `error`.
- Test helpers in `tests/backlot/test_auto_dispatch_worker.py`: `project_with_job` creates a validated queued job; `success(stage)` returns a settled `StageResult` with real fixture files and matching hashes; `ordinary_failure(stage)` and `policy_failure(stage)` return typed failures; `FakeRunner(results)` records stage calls and returns results in order.

- [ ] **Step 1: Write failing state-machine tests with a real filesystem and injected fake runner**

```python
def test_worker_runs_three_stages_and_stops_at_proposal_gate(project_with_job):
    runner = FakeRunner([success("research"), success("evidence_lock"), success("proposal")])
    Coordinator(project_with_job.parent, runner).process_next()
    job = read_job(project_with_job)
    assert job["state"] == "awaiting_human"
    assert [r["stage"] for r in job["stage_results"]] == ["research", "evidence_lock", "proposal"]
    assert not (project_with_job / "checkpoint_script.json").exists()

def test_worker_retries_one_ordinary_failure_only(project_with_job):
    runner = FakeRunner([ordinary_failure("research"), success("research"), success("evidence_lock"), success("proposal")])
    Coordinator(project_with_job.parent, runner).process_next()
    assert runner.calls.count("research") == 2

def test_policy_failure_is_not_retried(project_with_job):
    runner = FakeRunner([policy_failure("research")])
    Coordinator(project_with_job.parent, runner).process_next()
    assert runner.calls == ["research"]
    assert read_job(project_with_job)["state"] == "failed"
```

Add restart recovery coverage: a settled stage result with matching hashes is skipped, while a missing or mismatched artifact fails closed.

- [ ] **Step 2: Run worker tests and confirm import/function failures**

Run: `.venv/bin/python -m pytest tests/backlot/test_auto_dispatch_worker.py -q`

- [ ] **Step 3: Implement the state machine with per-project locking and atomic transitions**

`process_next` claims the oldest queued/retrying job, validates trigger receipt/checkpoint/topic selection, advances only through the exact allowlist, records attempt before dispatch, validates every returned artifact hash, and settles `awaiting_human` after proposal.

- [ ] **Step 4: Implement `OrcaRunner` as a typed subprocess adapter**

For every job it creates one Run using `orca orchestration run-create --objective "Auto production after topic approval: <project_id>:<job_id>" --json`, creates one sequential Task per stage, and launches a fresh agent terminal in the registered main worktree. Research uses Hermes through `orca terminal create --command hermes` plus injected dispatch; evidence lock uses Codex `gpt-5.6-sol` high; proposal uses Claude with the configured model/effort. It waits only on `worker_done`, `escalation`, and `question`, releases settled workers, and stores all Run/Task/Dispatch IDs. Command construction is argument-array only and accepts no client-supplied fragments.

- [ ] **Step 5: Implement the long-running script**

`scripts/mobile-dashboard-coordinator.py` accepts `--projects`, `--routing`, `--poll-seconds` (default `2`), and `--once`. It exits nonzero on invalid configuration, logs structured job transitions, and continues polling after a settled job failure.

- [ ] **Step 6: Run worker tests and a dry-run `--once` against an empty temporary projects root**

Run: `.venv/bin/python -m pytest tests/backlot/test_auto_dispatch_worker.py -q`

Run: `.venv/bin/python scripts/mobile-dashboard-coordinator.py --projects "$(mktemp -d)" --once`

- [ ] **Step 7: Commit**

```bash
git add backlot/orca_auto_dispatch.py backlot/auto_dispatch_worker.py scripts/mobile-dashboard-coordinator.py tests/backlot/test_auto_dispatch_worker.py
git commit -m "feat: coordinate approved topic work through Orca"
```

### Task 4: Project automation state onto the mobile dashboard

**Files:**
- Modify: `backlot/mobile_state.py`
- Modify: `backlot/ui/mobile.html`
- Modify: `backlot/ui/mobile.js`
- Modify: `backlot/ui/mobile.css`
- Modify: `schemas/mobile-dashboard/action.schema.json`
- Modify: `backlot/mobile_actions.py`
- Modify: `tests/backlot/test_mobile_state.py`
- Modify: `tests/contracts/test_mobile_dashboard_contract.py`
- Modify: `tests/backlot/test_mobile_actions.py`

**Interfaces:**
- Consumes: newest validated job in `automation/jobs/`.
- Produces: dashboard `automation` object and allowlisted `retry_auto_dispatch` action.

- [ ] **Step 1: Write failing projection and retry tests**

```python
def test_mobile_state_projects_durable_automation_status(project_with_job):
    state = build_mobile_state(project_with_job)
    assert state["automation"]["state"] == "running"
    assert state["automation"]["current_stage"] == "research"
    assert state["automation"]["attempt"] == 0

def test_retry_requires_failed_job_and_creates_retry_receipt(project_with_failed_job):
    failed_job = read_job(project_with_failed_job)
    retry_payload = {
        "action": "retry_auto_dispatch",
        "project_id": project_with_failed_job.name,
        "stage": "auto_dispatch",
        "failed_job_id": failed_job["job_id"],
        "expected_job_sha256": sha256_job(project_with_failed_job),
        "idempotency_key": "retry-auto-dispatch-0001",
    }
    result = execute_action(project_with_failed_job.parent, retry_payload, ACTOR)
    assert result.receipt["action"] == "retry_auto_dispatch"
    assert read_job(project_with_failed_job)["state"] == "queued"
```

- [ ] **Step 2: Run focused tests and confirm missing automation field/action failures**

Run: `.venv/bin/python -m pytest tests/backlot/test_mobile_state.py tests/backlot/test_mobile_actions.py tests/contracts/test_mobile_dashboard_contract.py -q`

- [ ] **Step 3: Add the bounded read-only automation projection**

Only expose state, stage, attempt, timestamps, a concise sanitized error code/message, and whether retry is allowed. Never expose command arguments, environment, terminal transcripts, or secrets.

- [ ] **Step 4: Render the automation card and retry action**

Show Korean labels for queued/running/retrying/awaiting-human/failed. `다시 실행` opens the existing decision dialog and posts only the allowlisted retry action with the failed job ID and current job SHA-256.

- [ ] **Step 5: Implement transactional retry**

Server-side validation requires the exact failed job, zero active job for the project, matching job SHA-256, and no policy failure. The action writes a retry receipt plus a new queued job referencing the original job; it never mutates original history.

- [ ] **Step 6: Run focused mobile tests and confirm pass**

Run: `.venv/bin/python -m pytest tests/backlot/test_mobile_state.py tests/backlot/test_mobile_actions.py tests/backlot/test_mobile_api.py tests/contracts/test_mobile_dashboard_contract.py -q`

- [ ] **Step 7: Commit**

```bash
git add backlot/mobile_state.py backlot/ui/mobile.html backlot/ui/mobile.js backlot/ui/mobile.css schemas/mobile-dashboard/action.schema.json backlot/mobile_actions.py tests/backlot/test_mobile_state.py tests/contracts/test_mobile_dashboard_contract.py tests/backlot/test_mobile_actions.py
git commit -m "feat: show and retry automatic production stages"
```

### Task 5: Install and audit the Coordinator service

**Files:**
- Modify: `scripts/install-mobile-dashboard-services.py`
- Modify: `scripts/mobile-dashboard-preflight.py`
- Modify: `tests/contracts/test_mobile_dashboard_operations.py`

**Interfaces:**
- Consumes: coordinator script, canonical projects path, routing config, Orca CLI path.
- Produces: `com.mk.youtube-factory.coordinator` LaunchAgent and preflight status.

- [ ] **Step 1: Write failing service and preflight tests**

```python
def test_installer_defines_dedicated_coordinator_service():
    plists = load_installer().service_plists()
    worker = plists["com.mk.youtube-factory.coordinator"]
    assert "mobile-dashboard-coordinator.py" in " ".join(worker["ProgramArguments"])
    assert worker["EnvironmentVariables"]["OPENMONTAGE_PROJECTS_DIR"].endswith("/projects")
    assert worker["KeepAlive"] is True
```

Add a preflight unit proving missing/unhealthy coordinator state makes readiness fail while leaving the dashboard and Tailscale checks unchanged.

- [ ] **Step 2: Run operations tests and confirm missing service failures**

Run: `.venv/bin/python -m pytest tests/contracts/test_mobile_dashboard_operations.py -q`

- [ ] **Step 3: Add the third isolated LaunchAgent**

Use the repository venv, loop-free argument arrays, explicit `PYTHONPATH`, canonical projects/routing paths, separate stdout/stderr logs, and no network listener. Install/remove it with the existing two services.

- [ ] **Step 4: Extend preflight with a read-only coordinator health check**

The worker writes `.runtime/mobile-dashboard/coordinator-health.json` atomically with PID, timestamp, queue counts, and last settled job. Preflight requires a live PID and health timestamp no older than 30 seconds.

- [ ] **Step 5: Run operations tests and confirm pass**

Run: `.venv/bin/python -m pytest tests/contracts/test_mobile_dashboard_operations.py -q`

- [ ] **Step 6: Commit**

```bash
git add scripts/install-mobile-dashboard-services.py scripts/mobile-dashboard-preflight.py tests/contracts/test_mobile_dashboard_operations.py
git commit -m "feat: supervise the mobile production coordinator"
```

### Task 6: Fault-injection verification and activation

**Files:**
- Create: `tests/backlot/test_auto_dispatch_integration.py`
- Modify: `docs/operations/mobile-dashboard.md`

**Interfaces:**
- Consumes: complete job, worker, dashboard, and service contracts.
- Produces: verified local service installation and a safe pending Human Gate.

- [ ] **Step 1: Add an end-to-end test with a fake Orca adapter**

The test must approve a fixture topic through `execute_action`, restart the Coordinator between research and evidence lock, inject one ordinary verification failure, complete on retry, project the dashboard status, and assert proposal is `awaiting_human` with no script/assets/render/publish checkpoint.

- [ ] **Step 2: Run all affected tests**

Run: `.venv/bin/python -m pytest tests/backlot/test_auto_dispatch_jobs.py tests/backlot/test_auto_dispatch_worker.py tests/backlot/test_auto_dispatch_integration.py tests/backlot/test_mobile_action_transaction.py tests/backlot/test_mobile_actions.py tests/backlot/test_mobile_api.py tests/backlot/test_mobile_state.py tests/contracts/test_mobile_dashboard_contract.py tests/contracts/test_mobile_dashboard_operations.py tests/contracts/test_orca_model_routing.py tests/contracts/test_youtube_factory_pipeline.py -q`

- [ ] **Step 3: Install/reload all three LaunchAgents**

Run: `.venv/bin/python scripts/install-mobile-dashboard-services.py --install`

- [ ] **Step 4: Run operational preflight and verify dashboard remains private**

Run: `.venv/bin/python scripts/mobile-dashboard-preflight.py`

Expected: loopback listener PASS, gateway health PASS, Tailscale backend Running, cached TLS certificate PASS, private Serve PASS, Coordinator health PASS.

- [ ] **Step 5: Verify current canonical pilot remains unapproved and no job was created retroactively**

```bash
jq '{status,human_approved}' projects/collapse-topic-pilot-2026-08-12/checkpoint_topic_approval.json
find projects/collapse-topic-pilot-2026-08-12/automation/jobs -type f 2>/dev/null | wc -l
```

Expected: `status=awaiting_human`, `human_approved=false`, job count `0`. The first job is created only by the user's next explicit topic approval.

- [ ] **Step 6: Commit**

```bash
git add tests/backlot/test_auto_dispatch_integration.py docs/operations/mobile-dashboard.md
git commit -m "test: verify topic approval automatic production handoff"
```

- [ ] **Step 7: Final verification**

Run: `git diff --check && git status --short && .venv/bin/python -m pytest tests/backlot tests/contracts -q`
