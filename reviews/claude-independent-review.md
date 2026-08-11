# Claude Independent Review — MK Visual Director Final Design v1

- Reviewer: Claude (Fable 5)
- Date: 2026-08-11
- Mode: **Independent** — `reviews/codex-independent-review.md`는 이 문서를 저장하기 전까지 읽지 않았다.
- 목적: 동조가 아니라 반증. 설계가 실패할 수 있는 지점을 찾는다.
- Human Gate: 이 리뷰는 어떤 gate도 승인하지 않는다. 모든 checkpoint는 사용자 승인 대기 상태로 남는다.

## 검수 방법

1. 지정된 9개 파일을 순서대로 정독. 추가로 `examples/` 3개, `README.md`, `reviews/README.md`, `reviews/CROSS-REVIEW-RUNBOOK.md`, `reviews/CLAUDE-INDEPENDENT-REVIEW-PROMPT.md`를 읽음.
2. 두 스키마를 Draft 2020-12 validator(jsonschema 4.26.0)로 기계 검증 — 메타스키마 검사, 예제 4개의 의도 대비 결과, 우회·과소제약·과잉제약 probe 29건.
3. `HERITAGE_FORGE.yaml` 파싱 + 내부 일관성(토큰, fallback 키, coverage, 스키마 enum 교차) 검사. 저장소 전체 내부 Markdown 링크 검사(모두 정상).
4. Hyatt 10개 구간 전체를 VisualPlan으로 실제 작성해 스키마 통과 여부와 표현 불가능 요소를 확인(dry-run).
5. 제품·API 주장을 공식 문서로 재확인: docs.topview.ai(getting-started, billing-rules, concurrency-and-storage, llms.txt, API reference), topview.ai(pricing, canvas, 3d-shot-composer, mcp), newtake.com 약관, github.com/calesthio/OpenMontage(scene_plan·checkpoint 스키마, hybrid.yaml 원문).

Disposition 표기: 이 독립검수에서 `ACCEPT`는 "지적이 유효하며 수정이 필요함", `REJECT`는 "반증을 시도했으나 설계가 옳음", `NEEDS_EVIDENCE`는 "판정에 추가 근거 필요", `BLOCKER`는 "구현 전 반드시 해결"을 뜻한다.

---

## Findings

### CLD-001

- ID: CLD-001
- Severity: BLOCKER
- Disposition: BLOCKER
- Location: `docs/ADR-002-OPENMONTAGE-INTEGRATION.md` 5행, 24행; `docs/MK_VISUAL_DIRECTOR_FINAL_DESIGN_v1.md` §5.1
- Claim: 설계 전체가 "현재 OpenMontage `scene_plan` schema"를 컴파일 대상으로 삼지만, 그 계약의 기준 커밋 `a9f1417ab4a9770bb6ebe24f51aa948a98aaa238`은 upstream에 존재하지 않고(GitHub 404), 저장소에 스키마 사본도 없다.
- Evidence: `https://github.com/calesthio/OpenMontage/commit/a9f1417...` → 404. upstream `main`의 `schemas/artifacts/scene_plan.schema.json`은 존재하지만 로컬 HEAD와 동일하다는 보장이 없다. ADR-002 스스로 "로컬 working tree에는 기존 사용자 변경이 있었다"고 기록했다.
- Failure mode: Claude·Codex·미래의 구현자가 각기 다른 scene_plan 계약을 보고 compiler를 검증한다. Acceptance test 1("valid VisualPlan이 current schema를 통과하는 artifact로 변환")이 재현 불가능해지고, upstream 변경 시 회귀를 감지할 기준선이 없다.
- Minimal change: 검토 시점의 `scene_plan.schema.json`, `checkpoint.schema.json`, `pipeline_defs/hybrid.yaml` 사본을 이 저장소 `vendor/openmontage/` 아래에 커밋하고, 대조 가능한 upstream 커밋 해시(또는 로컬 저장소의 export 방법)를 ADR-002에 기록한다.
- Verification: 리뷰어가 저장소만 clone해서 compiler 대상 스키마를 열 수 있으면 통과.

### CLD-002

- ID: CLD-002
- Severity: BLOCKER
- Disposition: BLOCKER
- Location: `schemas/visual-plan.schema.json` `$defs/overlay`; 설계 §14, §13
- Claim: "정확한 타이포·수치·도면"이 시스템의 핵심 약속인데, VisualPlan에는 overlay가 표시할 **실제 텍스트/수치/도면 내용과 claim 바인딩을 담을 필드가 없다**. `exact_text_from_claims`는 boolean일 뿐 어떤 claim의 어떤 텍스트인지 지정할 수 없고, `module`은 숏당 1개만 허용된다.
- Evidence: Hyatt dry-run에서 구간 2(날짜 타이포)의 날짜 문자열, 구간 7(load diagram)의 수치·화살표 명세를 어디에도 넣을 수 없었다. 구간 2는 TYPOGRAPHY+NUMBER, 구간 3은 CALLOUT+UNDERLINE이 동시에 필요하지만 `module`은 단일 enum이다. 다국어 치환(§14 "multilingual text substitution")을 위한 언어 맵도 없다.
- Failure mode: compiler가 scene_plan을 만들 때 overlay 내용이 없으므로 HyperFrames는 결국 사람이 별도 경로로 전달한 텍스트를 합성한다. 그 별도 경로는 claim_id와 기계적으로 연결되지 않으므로 Factual QC "every displayed number maps to claim_id"를 자동 검증할 수 없다 — 시스템의 존재 이유가 수동 공정으로 퇴화한다.
- Minimal change: `overlay.items[]`(배열)로 바꾸고 각 item에 `{module, claim_id 또는 source_id, text_key(다국어 키) 또는 literal, position_hint}`를 둔다. `exact_text_from_claims=true`인 item은 `claim_id` 필수.
- Verification: Hyatt 구간 2·3·7을 overlay item으로 완전 기술한 예제가 스키마를 통과하고, validator가 "표시 텍스트 → claim_id" 역추적을 기계적으로 수행할 수 있으면 통과.

### CLD-003

- ID: CLD-003
- Severity: BLOCKER
- Disposition: BLOCKER
- Location: 설계 §19(Gate-to-stage mapping), `docs/ADR-002` "Human Gate boundary"
- Claim: GATE_FINAL_EDIT과 GATE_TITLE_THUMBNAIL은 "pipeline 확장 필요"라고만 적혀 있고 구체 메커니즘이 설계되지 않았다. 이 상태로는 Acceptance criteria 4("Human Gate를 우회하는 상태 전이가 없음")를 충족하지 못한다.
- Evidence: upstream `pipeline_defs/hybrid.yaml` 원문에서 edit·compose 단계가 `human_approval_default: false`임을 확인했다 — 설계의 자기 인정(§19 "자동 진행될 수 있으므로")은 사실이다. checkpoint 스키마에 `human_approval_required`/`human_approved` boolean이 이미 존재하므로 기술적 장애물은 없지만, custom manifest를 쓸지 approval artifact를 쓸지, 그 artifact의 스키마와 작성 주체가 무엇인지 v1에 없다.
- Failure mode: Phase 1 구현자가 기본 hybrid manifest를 그대로 쓰면 최종 편집과 제목·썸네일이 사람 승인 없이 compose→publish 직전까지 자동 진행된다. 문서상의 gate 목록은 이를 막지 못한다.
- Minimal change: v2에서 (a) `mk-hybrid.yaml` custom manifest: edit·compose에 `human_approval_default: true` 지정, (b) GATE_TITLE_THUMBNAIL용 approval artifact의 최소 스키마(파일명, 필드, 작성 주체) 정의. 두 가지 모두 문서가 아니라 스키마/manifest 수준으로.
- Verification: dry-run에서 edit 단계 checkpoint가 `awaiting_human`으로 멈추는 것을 확인하면 통과.

### CLD-004

- ID: CLD-004
- Severity: HIGH
- Disposition: ACCEPT
- Location: 설계 §5.1, `docs/ADR-002` Decision; upstream `schemas/artifacts/scene_plan.schema.json`
- Claim: VisualPlan→scene_plan compiler의 **매핑 명세가 없다**. 특히 representation(REAL/AI_RECONSTRUCTION/GRAPHIC/HYBRID)을 upstream scene `type` enum(`talking_head, broll, animation, character_scene, diagram, text_card, transition, generated, screen_recording`)으로 어떻게 대응시키는지 규칙이 없고, HYBRID는 자연스러운 대응이 없다.
- Evidence: upstream scene_plan을 직접 확인한 결과 scene 객체는 `additionalProperties: false`이며 disclosure·evidence_ids·provider_route·fallback·continuity에 해당하는 필드가 없다. top-level `metadata`만 자유 객체다. 즉 shot-level 계약은 scene별로 붙일 수 없고 top-level metadata 또는 `overlay_notes` 자유 텍스트로만 전달된다.
- Failure mode: compile 후 단계(assets/edit/compose)에서 동작하는 도구는 scene_plan만 읽으므로 disclosure 의무·evidence 연결·fallback을 모른다. AI 재현 라벨 누락이 edit 단계에서 감지되지 않고 review build까지 흘러간다.
- Minimal change: v2에 (a) representation×coverage→scene type 매핑 표, (b) 손실 필드 목록과 각 필드의 이관 위치(`metadata.shots[scene_id]` 관례 등), (c) "Media/Factual QC는 scene_plan이 아니라 visual-plan.json을 직접 읽는다"는 명시 규칙을 추가.
- Verification: Hyatt dry-run plan을 손으로 compile한 표에서 10개 숏 전부가 유효한 scene type과 손실 없는 QC 경로를 갖면 통과.

### CLD-005

- ID: CLD-005
- Severity: HIGH
- Disposition: ACCEPT
- Location: `schemas/visual-plan.schema.json` top-level required; 설계 §5
- Claim: VisualPlan이 **자신이 생성된 대본을 참조하지 않는다**. `evidence_lock.registry_version`은 있지만 `script_ref`/`script_sha256`이 없어, 대본이 바뀐 뒤의 stale plan을 감지할 수 없다.
- Evidence: 스키마 top-level 속성은 schema_version, project_id, plan_id, status, generated_by, evidence_lock, global_style, sequences, approval뿐이다. `narration_range`는 초 단위 offset인데 기준이 되는 대본 버전이 파일 어디에도 없다.
- Failure mode: GATE_SCRIPT 이후 대본이 한 문장 수정되면 모든 narration_range와 claim 연결이 조용히 어긋난다. QC "VisualPlan checksum과 compiled scene plan checksum의 freshness"는 plan→scene_plan 방향만 보호하고 script→plan 방향은 보호하지 않는다.
- Minimal change: top-level에 `script_ref`(artifact 경로)와 `script_sha256` 필수 필드 추가 — evidence_lock과 같은 패턴.
- Verification: 대본 파일 1바이트 수정 후 validator가 stale을 검출하면 통과.

### CLD-006

- ID: CLD-006
- Severity: HIGH
- Disposition: ACCEPT
- Location: 설계 §2.4; `schemas/visual-plan.schema.json` `$defs/shot` allOf(2)
- Claim: HYBRID가 "실제 자료+정밀 그래픽"과 "실제→AI 전환"이라는 **성격이 전혀 다른 두 경우를 한 값에 과적재**했고, 스키마는 HYBRID 전체에 disclosure 라벨을 강제한다. 그 결과 AI가 전혀 없는 화면에도 라벨이 붙어 AI 표시의 변별력이 희석된다.
- Evidence: `examples/visual-plan.minimal.valid.json`의 HYBRID 숏은 AI가 없는데 라벨 "실제 자료 + 설명 그래픽"을 강제로 갖는다. Hyatt dry-run에서도 구간 2·3(실사진+타이포)이 같은 처지였다. 라벨은 자유 텍스트라 "AI 재현" 라벨과 기계적으로 구분되지 않는다.
- Failure mode: 시청자가 모든 라벨을 장식으로 학습한다 — AI 재현 표시 원칙(§2.4)의 목적 자체가 무력화된다. Factual QC "AI reconstruction label exists when needed"도 '어떤 HYBRID가 AI를 포함하는가'를 기계적으로 판정할 수 없다.
- Minimal change: shot에 `contains_ai: boolean`을 추가하고 disclosure 강제 조건을 `representation ∈ {AI_RECONSTRUCTION} ∨ contains_ai=true`로 변경. 라벨 문자열을 enum 또는 통제 어휘(`AI 재현`, `AI 재현 + 설명 그래픽`, `실제 자료 + 설명 그래픽`)로 제한.
- Verification: probe: AI 없는 HYBRID가 라벨 없이 통과하고, contains_ai=true인데 라벨이 없으면 실패해야 한다.

### CLD-007

- ID: CLD-007
- Severity: HIGH
- Disposition: ACCEPT
- Location: 설계 §5.1, §16, §19; `docs/ADR-002`
- Claim: 편집 단계 이후의 **역방향 동기화 규칙이 없다**. VisualPlan은 숏별 edit_trigger·transition을 상세 지정하지만, edit_decisions에서 편집자가 컷을 바꾸면 어느 artifact가 권위인지, VisualPlan이 stale로 표시되는지 정의되지 않았다.
- Evidence: §5.1은 "VisualPlan이 바뀌면 scene_plan을 다시 생성한다"만 규정한다(정방향). edit_decisions→VisualPlan 방향은 §19, ADR-002 어디에도 없다. End anchor edit(§16.1)은 편집 단계에서 큰 재배열을 전제하므로 이 충돌은 반드시 발생한다.
- Failure mode: 최종 영상과 VisualPlan이 다른데 둘 다 '승인된 artifact'로 남는다. Golden Test의 "±2 frames" 검사를 VisualPlan 기준으로 하면 실제 컷과 다른 것을 검사하게 된다.
- Minimal change: "VisualPlan의 편집 필드는 GATE_ANIMATIC까지의 계획 가설이며, edit_decisions가 컷의 최종 권위다. 편집 QC는 edit_decisions 기준으로 수행하고, plan 대비 이탈은 보고서로만 남긴다"를 v2에 명문화.
- Verification: 문서에 권위 순서가 명시되고 QC 절차가 그 순서를 참조하면 통과.

### CLD-008

- ID: CLD-008
- Severity: HIGH
- Disposition: ACCEPT
- Location: `golden-tests/HYATT-60-90S-GOLDEN-SEQUENCE.md` Visual continuity·Edit and audio; 설계 §16.2, §20
- Claim: "±2 frames", "anchor 위치 오차 3% 이하" 같은 정량 기준을 **계산할 데이터 구조가 어느 스키마에도 없다**. beat map(§16.2)은 artifact 목록(§5)에 없고, `sync_event`는 자유 문자열이며, anchor에는 좌표가 없다.
- Evidence: visual-plan 스키마의 `audioLayer.sync_event`는 `["string","null"]`, `continuity_bindings`는 문자열 배열이다. 타임스탬프·좌표 필드가 전무하다. Hyatt dry-run에서 구간 4→5의 match anchor를 "walkway_anchor"라는 이름 문자열로만 표현할 수 있었다.
- Failure mode: Golden Test 채점 시 ±2 frames와 3% 기준을 측정하려면 사람이 수작업으로 프레임을 세야 한다. 측정 절차가 정의되지 않았으므로 리뷰어마다 다른 값을 내고, "측정 가능해야 한다"는 Acceptance criteria 9가 사실상 미충족이다.
- Minimal change: (a) beat map을 canonical artifact로 승격하고 최소 스키마(`{event_id, type, time_seconds}`) 정의, (b) anchor에 선택적 `{x_pct, y_pct}` 추가, (c) 두 기준의 측정 절차(어떤 파일에서 어떤 도구로)를 golden test 문서에 1단락씩 명기.
- Verification: 제3자가 문서만 보고 같은 review build에서 같은 측정값을 재현하면 통과.

### CLD-009

- ID: CLD-009
- Severity: MEDIUM
- Disposition: ACCEPT
- Location: `schemas/visual-plan.schema.json` `$defs/approval`, top-level `status`; 설계 §19
- Claim: 승인 상태의 **전이 규칙과 단일 기록처가 없다**. 스키마는 상태값만 검증하므로 (a) 에이전트가 `approved_by`에 임의 이름을 채운 self-approval이 통과하고, (b) `plan.status=approved`인데 `approval.status=awaiting_human`인 모순 파일이 통과하며, (c) approval이 visual-plan과 checkpoint 두 곳에 이중 존재한다.
- Evidence: probe 결과 — `approved_by:"claude-agent-self"` 채운 파일 valid, plan/approval 상태 모순 파일 valid, `gate:"GATE_PUBLISH"`를 단 visual-plan도 valid. 설계 §20.1이 "top-level plan status와 approval status의 일관성"을 QC 항목으로 인정하지만 그 검사기의 규칙 목록이 없다.
- Failure mode: 파일 기반 승인은 파일을 쓰는 에이전트가 항상 위조할 수 있다. 진짜 방어선은 checkpoint(`human_approved`)인데, visual-plan 내부의 approval 객체가 '승인됨'처럼 보이는 두 번째 진실을 만들어 감사를 흐린다.
- Minimal change: visual-plan에서 approval 객체를 제거하거나 `gate_ref`(checkpoint 파일 참조)로 축소한다. 유지한다면 (a) 허용 전이 표(drafting→awaiting_human→approved/rejected/needs_revision, any→superseded), (b) plan.status와 approval.status의 일관성 규칙, (c) approval의 유일 작성 주체를 semantic validator 스펙으로 명문화한다.
- Verification: probe (a)(b)가 semantic validator에서 실패로 바뀌면 통과.

### CLD-010

- ID: CLD-010
- Severity: MEDIUM
- Disposition: ACCEPT
- Location: `schemas/visual-plan.schema.json` `$defs/approval` allOf else절
- Claim: `status`가 approved가 아니면 `approved_by`/`approved_at`을 **null로 강제**하므로, 누가 언제 rejected/needs_revision 판정을 내렸는지 기록할 수 없다.
- Evidence: probe — `status:"rejected", approved_by:"MK"` 파일이 INVALID("'MK' is not of type 'null'"). 거절 이력은 감사에서 승인만큼 중요하다.
- Failure mode: 거절 사유·주체가 notes 자유 텍스트로만 남아 기계 감사가 불가능하고, superseded 체인 추적도 안 된다.
- Minimal change: 필드를 `decided_by`/`decided_at`으로 개명하고 approved/rejected/needs_revision/superseded에서 non-null을 요구, drafting/awaiting_human에서만 null 강제.
- Verification: rejected+주체 기록 파일이 valid, approved+null 파일이 invalid면 통과.

### CLD-011

- ID: CLD-011
- Severity: MEDIUM
- Disposition: ACCEPT
- Location: 두 스키마의 모든 `format` 사용처; 설계 Phase 1 "VisualPlan validator"
- Claim: Draft 2020-12에서 `format`은 기본적으로 **주석일 뿐 검증되지 않는다**. validator 툴체인 요구사항이 설계에 없으므로 `approved_at:"yesterday sometime"` 같은 값이 통과한다.
- Evidence: probe — jsonschema 4.26.0 기본 설정에서 valid, `FormatChecker`를 붙여도 `rfc3339-validator` 미설치 상태에서는 여전히 valid. 이는 라이브러리 일반 동작이다(ajv도 `ajv-formats` 필요).
- Failure mode: 날짜·시각 필드 전체(retrieved_at, approved_at, created_at, publication_date)가 사실상 자유 문자열이 되어 freshness 비교·정렬이 깨진다.
- Minimal change: Phase 1 validator 스펙에 "format assertion 활성화 필수 + 구체 의존성(예: jsonschema+rfc3339-validator 또는 ajv+ajv-formats)"을 명기한다.
- Verification: 잘못된 date-time이 validator에서 실패하면 통과.

### CLD-012

- ID: CLD-012
- Severity: MEDIUM
- Disposition: ACCEPT
- Location: `schemas/visual-plan.schema.json` `$defs/shot` required(`camera`, `lighting`)
- Claim: GRAPHIC·HyperFrames 숏에도 물리 카메라 필드(framing/angle/height/lens_intent/movement)와 lighting이 **필수**라서 의미 없는 값을 지어내야 한다.
- Evidence: Hyatt dry-run 구간 7(load diagram)에서 `framing:"insert", lens_intent:"normal", lighting.family:"archive_or_motivated"` 같은 허구 값을 강제로 채웠다. 이런 노이즈가 compiler와 QC로 흘러간다.
- Failure mode: 다이어그램 숏의 camera 값을 진지하게 읽는 하위 도구(예: scene_plan의 shot_language 변환)가 잘못된 연출 정보를 갖게 되고, "필수 필드"의 신뢰가 전반적으로 떨어진다.
- Minimal change: `camera`·`lighting`을 `representation ∈ {REAL, AI_RECONSTRUCTION}` 또는 `provider_route.mode ∈ {REAL_INGEST, TOPVIEW_*, LOCAL_LTX}`일 때만 필수로 하는 조건부 스키마로 변경.
- Verification: GRAPHIC 숏이 camera 없이 valid, AI 숏이 camera 없이 invalid면 통과.

### CLD-013

- ID: CLD-013
- Severity: MEDIUM
- Disposition: ACCEPT
- Location: `schemas/visual-plan.schema.json` `provider_route.cost_tier`; 설계 §12.2, §19(GATE_BUDGET)
- Claim: GATE_BUDGET의 입력이 될 **수치 비용 추정 필드가 없다**. `cost_tier` enum(zero/draft/standard/premium)만으로는 "모든 유료 호출 전에 estimated cost를 기록한다"(§12.2)를 plan 수준에서 이행할 수 없다.
- Evidence: TopView는 모델·해상도별 크레딧이 공개돼 있고(예: 계열 모델 4 credits/4s) 응답에 `costCredit`이 있다. 추정→실측 대조가 가능한 구조인데 추정값을 담을 자리가 없다.
- Failure mode: 예산 게이트가 "숏 몇 개 × 대략 얼마"라는 문서 밖 계산에 의존하게 되고, cost snapshot(§19)과 plan의 대응이 끊긴다.
- Minimal change: `provider_route`에 선택 필드 `estimated_credits: number` 추가, plan 수준 합계는 validator가 계산해 checkpoint의 cost snapshot과 대조.
- Verification: 유료 mode(TOPVIEW_API 등)에서 estimated_credits 부재 시 semantic validator가 경고하면 통과.

### CLD-014

- ID: CLD-014
- Severity: MEDIUM
- Disposition: ACCEPT
- Location: `golden-tests/BANGJJA-STYLE-ACCEPTANCE-TEST.md` Scoring
- Claim: 5개 영역 각 20점·총 85점 합격이라는 정량 기준이 있지만 **체크리스트 항목→점수 배분 규칙이 없어** 총점을 재현 가능하게 계산할 수 없다.
- Evidence: 예: "Edit and audio" 영역은 체크 항목 6개에 20점 — 항목당 3.33점인지, 가중치가 있는지, 부분 점수가 허용되는지 미정의. 리뷰어 두 명이 같은 영상에 다른 점수를 내도 판정할 근거가 없다.
- Failure mode: 85점 경계선 근처에서 합격/불합격이 리뷰어 재량이 되고, Claude·Codex 점수 불일치를 중재할 규칙이 없다.
- Minimal change: 각 체크 항목에 명시적 배점을 부여(영역 합계 20점)하고 부분 점수 규칙(0/절반/만점)을 한 줄로 정의.
- Verification: 두 리뷰어가 같은 가상 결과표로 같은 총점을 내면 통과.

### CLD-015

- ID: CLD-015
- Severity: MEDIUM
- Disposition: PARTIAL
- Location: 설계 §12.1(Canvas path), `schemas/visual-plan.schema.json` `provider_route.mode`
- Claim: (a) §12.1이 "3D blocking"을 Canvas 용도로 기재했지만 공식 Canvas 페이지에는 3D blocking이 없고 별도 제품 3D Shot Composer의 기능이다. (b) 수동 탐색 공간인 Canvas가 자동 라우팅 대상인 `provider_route.mode` enum(TOPVIEW_CANVAS)에 들어 있어 역할 경계가 흐려진다.
- Evidence: topview.ai/canvas — 스토리보드 카드·씬 비교·에이전트 언급, 3D blocking 없음. topview.ai/3d-shot-composer — "previsualization and blocking tool"로 명시. API 문서에 Board(List/Get/Batch Download) 엔드포인트가 있어 Canvas 산출물 수집 일부는 자동화 가능하나, Canvas 작업 자체는 수동이다.
- Failure mode: Router가 TOPVIEW_CANVAS로 라우팅한 숏은 사실상 "사람이 Canvas에서 만들어 올 것"이라는 뜻인데, 이것이 자동 provider와 같은 enum에 있으면 상태 기계(submit/status/result)가 적용되지 않는 모드가 생겨 구현이 갈라진다.
- Minimal change: §12.1 문구를 "3D blocking은 3D Shot Composer"로 수정. TOPVIEW_CANVAS mode는 제거하고 Canvas 산출물은 REAL_INGEST와 동일한 수동 ingest 경로로 정의(출처만 provider metadata로 구분)하거나, 유지한다면 "manual mode"의 상태 규칙을 별도 정의.
- Verification: provider interface(§11.2)의 4개 함수가 모든 mode에 대해 정의 가능하면 통과.

### CLD-016

- ID: CLD-016
- Severity: MEDIUM
- Disposition: ACCEPT
- Location: `schemas/source-registry.schema.json`; 설계 §20.1
- Claim: Source Registry의 구조적 허점 4건 — (a) sources/claims가 빈 배열이어도 valid하고 그 위에 evidence_lock을 approve할 수 있다, (b) `status:"verified"` claim이 `contradicts` 인용만으로 valid, (c) `community` 출처가 credibility_tier 1로 valid, (d) rights `verified`인데 license null·local_copy null이 valid.
- Evidence: probe 4건 모두 valid로 통과(스키마 수준). §20.1이 semantic check를 예고하지만 규칙 목록이 없다.
- Failure mode: '스키마 통과'가 '증거 잠금 가능'으로 오독되면 빈 registry 위에 GATE_EVIDENCE_LOCK이 승인될 수 있다. verified의 의미가 인용 관계와 무관해진다.
- Minimal change: Phase 1 semantic validator 스펙에 최소 규칙 명시: evidence_lock 승인 시 sources≥1·claims≥1, verified claim은 supports 인용 ≥1, source_type과 tier의 허용 조합 표, rights.status=verified→license non-null. (스키마 자체보다 validator 규칙서가 적절한 위치다.)
- Verification: probe (a)–(d)가 semantic validator에서 실패로 바뀌면 통과.

### CLD-017

- ID: CLD-017
- Severity: MEDIUM
- Disposition: ACCEPT
- Location: 설계 전체(부재); `golden-tests/HYATT-60-90S-GOLDEN-SEQUENCE.md`
- Claim: 첫 Golden Test 소재가 114명이 사망한 실제 참사인데, **희생자·재난 묘사에 대한 편집 윤리 정책이 설계에 없다**. §2.4와 disclosure는 'AI임을 표시'만 다루고 '무엇을 재현하면 안 되는가'는 다루지 않는다.
- Evidence: 설계 §20.3 Factual QC와 golden test blocker 목록에 인명 피해 묘사 관련 항목이 없다. 재현 시퀀스(§17)는 붕괴 순간의 재현을 배제하지 않는다.
- Failure mode: AI로 사상 장면을 사실적으로 재현하면 라벨이 있어도 유가족·플랫폼·시청자 기준에서 문제가 된다. 채널 신뢰가 첫 에피소드에서 훼손될 수 있다.
- Minimal change: Visual Grammar 공통 규칙에 "인명 피해 순간의 사실적 AI 재현 금지, 구조·역학 중심 재현 허용" 같은 1-2줄 경계와 Factual QC 항목 1개 추가.
- Verification: Hyatt visual-plan에서 붕괴 순간을 직접 재현하는 숏이 QC에서 걸리면 통과.

### CLD-018

- ID: CLD-018
- Severity: LOW
- Disposition: ACCEPT
- Location: `config/visual-grammars/HERITAGE_FORGE.yaml` 119, 121-125, 20-33행
- Claim: 데이터 품질 3건 — (a) failure_patterns의 `hero_reveal_has_no narrative_or_evidence_payoff`에 스페이스가 있어 토큰이 깨졌다, (b) fallbacks의 키 `generated_text`·`queue_or_budget_failure`가 failure_patterns에 없는 키라 패턴→fallback 조회가 어긋난다(`title_is_baked_into_generated_video`는 fallback이 없다), (c) `sequence_pattern`은 evidence_insert를 쓰는데 `required_inputs.coverage.required`에는 없다 — Bangjja 테스트는 evidence_insert ≥1을 요구하므로 grammar 스스로와 불일치.
- Evidence: YAML 파싱 후 집합 비교 결과(검수 스크립트 출력).
- Failure mode: grammar를 기계로 읽는 Phase 1 loader가 만들어지는 순간 조회 실패 또는 잘못된 fallback 적용이 된다.
- Minimal change: 스페이스→언더스코어, fallback 키를 failure_patterns와 1:1로 정렬, required coverage에 evidence_insert 추가.
- Verification: "fallback 키 ⊆ failure_patterns, required ⊆ pattern coverage" 자동 검사 통과.

### CLD-019

- ID: CLD-019
- Severity: LOW
- Disposition: ACCEPT
- Location: `schemas/visual-plan.schema.json` sequence(entry/exit_transition)와 shot(transition_in/out)
- Claim: 시퀀스 경계에서 transition이 이중 정의된다 — sequence.exit_transition과 마지막 shot.transition_out이 충돌할 때 어느 쪽이 이기는지 규칙이 없다.
- Evidence: dry-run에서 SEQ_HY01.exit_transition=motion_match와 HY_SH04.transition_out=motion_match를 수동으로 일치시켜야 했다. 스키마·문서 모두 우선순위 규칙이 없다.
- Failure mode: compiler가 임의로 하나를 고르면 LLM adapter별로 결과가 달라져 §10의 동일 schema 출력 비교가 오염된다.
- Minimal change: "경계 transition은 sequence가 소유하고 첫/마지막 shot의 해당 필드는 `none`이어야 한다" 같은 한 줄 규칙 + semantic check.
- Verification: 충돌 파일이 validator에서 실패하면 통과.

### CLD-020

- ID: CLD-020
- Severity: LOW
- Disposition: ACCEPT
- Location: `schemas/visual-plan.schema.json` `provider_route.mode`의 `OPENMONTAGE_ONLY`; 설계 §11.1
- Claim: `OPENMONTAGE_ONLY` mode가 스키마에만 존재하고 설계 본문(§11.1 라우팅 결정표 포함) 어디에도 정의가 없다.
- Evidence: 저장소 전문 검색에서 해당 토큰은 스키마 1곳뿐.
- Failure mode: 각 구현자가 의미를 추측한다(자막 전용? 편집 전용 숏?).
- Minimal change: §11.1에 한 줄 정의를 추가하거나 enum에서 제거.
- Verification: 문서와 enum의 1:1 대응 검사.

### CLD-021

- ID: CLD-021
- Severity: LOW
- Disposition: NEEDS_EVIDENCE
- Location: `docs/ADR-001` Required safeguards 7("`/user/credit/detail`")
- Claim: 크레딧 조회 API의 존재는 확인되지만 정확한 endpoint 경로 `/user/credit/detail`은 공개 문서 목록에서 확인하지 못했다.
- Evidence: docs.topview.ai llms.txt 목록에는 "Query User Credit", "Query Credit Logs", "Query User Space"로 표기된다. 실제 경로 문자열은 해당 reference 페이지에서 재확인 필요.
- Failure mode: 경로가 다르면 pilot 어댑터의 비용 수집이 첫 실행에서 실패한다(치명적이지 않음 — 즉시 수정 가능).
- Minimal change: Phase 3 시작 시 reference 페이지에서 경로를 재확인하고 ADR-001에 반영.
- Verification: 실제 200 응답과 필드 확인.

### CLD-022

- ID: CLD-022
- Severity: LOW
- Disposition: NEEDS_EVIDENCE
- Location: `docs/ADR-001` Required safeguards 5; 설계 §11.3
- Claim: "실패 generation도 비용이 발생했는지 확인한다"는 안전장치는 옳지만, **실패 시 과금 여부에 대한 공식 규칙을 문서에서 확인하지 못했다**.
- Evidence: docs.topview.ai billing-rules는 실패 과금을 다루지 않는다(2026-08-11 확인). 설계도 단정하지 않고 '확인하라'고만 하므로 설계 자체는 문제 없음 — 다만 pilot 측정 항목으로 명시돼야 한다.
- Failure mode: 실패율이 높은 모델에서 예산 추정이 실측과 크게 어긋날 수 있다.
- Minimal change: Phase 4 Golden Pilot의 측정 항목에 "실패 task의 costCredit 분포"를 명시.
- Verification: pilot 후 실패 task 로그에 costCredit 기록 존재.

### CLD-023

- ID: CLD-023
- Severity: LOW
- Disposition: ACCEPT
- Location: 설계 §20(QC 소유), §7.2(Sequence 15–60초)
- Claim: 소소한 명세 공백 2건 — (a) Factual QC와 Editorial QC의 수행 주체가 §20에 배정되지 않았다(Data QC=validator, Media QC=OpenMontage는 유추 가능), (b) "Sequence는 15~60초"라는 §7.2 규칙이 스키마·validator 어디에도 없다(74초 Hyatt를 한 시퀀스로 만들어도 통과).
- Evidence: dry-run에서 74초 단일 시퀀스 구성도 스키마를 통과함을 확인. §20에는 검사 항목만 있고 owner 열이 없다.
- Failure mode: QC 항목이 '모두의 일 = 누구의 일도 아님'이 된다.
- Minimal change: §20에 owner 열 추가, 15–60초는 semantic validator의 경고(warning) 규칙으로.
- Verification: QC 항목별 owner가 명시되면 통과.

---

## 1. 유지해야 할 강점

1. **Clean plate 원칙(§2.3)** — 생성 영상에서 글자·수치를 분리하는 결정은 현재 영상 생성 모델의 실제 약점에 정확히 대응한다. 이 설계에서 가장 가치 있는 단일 규칙이다.
2. **VisualPlan을 IR로, OpenMontage를 canonical로 두는 구조(ADR-002)** — upstream을 fork하지 않고 `metadata` 확장점(실물 확인: 자유 객체)을 쓰는 판단은 옳고, 실제 스키마와도 호환된다.
3. **Negative example의 존재와 실효성** — `invalid-human-gate`, `invalid-undisclosed-ai`가 실제로 스키마에서 의도한 이유로 실패함을 기계 검증으로 확인했다. 계약을 예제로 고정하는 습관은 유지할 가치가 크다.
4. **Evidence Layer의 pinpoint citation과 `contradicts` 관계** — 반대 근거를 기록할 수 있는 구조는 사실 검증 시스템의 성숙한 설계다.
5. **Provider 상태 정규화(§11.3)** — 문서상 일반화보다 실제 endpoint 응답을 우선한다는 원칙까지 포함해, 실제 TopView 응답 구조(init/success/fail, costCredit)와 일치함을 확인했다.
6. **ADR-001의 과금·저장 회의주의** — 검증 결과 전부 사실이었고 일부는 공식 문서가 더 강하게 뒷받침한다(Ultra 크레딧은 API에 아예 사용 불가, URL 7일 만료 명시).
7. **Coverage 조립 편집(§7.4)** — 인물·공간 연속성이 약한 생성 모델의 실패를 짧은 coverage로 우회하는 전략은 방짜유기 분석에서 올바르게 추출된 교훈이다.
8. **자기 인정된 gate 구멍(§19)** — edit/compose 자동 진행 위험을 설계 스스로 기록했고, upstream manifest 실물로 사실임을 확인했다. 이 정직성은 유지돼야 한다(해결은 CLD-003).
9. **"렌더 성공 ≠ 완료" blocker** — 두 golden test 모두 실제 decode·프레임 육안 검수를 요구한다. 검증 지표가 목적을 재는지 의심하는 문화가 문서에 박혀 있다.

## 2. 심각도순 문제점

| ID | Severity | 요약 |
|---|---|---|
| CLD-001 | BLOCKER | OpenMontage 계약 기준선(커밋/스키마 사본)이 검증 불가 |
| CLD-002 | BLOCKER | overlay 텍스트·수치의 내용과 claim 바인딩을 담을 필드 부재 |
| CLD-003 | BLOCKER | GATE_FINAL_EDIT·GATE_TITLE_THUMBNAIL 강제 메커니즘 미설계(upstream 기본값은 자동 진행) |
| CLD-004 | HIGH | representation→scene type 매핑 및 손실 필드 이관 명세 부재 |
| CLD-005 | HIGH | script_ref/script_sha256 부재 — 대본 변경 후 stale plan 감지 불가 |
| CLD-006 | HIGH | HYBRID 과적재로 AI 표시 라벨의 변별력 희석 |
| CLD-007 | HIGH | edit 이후 역방향 동기화·권위 순서 미정의 |
| CLD-008 | HIGH | ±2 frames·3% anchor 기준의 측정 데이터 구조 부재 |
| CLD-009 | MEDIUM | 승인 전이 규칙 부재 + self-approval 통과 + 승인 기록 이중화 |
| CLD-010 | MEDIUM | rejected/needs_revision의 판정 주체 기록 불가(스키마가 null 강제) |
| CLD-011 | MEDIUM | format(date-time 등)이 기본 미검증 — validator 툴체인 미명세 |
| CLD-012 | MEDIUM | GRAPHIC 숏에 물리 camera/lighting 강제 → 허구 데이터 생성 |
| CLD-013 | MEDIUM | GATE_BUDGET 입력이 될 수치 비용 추정 필드 부재 |
| CLD-014 | MEDIUM | Bangjja 85점 기준의 항목별 배점 미정의 |
| CLD-015 | MEDIUM | Canvas에 3D blocking 오귀속 + 수동 도구가 자동 라우팅 enum에 존재 |
| CLD-016 | MEDIUM | 빈 registry 잠금 가능 등 semantic validator 규칙 목록 부재 |
| CLD-017 | MEDIUM | 참사 소재의 희생자 묘사 윤리 경계 부재 |
| CLD-018 | LOW | HERITAGE_FORGE 토큰 오타·fallback 키 불일치·coverage 불일치 |
| CLD-019 | LOW | 시퀀스 경계 transition 이중 정의 |
| CLD-020 | LOW | OPENMONTAGE_ONLY mode 미문서화 |
| CLD-021 | LOW | `/user/credit/detail` 정확 경로 미확인 (NEEDS_EVIDENCE) |
| CLD-022 | LOW | 실패 generation 과금 규칙 미확인 — pilot 측정 항목화 필요 (NEEDS_EVIDENCE) |
| CLD-023 | LOW | Factual/Editorial QC owner 미배정, 15–60초 규칙 미강제 |

## 3. 스키마 검증 결과

- 도구: Python jsonschema 4.26.0, Draft 2020-12. `HERITAGE_FORGE.yaml`은 PyYAML 파싱 + 교차 검사.
- 메타스키마: 두 스키마 모두 유효한 Draft 2020-12 스키마.
- 예제 4개: 전부 의도대로 동작 — `visual-plan.minimal.valid` PASS, `invalid-human-gate` FAIL(approved_by/at null), `invalid-undisclosed-ai` FAIL(disclosure const·label·evidence minItems), `source-registry.minimal.valid` PASS.
- Hyatt dry-run: 10구간 전체를 2개 시퀀스·10숏으로 작성 → **스키마 통과**, 구간 합계 74초 일치.
- 우회·제약 probe 29건 중 스키마가 막지 못한 주요 사례: 에이전트 self-approval(이름만 채우면 valid), plan/approval 상태 모순, 잘못된 date-time(포맷 미검증), 시퀀스보다 긴 숏(8초 시퀀스 안의 500초 숏), 중복 shot_id(시퀀스 간), 존재하지 않는 grammar/evidence id 참조, 빈 registry, contradicts 인용만으로 verified, community 출처의 tier 1. — 이 중 다수는 설계가 semantic check로 예고한 영역이지만(§20.1), 그 규칙 목록이 아직 없다는 점이 문제의 본질이다(CLD-009, 011, 016).
- 내부 Markdown 링크: 깨진 링크 없음. YAML 문제는 CLD-018 참조.

## 4. Golden Test dry-run 결과

**Hyatt 60–90s**: 표현 가능성 판정 — **조건부 가능**. 10구간 모두 스키마로 기술되고 타이밍(74초)도 일치한다. 그러나 작성 과정에서 다음을 표현할 수 없었다: (a) 날짜·수치·다이어그램의 실제 내용과 claim 바인딩(CLD-002), (b) 한 숏의 복수 overlay 모듈(CLD-002), (c) 4→5 전환 match anchor의 위치(3% 기준 측정 불가, CLD-008), (d) 구간 6의 freeze 시점·구간 5 clean plate 재사용 참조(자유 텍스트로만), (e) "마지막 문장 뒤 12 frames hold"(beat 데이터 구조 부재). Pass/fail 기준 중 Contract·Graphics·Media verification 절은 측정 가능하고, Visual continuity의 3%·Edit and audio의 ±2 frames는 측정 절차 정의 전까지 수동 판정이다. "REAL과 AI 경계를 보통 시청자가 이해"는 판정 프로토콜이 없는 주관 기준이다.

**Bangjja style**: coverage·모티프·연속성 요구는 현 스키마의 coverage_role·motif_bindings·continuity_bindings로 표현 가능하다. HERITAGE_FORGE의 `identical_camera_pattern_max_consecutive: 2`와 테스트의 "같은 패턴 3연속 금지", `impact_sync_tolerance_frames: 2`와 "±2 frames"는 서로 일치한다(좋음). 그러나 85점 채점은 항목별 배점이 없어 재현 불가능하고(CLD-014), grammar 데이터 자체의 불일치 3건(CLD-018)이 loader 구현 시 드러난다.

## 5. TopView 결정: 유지·수정·번복

**판정: 유지(조건부 수정).** 번복할 근거를 찾으려 했으나 실패했다.

- 공식 확인된 사실: REST API와 API key 인증 존재, 기능별 submit/query task 비동기 패턴, 응답의 init/success/fail 상태와 costCredit 필드, 크레딧 조회·로그 endpoint 존재, **웹·API 크레딧 공유**, **Ultra 크레딧 API 사용 불가(공식 명시)**, **API 결과 URL 7일 유효(공식 명시)**, 공유 자원 pool의 플랜별 queue 우선순위, Canvas·3D Shot Composer·MCP 제품 존재. Newtake 약관의 robot/scraper 금지 조항과 API 부재도 원문으로 확인 — ADR-001의 비교표는 사실에 부합한다.
- 수정할 것: §12.1의 Canvas 3D blocking 오귀속(CLD-015), `/user/credit/detail` 경로 재확인(CLD-021), 실패 과금 규칙의 pilot 측정 항목화(CLD-022), TOPVIEW_CANVAS mode의 재분류(CLD-015).
- 유지 조건: ADR-001의 Required safeguards(월간 pilot 한정, 연간·Unlimited 선구매 금지, 즉시 다운로드+checksum)는 전부 실측 전 필수로 유지한다. 모델별 강점 가설(§12.4)은 provider 마케팅이 아니라 pilot 실측으로만 보정한다는 원칙도 유지.

## 6. 단순화할 수 있는 항목 5개

1. **Remotion/FFmpeg 이중 runtime 선택 로직(§14, §15.2) 제거** — Golden Pilot 범위에서는 HyperFrames 단일 runtime을 사용자 승인으로 잠그면 충분하다. "동등한 contract를 Remotion으로 구현"은 지금 아무도 만들지 않을 코드의 명세다. 결정 기록만 남기고 v2 본문에서 뺀다.
2. **Visual Grammar 18개 → 6개** — 두 golden test가 실제로 사용하는 것은 archive_to_reality, evidence_to_reconstruction, freeze_to_explain, document_zoom, wide_medium_close, heritage_forge 정도다. 나머지 12개는 각 12개 필수 필드를 채우는 저작 비용만 만든다. 이름 목록만 남기고 정의는 필요할 때 작성.
3. **Director Memory(§9) 전체를 Phase 5로 이연** — Golden Pilot 1편에는 학습할 이력 자체가 없다. 지금은 스키마도 저장소도 필요 없다.
4. **visual-plan 내부 approval 객체 제거(CLD-009와 동일 수정)** — 승인은 checkpoint 한 곳에만 둔다. 스키마가 작아지고 이중 진실이 사라진다.
5. **TOPVIEW_CANVAS provider mode 제거(CLD-015와 동일 수정)** — Canvas 산출물은 수동 ingest로 통일. provider 상태 기계가 자동 경로에만 적용되어 어댑터 구현이 단순해진다.
6. (보너스) **multi-LLM adapter 비교(§10, Phase 4 "cross-model benchmark")를 pilot 이후로** — 첫 pilot은 adapter 1개로 끝내고, 비교는 Golden Test 점수 체계가 재현 가능해진 뒤에 한다.

## 7. Codex에 물어볼 질문

1. CLD-001: scene_plan 스키마 사본 없이 compiler 계약을 검증할 다른 방법을 찾았는가? 로컬 OpenMontage HEAD와 upstream의 차이를 확인했는가?
2. CLD-002: overlay 내용(payload) 부재를 발견했는가? 발견했다면 어떤 최소 스키마를 제안하는가 — `overlay.items[]` 안과 비교해 달라.
3. CLD-006: HYBRID 분리(contains_ai) 대 라벨 어휘 통제 — 어느 쪽이 더 작은 계약이라고 보는가?
4. CLD-007: 편집 이후 컷의 최종 권위를 edit_decisions로 두는 데 동의하는가? VisualPlan의 편집 필드를 '계획 가설'로 격하하는 것의 부작용이 있는가?
5. CLD-014: Bangjja 85점의 항목별 배점을 독립적으로 정의했는가? 정의했다면 두 배점표를 합치자.
6. CLD-022: 실패 generation의 과금 여부를 공식 문서 또는 실측으로 확인했는가?
7. CLD-003: GATE_FINAL_EDIT 강제를 custom manifest와 approval artifact 중 무엇으로 권하는가? upstream 호환성 비용을 어떻게 평가했는가?
8. 스키마의 `additionalProperties: false`(visual-plan 전면 적용)가 LLM adapter의 출력 안정화에 도움이 된다고 보는가, 아니면 사소한 필드 추가마다 schema version bump를 강제해 해가 된다고 보는가?

## 8. 최종 판정

**`DESIGN_NOT_READY`**

근거: BLOCKER 3건(CLD-001, 002, 003)이 설계 자신의 Acceptance criteria와 직접 충돌한다 — criteria 4(우회 없는 Human Gate)는 upstream manifest 실물로 미충족이 확인됐고, criteria 9(측정 가능한 Golden Test)는 CLD-008·014로 부분 미충족이며, criteria 1(schema로 Hyatt 표현 가능)은 overlay payload 결손(CLD-002) 때문에 "통과하되 핵심 내용이 비어 있는" 상태다.

단, 세 BLOCKER 모두 아키텍처 변경 없이 v2에서 해결 가능하다(스키마 사본 커밋, overlay 필드 추가, manifest/artifact 1개 정의). 전체 구조 — IR+compiler, Evidence Layer, clean plate, provider 추상화 — 는 건전하며, 외부 사실 검증에서 설계 문서의 주장 대부분이 정확했다는 점을 명시적으로 기록한다. BLOCKER 해소 후 재판정 시 `READY_FOR_IMPLEMENTATION_REVIEW` 도달이 현실적이다.

---

*이 리뷰는 어떤 Human Gate도 승인하지 않으며, 설계 파일을 수정하지 않았다. 검증 스크립트와 Hyatt dry-run plan은 재현 가능하도록 리뷰어 세션에 보존되어 있다.*
