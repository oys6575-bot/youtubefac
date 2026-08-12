(() => {
  "use strict";

  const TWO_STEP_GATES = new Set(["budget", "asset_selection", "final_review", "title_thumbnail", "publish"]);
  const ui = {
    title: document.querySelector("#project-title"), projectId: document.querySelector("#project-id"),
    connection: document.querySelector("#connection"), offline: document.querySelector("#offline-notice"),
    error: document.querySelector("#error-notice"), sync: document.querySelector("#last-sync"),
    stageCount: document.querySelector("#stage-count"), progress: document.querySelector("#stage-progress"),
    rail: document.querySelector("#stage-rail"), gateCard: document.querySelector("#gate-card"),
    automationCard: document.querySelector("#automation-card"), automationLabel: document.querySelector("#automation-label"),
    automationDetail: document.querySelector("#automation-detail"), automationActions: document.querySelector("#automation-actions"),
    collectionProgress: document.querySelector("#collection-progress"),
    gateTitle: document.querySelector("#gate-title"), gateDetail: document.querySelector("#gate-detail"),
    gateStage: document.querySelector("#gate-stage"), gateSelection: document.querySelector("#gate-selection"),
    gateActions: document.querySelector("#gate-actions"), topCandidates: document.querySelector("#top-candidates"),
    topicList: document.querySelector("#topic-list"), roles: document.querySelector("#role-list"),
    metrics: document.querySelector("#metrics"), providers: document.querySelector("#provider-list"),
    dialog: document.querySelector("#decision-dialog"), form: document.querySelector("#decision-form"),
    dialogTitle: document.querySelector("#dialog-title"), dialogSummary: document.querySelector("#dialog-summary"),
    dialogImpact: document.querySelector("#dialog-impact"), reasonField: document.querySelector("#reason-field"),
    reason: document.querySelector("#decision-reason"), confirmField: document.querySelector("#confirm-field"),
    confirmInput: document.querySelector("#confirm-input"), submit: document.querySelector("#decision-submit"),
  };

  let dashboard = null;
  let csrfToken = null;
  let selectedCandidate = null;
  let pendingAction = null;
  let projectId = location.pathname.split("/").filter(Boolean)[1] || null;

  function node(tag, className, text) {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text !== undefined && text !== null) item.textContent = String(text);
    return item;
  }

  async function api(path, options = {}) {
    const response = await fetch(path, { credentials: "same-origin", cache: "no-store", ...options });
    let body = null;
    try { body = await response.json(); } catch (_error) { body = {}; }
    if (!response.ok) {
      const error = new Error(body.code || `http_${response.status}`);
      error.status = response.status;
      throw error;
    }
    return body;
  }

  function setConnection() {
    const online = navigator.onLine;
    ui.connection.classList.toggle("offline", !online);
    ui.connection.querySelector("span:last-child").textContent = online ? "Tailscale 연결" : "오프라인";
    ui.offline.classList.toggle("hidden", online);
    document.querySelectorAll("[data-human-action]").forEach(button => { button.disabled = !online; });
    if (!online && ui.dialog.open) ui.dialog.close();
  }

  function showError(message) {
    ui.error.textContent = message;
    ui.error.classList.toggle("hidden", !message);
  }

  function openPanel(name) {
    document.querySelectorAll("[data-panel-view]").forEach(panel => panel.classList.toggle("active", panel.dataset.panelView === name));
    document.querySelectorAll("[data-panel]").forEach(button => button.classList.toggle("active", button.dataset.panel === name));
    scrollTo({ top: 0, behavior: "smooth" });
  }

  function selectCandidate(candidate) {
    selectedCandidate = candidate;
    document.querySelectorAll("[data-candidate-id]").forEach(card => card.classList.toggle("selected", card.dataset.candidateId === candidate.id));
    ui.gateSelection.classList.remove("hidden");
    ui.gateSelection.textContent = `선택: ${candidate.title} · ${candidate.score}점 · 검증 ${candidate.verification}`;
    renderGateActions();
  }

  function candidateCard(candidate, detailed = false) {
    const card = node("button", detailed ? "topic-row" : "candidate-card");
    card.type = "button";
    card.dataset.candidateId = candidate.id;
    if (detailed) {
      card.append(node("span", "topic-rank", `#${candidate.rank}`));
      const identity = node("span");
      identity.append(node("strong", "", candidate.title), node("small", "", `${candidate.location} · ${candidate.collapse_date}`));
      card.append(identity, node("span", "topic-question", candidate.question), node("span", "topic-score", candidate.score), node("span", "topic-verdict", candidate.verification));
    } else {
      const top = node("div", "candidate-top");
      top.append(node("span", "rank", `RANK ${candidate.rank}`), node("span", "score", candidate.score));
      const meta = node("div", "candidate-meta");
      meta.append(node("span", "", candidate.collapse_date), node("span", "pass", `${candidate.verification} · 공식 ${candidate.official_source_count}`));
      card.append(top, node("h3", "", candidate.title), node("p", "", candidate.question), meta);
    }
    card.addEventListener("click", () => selectCandidate(candidate));
    return card;
  }

  function renderStages() {
    ui.rail.replaceChildren();
    const complete = dashboard.metrics.completed_stages;
    ui.stageCount.textContent = `${complete} / ${dashboard.metrics.total_stages} 완료`;
    ui.progress.style.width = `${dashboard.metrics.total_stages ? complete / dashboard.metrics.total_stages * 100 : 0}%`;
    dashboard.stages.forEach(stage => {
      const step = node("div", `stage-step ${stage.status}`);
      step.title = `${stage.name}: ${stage.status}`;
      step.append(node("span", "stage-dot"), node("span", "", stage.name.replaceAll("_", " ")));
      ui.rail.append(step);
    });
  }

  function actionButton(label, action, style = "secondary") {
    const button = node("button", `button ${style}`, label);
    button.type = "button";
    button.dataset.humanAction = action;
    button.disabled = !navigator.onLine;
    button.addEventListener("click", () => openDecision(action));
    return button;
  }

  function renderGateActions() {
    ui.gateActions.replaceChildren();
    const gate = dashboard && dashboard.current_gate;
    if (!gate) return;
    if (gate.stage === "topic_approval") {
      const approve = actionButton("선택한 주제 승인", "approve_topic", "primary");
      approve.disabled = !navigator.onLine || !selectedCandidate || selectedCandidate.verification !== "PASS";
      ui.gateActions.append(approve);
    } else {
      ui.gateActions.append(actionButton("승인", "approve_gate", "primary"));
    }
    ui.gateActions.append(actionButton("수정 요청", "request_revision"), actionButton("거부", "reject_gate", "danger"), actionButton("작업 중지 요청", "request_stop", "danger"));
  }

  function renderGate() {
    const gate = dashboard.current_gate;
    ui.gateSelection.classList.add("hidden");
    if (!gate) {
      ui.gateCard.classList.add("inactive");
      ui.gateTitle.textContent = "승인 대기 없음";
      ui.gateDetail.textContent = "현재 사용자의 결정을 기다리는 단계가 없습니다.";
      ui.gateStage.textContent = "—";
      ui.gateActions.replaceChildren();
      return;
    }
    ui.gateCard.classList.remove("inactive");
    ui.gateTitle.textContent = gate.summary.title;
    ui.gateDetail.textContent = gate.summary.detail;
    ui.gateStage.textContent = gate.stage;
    if (gate.stage === "topic_approval" && selectedCandidate) {
      ui.gateSelection.classList.remove("hidden");
      ui.gateSelection.textContent = `선택: ${selectedCandidate.title} · ${selectedCandidate.score}점 · 검증 ${selectedCandidate.verification}`;
    }
    renderGateActions();
  }

  function elapsedLabel(updatedAt) {
    const started = Date.parse(updatedAt || "");
    if (!Number.isFinite(started)) return "경과시간 계산 중";
    const seconds = Math.max(0, Math.floor((Date.now() - started) / 1000));
    if (seconds < 60) return `${seconds}초 경과`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}분 경과`;
    return `${Math.floor(minutes / 60)}시간 ${minutes % 60}분 경과`;
  }

  function automationActivity(automation) {
    if (automation.state === "queued") return "Coordinator가 작업 시작을 준비 중";
    if (automation.state === "failed") return "자동 실행이 멈춤";
    if (automation.state === "awaiting_human") return "기획안 작성 완료 · 사용자 검토 대기";
    if (automation.state === "completed") return "허용된 자동 작업 완료";
    const activities = {
      research: "공식 출처와 핵심 주장 수집·정리 중",
      media_collection: "사용 가능한 실제 사진·영상·문서 수집 중",
      evidence_lock: "출처 원문과 주장 일치 여부 교차검증 중",
      proposal: "검증된 사실로 구성·영상 기획안 작성 중",
    };
    return activities[automation.current_stage] || "자동 작업 실행 중";
  }

  function renderCollectionProgress(automation) {
    if (!ui.collectionProgress) return;
    const progress = automation.current_stage === "media_collection" ? automation.media_collection : null;
    ui.collectionProgress.replaceChildren();
    ui.collectionProgress.classList.toggle("hidden", !progress);
    if (!progress) return;
    const source = progress.current_source || "소스 준비";
    const state = progress.state === "downloading" ? "다운로드 중" : progress.state === "searching" ? "검색 중" : progress.state;
    const head = node("div", "collection-head");
    head.append(node("strong", "", `${source} · ${state}`), node("span", "", `${Math.round(progress.elapsed_seconds)}초`));
    const counts = node("div", "collection-counts");
    counts.append(
      node("span", "", `발견 ${progress.counts.discovered}`),
      node("span", "", `수집 자료 ${progress.counts.accepted}`),
      node("span", "", `다운로드 ${progress.counts.downloaded}`),
      node("span", "", `권리 제외 ${progress.counts.rejected}`),
      node("span", "", `중복 ${progress.counts.duplicates}`),
    );
    const sourceLine = node("p", "collection-source", `완료 소스 ${progress.sources.completed.length}/${progress.sources.attempted.length}${progress.current_query ? ` · ${progress.current_query}` : ""}`);
    ui.collectionProgress.append(head, counts, sourceLine);
    if (progress.error) ui.collectionProgress.append(node("p", "collection-error", progress.error));
  }

  function renderAutomation() {
    const automation = dashboard.automation;
    if (!ui.automationCard || !ui.automationLabel || !ui.automationDetail || !ui.automationActions) {
      return;
    }
    if (!automation) {
      ui.automationCard.classList.add("hidden");
      ui.automationActions.replaceChildren();
      return;
    }
    const fallbackLabels = {
      queued: "자료조사 시작 대기",
      running: automation.current_stage === "research" ? "자료조사 실행 중" : automation.current_stage === "media_collection" ? "실제 자료 수집 실행 중" : automation.current_stage === "evidence_lock" ? "사실검증 실행 중" : "기획안 작성 중",
      retrying: "자동 작업 재시도 중",
      failed: "실패 · 다시 실행 가능",
      awaiting_human: "기획안 승인 대기",
      completed: "자동 작업 완료",
    };
    ui.automationCard.classList.remove("hidden");
    ui.automationCard.dataset.state = automation.state;
    ui.automationLabel.textContent = automation.label || fallbackLabels[automation.state] || "자동 작업 상태";
    const stageNames = { research: "자료조사", media_collection: "실제 자료 수집", evidence_lock: "사실검증", proposal: "기획안" };
    const completed = automation.completed_stages.length
      ? `완료: ${automation.completed_stages.map(stage => stageNames[stage] || stage).join(" → ")}`
      : "완료 단계 없음";
    const elapsed = ["running", "retrying", "queued"].includes(automation.state)
      ? ` · ${elapsedLabel(automation.updated_at)}`
      : "";
    const error = automation.last_error ? ` · ${automation.last_error.message}` : "";
    ui.automationDetail.textContent = `현재 작업: ${automationActivity(automation)}${elapsed} · ${completed}${error}`;
    renderCollectionProgress(automation);
    ui.automationActions.replaceChildren();
    if (automation.can_retry) {
      ui.automationActions.append(actionButton("다시 실행", "retry_auto_dispatch", "primary"));
    }
  }

  function renderRoles() {
    ui.roles.replaceChildren();
    dashboard.roles.forEach(role => {
      const row = node("div", "role-row");
      const statusLabel = role.status === "assigned_not_checked" ? "미확인" : role.status;
      row.append(node("strong", "", role.role.replaceAll("_", " ")), node("span", "role-runtime", role.runtime), node("span", "role-model", role.model), node("span", "role-status", statusLabel));
      ui.roles.append(row);
    });
  }

  function renderMetrics() {
    ui.metrics.replaceChildren();
    const cost = dashboard.cost || {};
    const metrics = [
      [dashboard.metrics.completed_stages, "완료 단계"],
      [dashboard.metrics.approval_receipts, "승인 기록"],
      [`$${Number(cost.total_spent_usd || 0).toFixed(2)}`, "사용 비용"],
      [dashboard.metrics.renders, "렌더 결과"],
    ];
    metrics.forEach(([value, label]) => { const card = node("div", "metric"); card.append(node("strong", "", value), node("span", "", label)); ui.metrics.append(card); });
  }

  function renderProviders() {
    ui.providers.replaceChildren();
    Object.entries(dashboard.providers).forEach(([name, provider]) => {
      const card = node("article", "provider-card");
      const header = node("header");
      header.append(node("h3", "", name), node("span", provider.status === "connected" ? "pass" : "", provider.status));
      const detail = provider.mode ? `운영 방식: ${provider.mode}` : provider.checked_at ? `마지막 확인: ${new Date(provider.checked_at).toLocaleString("ko-KR")}` : "아직 저장된 연결 점검 결과가 없습니다.";
      card.append(header, node("p", "", detail));
      ui.providers.append(card);
    });
  }

  function render() {
    ui.title.textContent = dashboard.project.title;
    ui.projectId.textContent = `${dashboard.project.project_id} · ${dashboard.project.pipeline_type}`;
    ui.sync.textContent = dashboard.project.last_sync ? `마지막 동기화 ${new Date(dashboard.project.last_sync).toLocaleString("ko-KR")}` : "동기화 기록 없음";
    renderStages(); renderAutomation(); renderGate(); renderRoles(); renderMetrics(); renderProviders();
    ui.topCandidates.replaceChildren(...dashboard.topic_candidates.slice(0, 3).map(item => candidateCard(item)));
    ui.topicList.replaceChildren(...dashboard.topic_candidates.map(item => candidateCard(item, true)));
    setConnection();
  }

  function openDecision(action) {
    const isRetry = action === "retry_auto_dispatch";
    if (!navigator.onLine || (!isRetry && !dashboard.current_gate)) return;
    if (isRetry && !(dashboard.automation && dashboard.automation.can_retry)) return;
    const gate = dashboard.current_gate;
    if (action === "approve_topic" && !selectedCandidate) return;
    pendingAction = action;
    const needsReason = ["reject_gate", "request_revision", "request_stop", "retry_auto_dispatch"].includes(action);
    const needsTypedConfirmation = !isRetry && TWO_STEP_GATES.has(gate.stage) && ["approve_gate", "approve_topic"].includes(action);
    const labels = { approve_topic: "주제 선택 승인", approve_gate: "Human Gate 승인", reject_gate: "Gate 거부", request_revision: "수정 요청", request_stop: "작업 중지 요청", retry_auto_dispatch: "자동 작업 다시 실행" };
    ui.dialogTitle.textContent = labels[action];
    ui.dialogSummary.textContent = isRetry ? `${dashboard.automation.current_stage} 단계부터 새 작업 기록으로 다시 실행합니다.` : selectedCandidate && action === "approve_topic" ? `${selectedCandidate.title}을 다음 제작 주제로 승인합니다.` : gate.summary.title;
    ui.dialogImpact.textContent = action.startsWith("approve") ? "이 결정은 다음 단계 실행을 허용하는 기록입니다. 유료 호출이나 게시를 즉시 실행하지 않습니다." : isRetry ? "기존 실패 기록은 그대로 보존하고, 허용된 단계만 새 작업으로 다시 실행합니다." : "이 요청은 Coordinator가 확인할 작업 기록으로 남습니다. 임의 명령을 실행하지 않습니다.";
    ui.reasonField.classList.toggle("hidden", !needsReason);
    ui.confirmField.classList.toggle("hidden", !needsTypedConfirmation);
    ui.reason.value = ""; ui.confirmInput.value = "";
    ui.submit.textContent = isRetry ? "다시 실행 기록" : action.startsWith("approve") ? "승인 기록" : "요청 기록";
    ui.dialog.showModal();
  }

  function closeDecision() {
    pendingAction = null;
    ui.dialog.close();
  }

  async function submitDecision(event) {
    event.preventDefault();
    const isRetry = pendingAction === "retry_auto_dispatch";
    if (!pendingAction || (!isRetry && !dashboard.current_gate) || !navigator.onLine) return;
    const gate = dashboard.current_gate;
    const needsReason = ["reject_gate", "request_revision", "request_stop", "retry_auto_dispatch"].includes(pendingAction);
    const needsTypedConfirmation = !isRetry && TWO_STEP_GATES.has(gate.stage) && ["approve_gate", "approve_topic"].includes(pendingAction);
    if (needsReason && !ui.reason.value.trim()) { ui.reason.focus(); return; }
    if (needsTypedConfirmation && ui.confirmInput.value !== "CONFIRM") { ui.confirmInput.focus(); return; }
    const body = isRetry ? {
      action: pendingAction,
      project_id: dashboard.project.project_id,
      retry_job_id: dashboard.automation.job_id,
      expected_job_sha256: dashboard.automation.job_sha256,
      idempotency_key: crypto.randomUUID(),
      reason: ui.reason.value.trim(),
    } : {
      action: pendingAction,
      project_id: dashboard.project.project_id,
      stage: gate.stage,
      expected_checkpoint_sha256: gate.checkpoint_sha256,
      idempotency_key: crypto.randomUUID(),
    };
    if (pendingAction === "approve_topic") body.selected_candidate_id = selectedCandidate.id;
    if (needsReason) body.reason = ui.reason.value.trim();
    if (needsTypedConfirmation) body.confirmation = "CONFIRM";
    ui.submit.disabled = true;
    try {
      await api(`/api/mobile/project/${encodeURIComponent(dashboard.project.project_id)}/actions`, {
        method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken }, body: JSON.stringify(body),
      });
      ui.dialog.close(); selectedCandidate = null; await loadDashboard();
    } catch (error) {
      if (error.status === 409) { showError("상태가 바뀌었습니다. 최신 화면을 다시 불러왔습니다."); await loadDashboard(); }
      else showError(`결정을 기록하지 못했습니다: ${error.message}`);
    } finally { ui.submit.disabled = false; }
  }

  async function loadDashboard() {
    if (!navigator.onLine || !projectId) return;
    dashboard = await api(`/api/mobile/project/${encodeURIComponent(projectId)}/dashboard`);
    render();
  }

  function refreshAutomationClock() {
    if (dashboard && dashboard.automation) renderAutomation();
  }

  async function start() {
    setConnection();
    if (!navigator.onLine) return;
    try {
      const session = await api("/api/mobile/session");
      csrfToken = session.csrf_token;
      if (!projectId) {
        const projects = await api("/api/mobile/projects");
        if (!projects.length) throw new Error("표시할 프로젝트가 없습니다");
        projectId = projects[0].project_id;
        history.replaceState(null, "", `/mobile/${encodeURIComponent(projectId)}`);
      }
      await loadDashboard();
      const events = new EventSource(`/api/mobile/project/${encodeURIComponent(projectId)}/events`);
      events.onmessage = event => { try { if (JSON.parse(event.data).type === "change") loadDashboard(); } catch (_error) {} };
      events.onerror = () => setConnection();
    } catch (error) { showError(`대시보드를 열 수 없습니다: ${error.message}`); }
  }

  document.querySelectorAll("[data-panel]").forEach(button => button.addEventListener("click", () => openPanel(button.dataset.panel)));
  document.querySelectorAll("[data-open-panel]").forEach(button => button.addEventListener("click", () => openPanel(button.dataset.openPanel)));
  document.querySelectorAll("[data-dialog-close]").forEach(button => button.addEventListener("click", closeDecision));
  ui.form.addEventListener("submit", submitDecision);
  addEventListener("online", () => { setConnection(); start(); });
  addEventListener("offline", setConnection);
  setInterval(refreshAutomationClock, 30000);
  if ("serviceWorker" in navigator) {
    let reloadingForWorker = false;
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (reloadingForWorker) return;
      reloadingForWorker = true;
      location.reload();
    });
    navigator.serviceWorker.register("/sw.js", { scope: "/" });
  }
  start();
})();
