(() => {
  "use strict";

  const TWO_STEP_GATES = new Set(["budget", "asset_selection", "final_review", "title_thumbnail", "publish"]);
  const STAGE_NAMES = {
    topic_search: "주제 검색", topic_verification: "주제 검증", topic_approval: "주제 승인",
    research: "자료 조사", media_collection: "자료 수집", evidence_lock: "사실 검증",
    proposal: "구성", script: "대본", visual_plan: "영상 설계", animatic: "애니매틱",
    budget: "예산", assets: "에셋 제작", asset_selection: "에셋 선택", edit: "편집",
    compose: "영상 조립", final_review: "검수", package: "최종본", title_thumbnail: "제목·썸네일", publish: "게시",
  };
  const ui = {
    title: document.querySelector("#project-title"), projectId: document.querySelector("#project-id"),
    connection: document.querySelector("#connection"), offline: document.querySelector("#offline-notice"), error: document.querySelector("#error-notice"), sync: document.querySelector("#last-sync"),
    currentWorkCard: document.querySelector("#current-work-card"), currentWorkStatus: document.querySelector("#current-work-status"), currentWorkTitle: document.querySelector("#current-work-title"), currentWorkDetail: document.querySelector("#current-work-detail"),
    stageCount: document.querySelector("#stage-count"), progress: document.querySelector("#stage-progress"), rail: document.querySelector("#stage-rail"),
    automationCard: document.querySelector("#automation-card"), automationLabel: document.querySelector("#automation-label"), automationDetail: document.querySelector("#automation-detail"), automationActions: document.querySelector("#automation-actions"), collectionProgress: document.querySelector("#collection-progress"),
    gateCard: document.querySelector("#gate-card"), gateTitle: document.querySelector("#gate-title"), gateDetail: document.querySelector("#gate-detail"), gateStage: document.querySelector("#gate-stage"), gateSelection: document.querySelector("#gate-selection"), gateActions: document.querySelector("#gate-actions"),
    statusAssetCount: document.querySelector("#status-asset-count"), statusScriptState: document.querySelector("#status-script-state"), statusEditState: document.querySelector("#status-edit-state"),
    topicList: document.querySelector("#topic-list"), scriptTitle: document.querySelector("#script-title"), scriptDuration: document.querySelector("#script-duration"), scriptSections: document.querySelector("#script-sections"), visualPrompts: document.querySelector("#visual-prompts"),
    assetGrid: document.querySelector("#asset-grid"), assetCount: document.querySelector("#asset-count"), assetTotal: document.querySelector("#asset-total"), assetImages: document.querySelector("#asset-images"), assetVideos: document.querySelector("#asset-videos"), assetAudio: document.querySelector("#asset-audio"),
    editStatus: document.querySelector("#edit-status"), editOverview: document.querySelector("#edit-overview"), editGaps: document.querySelector("#edit-gaps"), editCuts: document.querySelector("#edit-cuts"),
    reviewStatus: document.querySelector("#review-status"), reviewPlayer: document.querySelector("#review-player"), reviewEmpty: document.querySelector("#review-empty"), reviewFindings: document.querySelector("#review-findings"), reviewActions: document.querySelector("#review-actions"),
    finalStatus: document.querySelector("#final-status"), finalPlayer: document.querySelector("#final-player"), finalEmpty: document.querySelector("#final-empty"), finalMeta: document.querySelector("#final-meta"), finalDownload: document.querySelector("#final-download"),
    mediaDialog: document.querySelector("#media-dialog"), mediaStage: document.querySelector("#media-stage"), mediaTitle: document.querySelector("#media-title"), mediaMeta: document.querySelector("#media-meta"),
    dialog: document.querySelector("#decision-dialog"), form: document.querySelector("#decision-form"), dialogTitle: document.querySelector("#dialog-title"), dialogSummary: document.querySelector("#dialog-summary"), dialogImpact: document.querySelector("#dialog-impact"), reasonField: document.querySelector("#reason-field"), reason: document.querySelector("#decision-reason"), confirmField: document.querySelector("#confirm-field"), confirmInput: document.querySelector("#confirm-input"), submit: document.querySelector("#decision-submit"),
  };

  let dashboard = null;
  let csrfToken = null;
  let selectedCandidate = null;
  let pendingAction = null;
  let assetFilter = "all";
  let projectId = location.pathname.split("/").filter(Boolean)[1] || null;

  function node(tag, className, text) {
    const item = document.createElement(tag);
    if (className) item.className = className;
    if (text !== undefined && text !== null) item.textContent = String(text);
    return item;
  }

  async function api(path, options = {}) {
    const response = await fetch(path, { credentials: "same-origin", cache: "no-store", ...options });
    let body = {};
    try { body = await response.json(); } catch (_error) {}
    if (!response.ok) { const error = new Error(body.code || `http_${response.status}`); error.status = response.status; throw error; }
    return body;
  }

  function showError(message) { ui.error.textContent = message || ""; ui.error.classList.toggle("hidden", !message); }

  function setConnection() {
    const online = navigator.onLine;
    ui.connection.classList.toggle("offline", !online);
    ui.connection.querySelector("span:last-child").textContent = online ? "Tailscale 연결" : "오프라인";
    ui.offline.classList.toggle("hidden", online);
    document.querySelectorAll("[data-human-action]").forEach(button => { button.disabled = !online; });
    if (!online && ui.dialog.open) ui.dialog.close();
  }

  function openPanel(name) {
    document.querySelectorAll("[data-panel-view]").forEach(panel => panel.classList.toggle("active", panel.dataset.panelView === name));
    document.querySelectorAll("[data-panel]").forEach(button => button.classList.toggle("active", button.dataset.panel === name));
    scrollTo({ top: 0, behavior: "smooth" });
  }

  function actionButton(label, action, style = "secondary") {
    const button = node("button", `button ${style}`, label);
    button.type = "button";
    button.dataset.humanAction = action;
    button.disabled = !navigator.onLine;
    button.addEventListener("click", () => openDecision(action));
    return button;
  }

  function candidateCard(candidate) {
    const card = node("button", "topic-row");
    card.type = "button";
    card.dataset.candidateId = candidate.id;
    const identity = node("span", "topic-identity");
    identity.append(node("strong", "", candidate.title), node("small", "", `${candidate.location || ""} · ${candidate.collapse_date || ""}`));
    card.append(node("span", "topic-rank", `#${candidate.rank}`), identity, node("span", "topic-question", candidate.question), node("span", "topic-score", candidate.score), node("span", "topic-verdict", candidate.verification));
    card.addEventListener("click", () => {
      selectedCandidate = candidate;
      document.querySelectorAll("[data-candidate-id]").forEach(item => item.classList.toggle("selected", item.dataset.candidateId === candidate.id));
      renderGate();
    });
    return card;
  }

  function renderCurrentWork() {
    const work = dashboard.current_work || {};
    ui.currentWorkCard.dataset.state = work.status || "idle";
    ui.currentWorkStatus.textContent = work.status === "in_progress" || work.status === "running" ? "진행 중" : work.status === "awaiting_human" ? "확인 대기" : work.status === "failed" ? "작업 중단" : "대기";
    ui.currentWorkTitle.textContent = work.title || "현재 작업 대기";
    ui.currentWorkDetail.textContent = work.detail || "다음 제작 단계가 시작되면 여기에 표시됩니다.";
  }

  function renderStages() {
    ui.rail.replaceChildren();
    const complete = dashboard.metrics.completed_stages;
    ui.stageCount.textContent = `${complete} / ${dashboard.metrics.total_stages} 완료`;
    ui.progress.style.width = `${dashboard.metrics.total_stages ? complete / dashboard.metrics.total_stages * 100 : 0}%`;
    dashboard.stages.forEach(stage => {
      const step = node("div", `stage-step ${stage.status}`);
      step.append(node("span", "stage-dot"), node("span", "", STAGE_NAMES[stage.name] || stage.name));
      ui.rail.append(step);
    });
  }

  function elapsedLabel(updatedAt) {
    const started = Date.parse(updatedAt || "");
    if (!Number.isFinite(started)) return "경과시간 계산 중";
    const seconds = Math.max(0, Math.floor((Date.now() - started) / 1000));
    if (seconds < 60) return `${seconds}초 경과`;
    const minutes = Math.floor(seconds / 60);
    return minutes < 60 ? `${minutes}분 경과` : `${Math.floor(minutes / 60)}시간 ${minutes % 60}분 경과`;
  }

  function automationActivity(automation) {
    const activeStage = automation.active_stage || automation.current_stage;
    if (activeStage === "media_collection" && automation.media_collection && ["searching", "downloading"].includes(automation.media_collection.state)) return "사용 가능한 실제 사진·영상·문서 수집 중";
    if (automation.state === "queued") return "Coordinator가 작업 시작을 준비 중";
    if (automation.state === "failed") return "자동 실행이 멈춤";
    if (automation.state === "awaiting_human") return "기획안 작성 완료 · 사용자 검토 대기";
    if (automation.state === "completed") return "허용된 자동 작업 완료";
    return ({ research: "공식 출처와 핵심 주장 수집·정리 중", media_collection: "실제 자료 수집 실행 중", evidence_lock: "출처 원문과 주장 일치 여부 교차검증 중", proposal: "검증된 사실로 구성·영상 기획안 작성 중" })[activeStage] || "자동 작업 실행 중";
  }

  function renderCollectionProgress(automation) {
    const progress = (automation.active_stage || automation.current_stage) === "media_collection" ? automation.media_collection : null;
    ui.collectionProgress.replaceChildren();
    ui.collectionProgress.classList.toggle("hidden", !progress);
    if (!progress) return;
    const head = node("div", "collection-head");
    head.append(node("strong", "", `${progress.current_source || "소스 준비"} · ${progress.state === "downloading" ? "다운로드 중" : "검색 중"}`), node("span", "", `${Math.round(progress.elapsed_seconds)}초`));
    const counts = node("div", "collection-counts");
    counts.append(node("span", "", `발견 ${progress.counts.discovered}`), node("span", "", `수집 자료 ${progress.counts.accepted}`), node("span", "", `다운로드 ${progress.counts.downloaded}`), node("span", "", `권리 제외 ${progress.counts.rejected}`));
    ui.collectionProgress.append(head, counts);
  }

  function renderAutomation() {
    const automation = dashboard.automation;
    if (!ui.automationCard || !ui.automationLabel || !ui.automationDetail || !ui.automationActions) return;
    if (!automation || !["queued", "running", "retrying", "failed"].includes(automation.state)) { ui.automationCard.classList.add("hidden"); return; }
    ui.automationCard.classList.remove("hidden");
    ui.automationCard.dataset.state = automation.state;
    const fallbackLabels = {
      queued: "자료조사 시작 대기",
      running: automation.current_stage === "research" ? "자료조사 실행 중" : automation.current_stage === "media_collection" ? "실제 자료 수집 실행 중" : "자동 작업 실행 중",
      retrying: "자동 작업 재시도 중",
      failed: "자동 작업 중단",
    };
    ui.automationLabel.textContent = automation.label || fallbackLabels[automation.state] || "자동 작업 상태";
    ui.automationDetail.textContent = `현재 작업: ${automationActivity(automation)} · ${elapsedLabel(automation.updated_at)}`;
    renderCollectionProgress(automation);
    ui.automationActions.replaceChildren();
    if (automation.can_retry) ui.automationActions.append(actionButton("다시 실행", "retry_auto_dispatch", "primary"));
  }

  function renderGateActions() {
    ui.gateActions.replaceChildren();
    const gate = dashboard.current_gate;
    if (!gate) return;
    if (gate.stage === "topic_approval") {
      const approve = actionButton("선택한 주제 승인", "approve_topic", "primary");
      approve.disabled = !navigator.onLine || !selectedCandidate || selectedCandidate.verification !== "PASS";
      ui.gateActions.append(approve);
    } else ui.gateActions.append(actionButton("승인", "approve_gate", "primary"));
    ui.gateActions.append(actionButton("수정 요청", "request_revision"), actionButton("거부", "reject_gate", "danger"));
  }

  function renderGate() {
    const gate = dashboard.current_gate;
    ui.gateSelection.classList.add("hidden");
    if (!gate) { ui.gateCard.classList.add("hidden"); ui.gateActions.replaceChildren(); return; }
    ui.gateCard.classList.remove("hidden");
    ui.gateTitle.textContent = gate.summary.title;
    ui.gateDetail.textContent = gate.summary.detail;
    ui.gateStage.textContent = STAGE_NAMES[gate.stage] || gate.stage;
    if (gate.stage === "topic_approval" && selectedCandidate) {
      ui.gateSelection.classList.remove("hidden");
      ui.gateSelection.textContent = `선택: ${selectedCandidate.title} · ${selectedCandidate.score}점`;
    }
    renderGateActions();
  }

  function emptyState(title, detail) {
    const empty = node("div", "empty-state");
    empty.append(node("span", "empty-mark", "○"), node("h3", "", title), node("p", "", detail));
    return empty;
  }

  function renderScript() {
    const script = dashboard.script_view || { sections: [], visual_prompts: [] };
    ui.scriptTitle.textContent = script.title || "대본";
    ui.scriptDuration.textContent = script.total_duration_seconds ? `${Math.round(script.total_duration_seconds)}초` : "준비 중";
    ui.scriptSections.replaceChildren();
    if (!script.sections.length) ui.scriptSections.append(emptyState("대본 준비 중", "자료와 기획안을 반영한 대본이 작성되면 이곳에서 읽을 수 있습니다."));
    script.sections.forEach(section => {
      const card = node("article", "script-card");
      const meta = node("div", "script-meta");
      meta.append(node("strong", "", section.label || section.id), node("span", "", `${section.start_seconds}s – ${section.end_seconds}s`));
      card.append(meta, node("p", "script-text", section.text));
      ui.scriptSections.append(card);
    });
    ui.visualPrompts.replaceChildren();
    if (!script.visual_prompts.length) ui.visualPrompts.append(emptyState("영상 프롬프트 준비 중", "장면 구도, 카메라 움직임, 전환과 생성 지시가 이곳에 표시됩니다."));
    script.visual_prompts.forEach(prompt => {
      const card = node("article", "prompt-card");
      const header = node("div", "prompt-header");
      header.append(node("strong", "", `${prompt.sequence_id || "SEQ"} · ${prompt.shot_id || "SHOT"}`), node("span", "", `${prompt.representation || ""} · ${prompt.duration_seconds}s`));
      card.append(header, node("h3", "", prompt.sequence_purpose || "장면"), node("p", "", prompt.prompt || "화면 지시 준비 중"), node("small", "", `${prompt.provider_route || "라우트 미정"} · ${prompt.pacing_profile || "속도 미정"}`));
      ui.visualPrompts.append(card);
    });
  }

  function formatDuration(seconds) { return seconds ? `${Math.round(seconds)}초` : ""; }

  function openMedia(asset) {
    ui.mediaStage.replaceChildren();
    let media;
    if (asset.media_type === "image") { media = node("img", "media-full"); media.alt = asset.label; media.src = asset.media_url; }
    else if (asset.media_type === "video") { media = node("video", "media-full"); media.controls = true; media.playsInline = true; media.preload = "metadata"; media.src = asset.media_url; }
    else { media = node("audio", "media-audio"); media.controls = true; media.src = asset.media_url; }
    ui.mediaStage.append(media);
    ui.mediaTitle.textContent = asset.label;
    const dimensions = asset.width && asset.height ? `${asset.width}×${asset.height}` : "";
    ui.mediaMeta.textContent = [asset.media_type === "image" ? "사진" : asset.media_type === "video" ? "영상" : "오디오", dimensions, formatDuration(asset.duration_seconds)].filter(Boolean).join(" · ");
    ui.mediaDialog.showModal();
  }

  function assetCard(asset) {
    const card = node("button", "asset-card");
    card.type = "button";
    card.dataset.mediaType = asset.media_type;
    const preview = node("div", "asset-preview");
    if (asset.media_type === "audio") preview.append(node("span", "audio-mark", "♫"));
    else {
      const image = node("img", "");
      image.loading = "lazy";
      image.alt = asset.label;
      image.src = asset.preview_url;
      preview.append(image);
      if (asset.media_type === "video") preview.append(node("span", "play-mark", "▶"));
    }
    const info = node("div", "asset-info");
    info.append(node("strong", "", asset.label), node("small", "", asset.media_type === "video" ? `영상 ${formatDuration(asset.duration_seconds)}` : asset.media_type === "image" ? "사진" : "오디오"));
    card.append(preview, info);
    card.addEventListener("click", () => openMedia(asset));
    return card;
  }

  function renderAssetLibrary() {
    const library = dashboard.asset_library || { summary: {}, items: [] };
    const summary = library.summary || {};
    ui.assetCount.textContent = `${summary.total || 0}개`;
    ui.assetTotal.textContent = summary.total || 0;
    ui.assetImages.textContent = summary.images || 0;
    ui.assetVideos.textContent = summary.videos || 0;
    ui.assetAudio.textContent = summary.audio || 0;
    ui.statusAssetCount.textContent = summary.total || 0;
    const items = library.items.filter(asset => assetFilter === "all" || asset.media_type === assetFilter);
    ui.assetGrid.replaceChildren();
    if (!items.length) ui.assetGrid.append(emptyState("표시할 에셋이 없습니다", "수집 또는 생성이 완료되면 사진과 영상이 여기에 나타납니다."));
    else ui.assetGrid.append(...items.map(assetCard));
  }

  function renderEdit() {
    const edit = dashboard.edit_view || { status: "not_started", cuts: [], gaps: [] };
    ui.editStatus.textContent = edit.status === "in_progress" ? "진행 중" : edit.status === "completed" ? "완료" : "대기";
    ui.statusEditState.textContent = ui.editStatus.textContent;
    ui.editOverview.replaceChildren();
    const overview = node("article", "edit-overview-card");
    overview.append(node("strong", "", edit.cuts.length ? `${edit.cuts.length}개 구간 편집 중` : "편집 준비 중"), node("p", "", edit.cuts.length ? `${edit.render_runtime || "편집 런타임 미정"} 기준으로 타임라인을 구성하고 있습니다.` : "대본과 에셋 선택이 완료되면 편집 진행 상황이 표시됩니다."));
    ui.editOverview.append(overview);
    ui.editGaps.replaceChildren();
    if (!edit.gaps.length) ui.editGaps.append(emptyState("현재 기록된 부족분 없음", edit.cuts.length ? "추가 에셋 요구가 발견되면 즉시 표시합니다." : "장면 설계와 에셋 배치 후 부족한 사진·생성 영상이 표시됩니다."));
    edit.gaps.forEach(gap => {
      const card = node("article", "gap-card");
      if (typeof gap === "string") card.append(node("strong", "", "추가 에셋 필요"), node("p", "", gap));
      else card.append(node("strong", "", gap.type || "추가 에셋 필요"), node("p", "", gap.detail || gap.description || "확인이 필요합니다."));
      ui.editGaps.append(card);
    });
    ui.editCuts.replaceChildren();
    if (!edit.cuts.length) ui.editCuts.append(emptyState("편집 구간 없음", "편집이 시작되면 장면별 진행 상태를 볼 수 있습니다."));
    edit.cuts.forEach((cut, index) => {
      const row = node("article", "cut-row");
      row.append(node("span", "cut-index", String(index + 1).padStart(2, "0")), node("strong", "", cut.id || `구간 ${index + 1}`), node("span", "", `${cut.in_seconds}s – ${cut.out_seconds}s`), node("small", "", cut.reason || "편집 중"));
      ui.editCuts.append(row);
    });
  }

  function renderReview() {
    const review = dashboard.review_view || { status: "not_ready", issues: [] };
    ui.reviewStatus.textContent = review.status === "pass" ? "통과" : review.status === "revise" ? "수정 필요" : review.status === "fail" ? "실패" : "준비 전";
    ui.reviewPlayer.classList.toggle("hidden", !review.has_preview);
    ui.reviewEmpty.classList.toggle("hidden", review.has_preview);
    if (review.has_preview && ui.reviewPlayer.src !== new URL(review.preview_url, location.href).href) ui.reviewPlayer.src = review.preview_url;
    ui.reviewFindings.replaceChildren();
    if (!review.issues.length) ui.reviewFindings.append(emptyState(review.status === "pass" ? "검수 통과" : "검수 결과 준비 중", review.status === "pass" ? "최종본으로 이동할 수 있습니다." : "영상이 완성되면 시간 구간별 수정 사항을 표시합니다."));
    review.issues.forEach((issue, index) => {
      const card = node("article", "finding-card");
      const text = typeof issue === "string" ? issue : issue.detail || issue.description || JSON.stringify(issue);
      card.append(node("span", "finding-index", String(index + 1).padStart(2, "0")), node("p", "", text));
      ui.reviewFindings.append(card);
    });
    ui.reviewActions.replaceChildren();
    if (dashboard.current_gate && dashboard.current_gate.stage === "final_review") {
      ui.reviewActions.append(actionButton("검수 통과 승인", "approve_gate", "primary"));
      if (review.status !== "pass") ui.reviewActions.append(actionButton("편집으로 되돌리기", "return_to_edit", "danger"));
    }
  }

  function renderFinal() {
    const final = dashboard.final_view || { status: "not_ready" };
    const ready = final.status === "ready";
    ui.finalStatus.textContent = ready ? "완성" : "준비 전";
    ui.finalPlayer.classList.toggle("hidden", !ready);
    ui.finalEmpty.classList.toggle("hidden", ready);
    ui.finalDownload.classList.toggle("hidden", !ready);
    ui.finalMeta.replaceChildren();
    if (!ready) return;
    ui.finalPlayer.src = final.video_url;
    ui.finalDownload.href = final.download_url;
    const output = final.output || {};
    ui.finalMeta.append(node("span", "", output.resolution || ""), node("span", "", output.format || ""), node("span", "", formatDuration(output.duration_seconds)));
  }

  function render() {
    ui.title.textContent = dashboard.project.title;
    ui.projectId.textContent = dashboard.project.project_id;
    ui.sync.textContent = dashboard.project.last_sync ? `마지막 동기화 ${new Date(dashboard.project.last_sync).toLocaleString("ko-KR")}` : "동기화 기록 없음";
    renderCurrentWork(); renderStages(); renderAutomation(); renderGate(); renderScript(); renderAssetLibrary(); renderEdit(); renderReview(); renderFinal();
    ui.statusScriptState.textContent = dashboard.script_view.status === "available" ? "확인 가능" : "준비 중";
    ui.topicList.replaceChildren(...dashboard.topic_candidates.map(candidateCard));
    setConnection();
  }

  function openDecision(action) {
    const isRetry = action === "retry_auto_dispatch";
    const isReturn = action === "return_to_edit";
    if (!navigator.onLine || (!isRetry && !dashboard.current_gate)) return;
    if (isRetry && !(dashboard.automation && dashboard.automation.can_retry)) return;
    const gate = dashboard.current_gate;
    if (action === "approve_topic" && !selectedCandidate) return;
    pendingAction = action;
    const needsReason = ["reject_gate", "request_revision", "request_stop", "retry_auto_dispatch", "return_to_edit"].includes(action);
    const needsTypedConfirmation = !isRetry && !isReturn && TWO_STEP_GATES.has(gate.stage) && ["approve_gate", "approve_topic"].includes(action);
    const labels = { approve_topic: "주제 선택 승인", approve_gate: "승인", reject_gate: "거부", request_revision: "수정 요청", request_stop: "작업 중지 요청", retry_auto_dispatch: "자동 작업 다시 실행", return_to_edit: "편집으로 되돌리기" };
    ui.dialogTitle.textContent = labels[action];
    ui.dialogSummary.textContent = isRetry ? `${dashboard.automation.current_stage} 단계부터 다시 실행합니다.` : isReturn ? "검수 결과를 확인하고 편집 단계로 되돌립니다." : selectedCandidate && action === "approve_topic" ? `${selectedCandidate.title}을 다음 제작 주제로 승인합니다.` : gate.summary.title;
    ui.dialogImpact.textContent = isReturn ? "수정 지시를 기록한 뒤 편집 단계로 돌아갑니다. 기존 검수 기록은 보존됩니다." : action.startsWith("approve") ? "이 결정은 다음 단계 실행을 허용하는 기록입니다." : "이 요청은 제작 기록으로 남으며 기존 결과는 삭제하지 않습니다.";
    ui.reasonField.classList.toggle("hidden", !needsReason);
    ui.confirmField.classList.toggle("hidden", !needsTypedConfirmation);
    ui.reason.value = ""; ui.confirmInput.value = "";
    ui.submit.textContent = action.startsWith("approve") ? "승인 기록" : "요청 기록";
    ui.dialog.showModal();
  }

  function closeDecision() { pendingAction = null; ui.dialog.close(); }

  async function submitDecision(event) {
    event.preventDefault();
    const isRetry = pendingAction === "retry_auto_dispatch";
    const isReturn = pendingAction === "return_to_edit";
    if (!pendingAction || (!isRetry && !dashboard.current_gate) || !navigator.onLine) return;
    const gate = dashboard.current_gate;
    const needsReason = ["reject_gate", "request_revision", "request_stop", "retry_auto_dispatch", "return_to_edit"].includes(pendingAction);
    const needsTypedConfirmation = !isRetry && !isReturn && TWO_STEP_GATES.has(gate.stage) && ["approve_gate", "approve_topic"].includes(pendingAction);
    if (needsReason && !ui.reason.value.trim()) { ui.reason.focus(); return; }
    if (needsTypedConfirmation && ui.confirmInput.value !== "CONFIRM") { ui.confirmInput.focus(); return; }
    const body = isRetry ? { action: pendingAction, project_id: dashboard.project.project_id, retry_job_id: dashboard.automation.job_id, expected_job_sha256: dashboard.automation.job_sha256, idempotency_key: crypto.randomUUID(), reason: ui.reason.value.trim() } : { action: pendingAction, project_id: dashboard.project.project_id, stage: gate.stage, expected_checkpoint_sha256: gate.checkpoint_sha256, idempotency_key: crypto.randomUUID() };
    if (pendingAction === "approve_topic") body.selected_candidate_id = selectedCandidate.id;
    if (needsReason) body.reason = ui.reason.value.trim();
    if (needsTypedConfirmation) body.confirmation = "CONFIRM";
    ui.submit.disabled = true;
    try {
      await api(`/api/mobile/project/${encodeURIComponent(dashboard.project.project_id)}/actions`, { method: "POST", headers: { "Content-Type": "application/json", "X-CSRF-Token": csrfToken }, body: JSON.stringify(body) });
      ui.dialog.close(); selectedCandidate = null; await loadDashboard();
    } catch (error) {
      if (error.status === 409) { showError("상태가 바뀌었습니다. 최신 화면을 다시 불러왔습니다."); await loadDashboard(); }
      else showError(`결정을 기록하지 못했습니다: ${error.message}`);
    } finally { ui.submit.disabled = false; }
  }

  async function loadDashboard() { if (navigator.onLine && projectId) { dashboard = await api(`/api/mobile/project/${encodeURIComponent(projectId)}/dashboard`); render(); } }
  function refreshAutomationClock() { if (dashboard && dashboard.automation) renderAutomation(); }

  async function start() {
    setConnection();
    if (!navigator.onLine) return;
    try {
      const session = await api("/api/mobile/session"); csrfToken = session.csrf_token;
      if (!projectId) { const projects = await api("/api/mobile/projects"); if (!projects.length) throw new Error("표시할 프로젝트가 없습니다"); projectId = projects[0].project_id; history.replaceState(null, "", `/mobile/${encodeURIComponent(projectId)}`); }
      await loadDashboard();
      const events = new EventSource(`/api/mobile/project/${encodeURIComponent(projectId)}/events`);
      events.onmessage = event => { try { if (JSON.parse(event.data).type === "change") loadDashboard(); } catch (_error) {} };
      events.onerror = () => setConnection();
    } catch (error) { showError(`대시보드를 열 수 없습니다: ${error.message}`); }
  }

  document.querySelectorAll("[data-panel]").forEach(button => button.addEventListener("click", () => openPanel(button.dataset.panel)));
  document.querySelectorAll("[data-open-panel]").forEach(button => button.addEventListener("click", () => openPanel(button.dataset.openPanel)));
  document.querySelectorAll("[data-script-tab]").forEach(button => button.addEventListener("click", () => { document.querySelectorAll("[data-script-tab]").forEach(item => item.classList.toggle("active", item === button)); document.querySelectorAll("[data-script-view]").forEach(view => view.classList.toggle("active", view.dataset.scriptView === button.dataset.scriptTab)); }));
  document.querySelectorAll("[data-asset-filter]").forEach(button => button.addEventListener("click", () => { assetFilter = button.dataset.assetFilter; document.querySelectorAll("[data-asset-filter]").forEach(item => item.classList.toggle("active", item === button)); if (dashboard) renderAssetLibrary(); }));
  document.querySelectorAll("[data-dialog-close]").forEach(button => button.addEventListener("click", closeDecision));
  document.querySelectorAll("[data-media-close]").forEach(button => button.addEventListener("click", () => { ui.mediaStage.replaceChildren(); ui.mediaDialog.close(); }));
  ui.mediaDialog.addEventListener("click", event => { if (event.target === ui.mediaDialog) { ui.mediaStage.replaceChildren(); ui.mediaDialog.close(); } });
  ui.form.addEventListener("submit", submitDecision);
  addEventListener("online", () => { setConnection(); start(); }); addEventListener("offline", setConnection);
  setInterval(refreshAutomationClock, 30000);
  if ("serviceWorker" in navigator) { let reloadingForWorker = false; navigator.serviceWorker.addEventListener("controllerchange", () => { if (reloadingForWorker) return; reloadingForWorker = true; location.reload(); }); navigator.serviceWorker.register("/sw.js", { scope: "/" }); }
  start();
})();
