# MK Visual Director Final Design v2 (Candidate)

## Document status

- Version: 2.0 (candidate)
- Date: 2026-08-11
- Status: **READY_FOR_USER_GATE**
- Implementation: NOT AUTHORIZED
- Paid production calls: NOT AUTHORIZED
- Final render or publication: NOT AUTHORIZED
- 선행 문서: [v1](MK_VISUAL_DIRECTOR_FINAL_DESIGN_v1.md)은 보존한다. 이 문서는 [`reviews/final-consensus.md`](../reviews/final-consensus.md)에 합의된 변경만 v1에 반영한 후속 candidate다.

`READY_FOR_USER_GATE`는 구현 승인이 아니다. 사용자 Human Gate 승인 전에는 구현·유료 생성·최종 렌더·공개를 시작하지 않는다.

## Stage 4 첨부 (runbook 의무 항목)

### 변경 요약

1. VisualPlan schema **2.0.0** 신설([`visual-plan.v2.schema.json`](../schemas/visual-plan.v2.schema.json), v1 schema 보존): typed `overlay.items[]`와 claim binding, `script_ref`/`script_sha256`, `contains_ai`와 disclosure 불변식, approval 객체 → `gate_ref`, 조건부 camera/lighting, `estimated_credits`, route enum 정리, `match_anchors`.
2. OpenMontage 기준선을 [`vendor/openmontage/contract-lock.json`](../vendor/openmontage/contract-lock.json)으로 고정(전체 사본 vendoring 대신 — upstream AGPL-3.0).
3. Human Gate 강제 메커니즘 명세: edit/compose용 custom manifest + GATE_TITLE_THUMBNAIL용 approval artifact (§19).
4. Compiler를 loss-accounting 계약으로 정의하고 representation→scene type 매핑 표 추가 (§5.1).
5. 편집 이후 artifact 권위 순서 명문화: `edit_decisions`가 컷의 최종 권위 (§16.4).
6. Beat map을 canonical artifact로 승격, ±2 frames·anchor 3% 측정 절차를 golden test에 명기.
7. 참사·인명 피해 묘사의 편집 윤리 경계 추가 (§17.1).
8. `HERITAGE_FORGE.yaml` 1.0.1 데이터 결함 수정, Bangjja 항목별 배점표 추가, Hyatt synthetic fixture 명시.
9. 단순화 8건 반영: 단일 runtime pilot, grammar 우선순위 축소, Director Memory 이연 등 (§3.1).

### 해결한 finding ID

- BLOCKER 해소(v2 계약 반영 + fixture 통과): CLD-002, CDX-X-002, CLD-003(명세 확정; 구현 검증은 Phase 1), CDX-001
- HIGH: CLD-001(PARTIAL→contract lock), CLD-004/CDX-003, CLD-005, CLD-006/CDX-004/CDX-X-001, CLD-007, CLD-008
- MEDIUM: CLD-009, CLD-010, CLD-011/CDX-002(계약 명세; 구현은 Phase 1), CLD-012, CLD-013, CLD-014/CDX-007, CLD-015, CLD-016, CLD-017
- LOW: CLD-018, CLD-019, CLD-020, CLD-023, CDX-006
- RESOLVED(변경 불요): CLD-021

### 남은 위험

1. **CLD-022/CDX-005 (NEEDS_EVIDENCE)**: 실패 generation 과금은 endpoint별 실측 전까지 미확정 — Phase 3 pilot 측정 항목.
2. CLD-003의 명세는 확정됐지만 **실행 증거(edit checkpoint가 `awaiting_human`에서 정지하는 dry-run)는 Phase 1 구현에서 확보**된다.
3. semantic validator는 규칙 목록만 확정된 상태다. 오류 코드·구현은 Phase 1이다.
4. HYBRID `contains_ai`의 component provenance 파생은 asset manifest가 생기는 Phase 1 이후에만 완전 검증된다. 그 전에는 schema 불변식(AI_RECONSTRUCTION→true)만 강제된다.
5. 85점 총점 기준은 pilot 2회 calibration 전까지 참고 지표다.

### Schema version 변경

- visual-plan: **1.0.0 → 2.0.0 (breaking)**. v1 schema와 v1 예제는 보존.
- source-registry: **1.0.0 유지** — 합의된 보강(supports 인용·excerpt hash 요건, rights_basis 일반화)은 semantic validator 규칙으로 구현 (§20.1).

### Golden Test 변경

- Hyatt: synthetic contract fixture 명시, v2 schema·typed overlay 계약 항목 추가, 측정 절차 3건(anchor 3%, ±2 frames, 주관 기준 판정 규약) 추가.
- Bangjja: 28개 항목별 배점표와 부분점 규칙 추가, 합격 조건을 `blocker 0 + 영역 하한 필수, 총점 85 참고`로 변경.

### Phase 1 범위

§23 참조. 핵심 산출물: semantic validator(오류 코드 고정), VisualPlan→scene_plan compiler(loss-accounting test 포함), `mk-hybrid.yaml` manifest와 gate 정지 dry-run 증거, title/thumbnail approval artifact, contract lock 검증 CI, placeholder animatic. 유료 생성 없음.

---

## 1. Objective

목표는 특정 LLM이나 특정 영상 생성 모델에 종속되지 않는 시네마틱 다큐멘터리 제작 시스템이다. (v1 §1과 동일 — 9단계 수행 목록 유지)

## 2. Non-negotiable principles

### 2.1 Meaning before camera — v1과 동일

### 2.2 Sequence before Shot — v1과 동일

### 2.3 Clean plate — v1과 동일

생성 영상에는 정확한 글자, 날짜, 수치, 화살표, 로고, 도면 설명을 넣지 않는다. 정확한 표시 내용은 **typed overlay payload**로만 존재한다 (§2.5).

### 2.4 Evidence and reconstruction separation (개정 — CLD-006, CDX-X-001)

모든 화면은 다음 중 하나로 분류한다.

- REAL: 실제 사진·영상·문서·도면
- AI_RECONSTRUCTION: 사실에 근거한 AI 재현
- GRAPHIC: 설명 그래픽·지도·타임라인
- HYBRID: 서로 다른 표현의 합성(실제+그래픽, 실제→AI 전환 등)

representation과 별도로 모든 shot은 `contains_ai: boolean`을 갖는다.

- `AI_RECONSTRUCTION`은 항상 `contains_ai=true` (schema 강제).
- HYBRID의 `contains_ai`는 자기신고가 아니라 component provenance에서 파생하며, semantic validator가 일관성을 검사한다: 구성 요소 중 하나라도 generated/reconstructed이면 true.
- **Disclosure는 `contains_ai=true`일 때만 강제**된다. AI가 없는 실제 자료+그래픽 화면에 AI 라벨을 붙여 표시의 변별력을 희석하지 않는다.
- 라벨은 자유 텍스트가 아니라 통제 어휘다: `AI 재현`, `AI 재현 + 설명 그래픽`(contains_ai=true), `실제 자료 + 설명 그래픽`(선택적, 비AI HYBRID).

### 2.5 Exact text is claim-bound (신설 — CLD-002, CDX-X-002)

화면에 표시되는 모든 정확한 텍스트·수치·도면 라벨은 VisualPlan의 `overlay.items[]`에 typed payload로 존재해야 하며:

- `exact_text_from_claims=true`인 item은 `claim_id` 바인딩이 필수다 (schema 강제).
- 렌더 값은 claim의 canonical/localized value에서 resolve한다. literal을 병기하면 claim 값과 일치해야 한다 (semantic 검사).
- unbound literal은 비사실적 카피(제목·브랜드)에만 허용된다.
- 다국어는 `text_key + locale`로 해결한다.

### 2.6 Local source of truth — v1과 동일

### 2.7 Human Gates — v1 §2.6과 동일 (9개 gate 목록 유지)

## 3. Scope and non-goals

v1 §3과 동일하되, 다음이 initial scope에서 **명시적으로 제외**된다.

### 3.1 단순화로 제외·이연된 항목 (final-consensus §3)

1. Remotion 동등 contract 구현 명세 — runtime 사용자 선택 gate는 유지하되, Golden Pilot은 사용자 승인으로 HyperFrames 단일 runtime을 잠근다.
2. Visual Grammar 18종 전체 정의 — golden test가 실제 선택하는 `EVIDENCE_TO_RECONSTRUCTION`, `FREEZE_TO_EXPLAIN`, `HERITAGE_FORGE`만 우선 정의하고 나머지는 이름 목록으로 유지.
3. Director Memory 전체 — Phase 5로 이연 (v1 §9는 v2 본문에서 제거).
4. VisualPlan 내부 approval 객체 — `gate_ref`로 축소 (§19).
5. `TOPVIEW_CANVAS`·`OPENMONTAGE_ONLY` route mode — 제거 (§11, §12).
6. TopView pilot endpoint — 실제 필요한 2–3개만 contract fixture로 구현, 나머지 unsupported.
7. 첫 pilot 범위 — synthetic fixture + 720p review build까지. publish automation·최종 1080p 제외.
8. Multi-LLM adapter 비교 — 채점 체계 calibration 이후로 이연.

## 4. System architecture

v1 §4의 파이프라인 다이어그램에서 한 곳 변경: PRODUCTION ROUTER의 분기는 다음과 같다.

~~~text
PRODUCTION ROUTER
   ├─ REAL → ingest and normalize (TopView Canvas 산출물 포함: manual ingest + provenance)
   ├─ VIDEO → TopView API / local LTX
   └─ GRAPHIC/OVERLAY → HyperFrames
~~~

## 5. Canonical project artifacts

v1 §5의 표에 다음을 추가·변경한다.

| Artifact | Owner | Purpose |
|---|---|---|
| (v1 표 전체 유지) | | |
| **beat_map** (신설) | OpenMontage canonical sidecar | `{event_id, type, time_seconds}` 이벤트 목록 — 내레이션 clause·music beat·SFX transient·impact·title reveal의 단일 타이밍 기준 (CLD-008) |
| **vendor/openmontage/contract-lock.json** (신설) | 이 저장소 | upstream 계약 기준선: commit·blob·SHA-256·검증 명령 (CLD-001) |
| **title-thumbnail-approval.json** (신설) | OpenMontage artifacts/ | GATE_TITLE_THUMBNAIL 승인 기록 (§19) |

VisualPlan의 기계 검증 계약은 [`visual-plan.v2.schema.json`](../schemas/visual-plan.v2.schema.json)이다. v2 예제: [valid(Hyatt 2·3·7 typed overlay)](../examples/visual-plan.v2.hyatt-overlay.valid.json), [literal 우회 negative](../examples/visual-plan.v2.invalid-literal-bypass.json), [미표시 AI negative](../examples/visual-plan.v2.invalid-undisclosed-ai.json), [AI flag 모순 negative](../examples/visual-plan.v2.invalid-ai-flag-contradiction.json).

### 5.1 OpenMontage compatibility rule (개정 — CLD-004, CDX-003)

VisualPlan은 scene_plan을 대체하지 않는 IR이다. deterministic compiler가 contract lock으로 고정된 scene_plan schema로 변환한다.

**Representation → scene type 매핑 (규범):**

| VisualPlan | 조건 | scene_plan `type` |
|---|---|---|
| REAL | 사진·영상·문서 ingest | `broll` |
| AI_RECONSTRUCTION | — | `generated` |
| GRAPHIC | DIAGRAM/CALLOUT 중심 | `diagram` |
| GRAPHIC | 텍스트 카드 중심 | `text_card` |
| HYBRID | `contains_ai=true` | `generated` (base layer 기준) |
| HYBRID | `contains_ai=false` | `broll` (base layer 기준) |
| coverage_role=transition | — | `transition` |

**Loss-accounting 계약:** 모든 VisualPlan 필드는 다음 네 소비처 중 하나에 배정된다 — `scene field로 컴파일 | scene_plan.metadata로 이관 | QC가 visual-plan을 직접 소비 | 정당화된 drop`. `disclosure`, `evidence_ids`, `overlay`는 **drop 금지 집합**이다. scene 객체는 닫힌 계약이므로 shot-level 세부는 top-level `metadata.shots[<scene_id>]` 관례로 이관하고, **Media QC와 Factual QC는 scene_plan이 아니라 visual-plan.json을 직접 읽는다.** 모든 shot_id는 scene_id 또는 `metadata.shot_id_map`에 존재해야 한다.

`scene_plan.metadata`에는 최소한 `visual_plan_ref`, `visual_plan_sha256`, `visual_plan_schema_version`, `shot_id_map`을 남긴다. VisualPlan 변경 시 scene plan은 수동 편집이 아니라 compiler 재실행으로 동기화한다.

## 6. Evidence Layer

v1 §6과 동일. 다음 semantic validator 규칙이 추가로 계약에 포함된다 (CLD-016, 스키마는 1.0.0 유지):

1. evidence_lock 승인 시 sources ≥ 1, claims ≥ 1.
2. `status=verified` claim은 `supports` 인용 ≥ 1, 그중 `excerpt_sha256` non-null ≥ 1.
3. source_type과 credibility_tier의 허용 조합 표 (예: `community`는 tier 4–5만).
4. `rights.status=verified`는 `license non-null`이 아니라 **`rights_basis`(license | public_domain | direct_permission | fair_use_reviewed) + 근거 locator + local copy/checksum** 조건으로 검증한다.

## 7. MK Visual Director — v1 §7과 동일 (semantic analysis, sequence 15–60초 원칙, shot planning, coverage rules)

15–60초 규칙은 hard error가 아니라 semantic warning + waiver reason으로 검사한다 (CLD-023).

## 8. Visual Grammar — v1 §8과 동일하되 §3.1의 우선순위 축소 적용

`HERITAGE_FORGE` 1.0.1: 토큰 오타 수정, fallback 키를 failure_patterns와 1:1 정렬, required coverage에 `evidence_insert` 추가 (CLD-018).

## 9. Director Memory — Phase 5로 이연 (§3.1)

v1 §9의 Store/Do-not-store 원칙은 Phase 5 설계 시 그대로 계승한다.

## 10. LLM independence — v1 §10과 동일

cross-model 비교는 채점 calibration 이후로 이연 (§3.1).

## 11. Production Router

### 11.1 Routing decision (개정)

~~~text
exact historical evidence exists
→ REAL or REAL+GRAPHIC

precise numbers, text, diagram, map
→ HyperFrames (typed overlay.items[])

cinematic reconstruction required
→ image master + TopView API video

layout or camera blocking uncertain
→ TopView Canvas 또는 3D Shot Composer에서 수동 탐색 후 결과를 manual ingest

low-cost draft
→ local image + local LTX

sensitive or unpublished source
→ local provider only
~~~

route mode enum은 `REAL_INGEST | TOPVIEW_API | LOCAL_LTX | HYPERFRAMES` 4종이다. Canvas는 수동 작업 공간이므로 자동 라우팅 대상이 아니고(CLD-015), 산출물은 provider provenance metadata를 가진 `REAL_INGEST` 계열 manual ingest로 들어온다. `OPENMONTAGE_ONLY`는 제거됐다(CLD-020).

### 11.2 Provider interface — v1과 동일 + 비용 추정

유료 cost_tier(draft/standard/premium)의 shot은 `estimated_credits`가 필수다(schema 강제, CLD-013). 예상치는 GATE_BUDGET의 cost snapshot으로 합산되고, 실측 `costCredit`과 cost ledger에서 대조한다. provider별 단가 의미는 정규화하지 않는다.

### 11.3 Normalized state mapping — v1과 동일 (raw_status·raw_response·error_code·costCredit 보존)

공통 정규화 대상은 상태 5종·비용 수치·파일 URL·타임스탬프로 한정한다. 모델별 파라미터·오류 코드 체계·cancel 지원은 endpoint-specific으로 두고 raw를 보존한다 (CDX-005).

## 12. TopView integration

v1 §12와 동일하되 다음 수정 (ADR-001 Amendments 참조):

- **12.1**: 3D blocking은 Canvas가 아니라 **3D Shot Composer**의 기능이다. Canvas 용도는 스타일 탐색·후보 비교·씬 구성이며, 승인 결과는 즉시 로컬로 내려받아 shot_id로 개명하고 manual ingest로 등록한다.
- **12.2 Billing boundary**: 확인된 공식 사실 — 웹·API 크레딧 공유, **Ultra 크레딧은 API 사용 불가**, 결과 URL **7일 유효**. 실패 시 과금은 endpoint별 실측 항목 (CLD-022).
- **12.4**: 모델 라우팅 원칙 유지. pilot은 2–3개 endpoint로 한정.

## 13. Image master stage — v1과 동일

텍스트 overlay가 필요한 경우 레이아웃은 overlay item의 `position_hint`·`safe_area`로 계획하고 이미지를 그에 맞춰 생성한다.

## 14. HyperFrames

8개 초기 모듈(v1 목록)은 overlay item의 `module` enum과 1:1이다. Required behavior(v1)에 추가:

- overlay item의 claim resolve: `claim_id → canonical/localized value` 렌더링
- literal 병기 시 claim 값과의 일치 실패는 렌더 거부

runtime 선택 gate는 유지하되 Golden Pilot은 HyperFrames 단일 runtime을 사용자 승인으로 잠근다 (§3.1). Remotion 동등 contract 명세는 v2 범위에서 제외됐다.

## 15. OpenMontage — v1과 동일 + contract lock

기준 계약(stage 목록, checkpoint enum, artifact 목록)은 문서 서술이 아니라 [`vendor/openmontage/contract-lock.json`](../vendor/openmontage/contract-lock.json)이 고정한 upstream 커밋 `4eab34c5…`의 실물 파일이다. lock 검증 실패 시 compiler·gate 작업을 중단한다.

## 16. Audio and edit grammar

### 16.1 End anchor edit — v1과 동일

### 16.2 Beat map (개정 — CLD-008)

beat map은 canonical artifact다. 최소 스키마:

~~~text
beat_map.json
  events[]:
    event_id: string (예: BEAT_DATE_CLAUSE)
    type: narration_clause | music_beat | music_section | sfx_transient |
          action_impact | title_reveal | silence
    time_seconds: number
~~~

VisualPlan `audio_layers[].sync_event`와 golden test의 ±2 frames 검사는 이 artifact의 `event_id`·`time_seconds`를 기준으로 한다.

### 16.3 Cut policies — v1과 동일 (±2 frames 검사 포함)

### 16.4 Artifact authority after edit (신설 — CLD-007)

컷·타이밍·runtime의 최종 권위는 `edit_decisions`다. VisualPlan의 edit_trigger·transition 필드는 **GATE_ANIMATIC까지의 계획 가설**이며, 편집 단계 이후의 차이는 자동 역수정 없이 `{planned, actual, reason, actor, decided_at}` divergence report로 기록한다. Golden Test의 편집 측정은 실제 `edit_decisions` 기준이다.

경계 transition의 소유 규칙(CLD-019): 시퀀스 경계는 sequence의 entry/exit_transition이 소유하고, 첫 shot의 `transition_in`과 마지막 shot의 `transition_out`은 `none`이어야 한다 (semantic 검사).

## 17. REAL + AI + GRAPHIC mixing — v1 §17과 동일 (비율 가설 유지: pilot 관측 기준)

### 17.1 인명 피해 묘사의 편집 윤리 경계 (신설 — CLD-017)

disclosure(AI 표시)와 별개의 계약이다.

1. 인명 피해 순간의 사실적 AI 재현은 금지한다. 재현은 구조·역학·공간·시간 관계 중심으로 한다.
2. 특정 실존 피해자를 식별 가능하게 재현하지 않는다.
3. 불확실한 사실은 화면·내레이션 모두에서 단정하지 않고 불확실성을 표시한다.
4. Factual QC에 해당 검사 항목을 둔다 (§20.3).

## 18. Project folder structure — v1과 동일 + 추가 파일

~~~text
projects/<project-id>/artifacts/
  (v1 목록 유지)
  beat-map.json
  title-thumbnail-approval.json
repo 루트:
  vendor/openmontage/contract-lock.json
~~~

## 19. Human Gate mapping (개정 — CLD-003, CDX-001, CLD-009/010)

### 승인의 단일 기록처

승인 상태·행위자·시각은 **OpenMontage checkpoint에만** 기록한다. VisualPlan은 `gate_ref {gate, checkpoint_path}`로 참조만 하며 자체 approval 상태를 갖지 않는다. 거절·수정요청의 행위자도 checkpoint decision record에 남는다(CLD-010). 어떤 에이전트도 `human_approved=true`를 추정하거나 생성해서는 안 된다.

### Gate 강제 메커니즘 (v1의 "pipeline 확장 필요"를 구체화)

1. **`mk-hybrid.yaml` custom manifest (Phase 1 산출물)**: upstream `hybrid.yaml`을 기반으로 하되 `edit`·`compose` stage의 `human_approval_default`를 **true**로 설정한다. checkpoint schema의 `human_approval_required`/`human_approved`는 upstream에 이미 존재하므로 새 계약 표면이 없다. 이것이 GATE_FINAL_EDIT의 강제 방식이다.
2. **GATE_TITLE_THUMBNAIL**: 대응 stage가 없으므로 approval artifact로 강제한다. `artifacts/title-thumbnail-approval.json` 최소 스키마: `{gate: "GATE_TITLE_THUMBNAIL", status: awaiting_human|approved|rejected, decided_by, decided_at, title_ref, thumbnail_ref, notes}`. **작성 주체는 사용자 승인 UI/CLI 단일 경로**이며, publish stage 진입 조건에 이 artifact의 `approved`를 포함한다.
3. Phase 1 acceptance: 승인 기록 없는 review build로 compose 진행을 시도하는 contract test가 실패해야 하고, edit checkpoint가 `awaiting_human`에서 정지하는 dry-run 증거를 남긴다.

### Gate-to-stage mapping

v1 표를 유지하되 GATE_FINAL_EDIT 행은 `mk-hybrid.yaml의 edit/compose human gate`, GATE_TITLE_THUMBNAIL 행은 `title-thumbnail-approval.json`으로 대체한다.

## 20. QC (개정 — owner 배정: CLD-023)

| QC 계층 | Owner | 입력 |
|---|---|---|
| 20.1 Data QC | **semantic validator** (Phase 1 계약) | visual-plan, source-registry, beat map, contract lock |
| 20.2 Media QC | **OpenMontage** | 실제 미디어 파일 + **visual-plan.json 직접 소비** |
| 20.3 Factual QC | **semantic validator(기계 검사) + 리뷰어(판정)** | claim ledger, overlay items, 렌더 프레임 |
| 20.4 Editorial QC | **리뷰어(Claude/Codex) + 사용자** | review build |

### 20.1 Data QC — validator 계약 (CLD-011, CDX-002, CLD-016)

- 툴체인 고정: JSON Schema Draft 2020-12, **AJV 8.x + `ajv-formats`**, strict-mode 정책과 버전을 Phase 1에서 고정하고 CI에 (a) 잘못된 date/date-time fixture, (b) schema 컴파일 fixture를 둔다. (참고: Python jsonschema 기본 설정은 format을 검증하지 않는다 — 교차검수에서 실증됨.)
- 오류 코드를 고정한 deterministic semantic validator. 최소 규칙: cross-file referential integrity(evidence_ids ↔ registry, sync_event ↔ beat map, grammar id ↔ grammar registry), 전역 ID 유일성, `narration start < end`, shot 합계 vs sequence target 허용 오차, script_sha256 freshness, scene plan checksum freshness, 경계 transition 소유(§16.4), 15–60초 warning+waiver, HYBRID contains_ai provenance 일관성, literal-claim 일치, 유료 shot의 estimated_credits, §6의 registry 규칙 4건.
- v1의 나머지 항목 유지.

### 20.2 Media QC — v1과 동일

### 20.3 Factual QC — v1과 동일 + 추가 2건

- 모든 표시 텍스트·수치가 overlay item의 claim_id로 역추적된다 (CLD-002).
- 인명 피해 순간의 사실적 재현이 없다 (§17.1).

### 20.4 Editorial QC — v1과 동일

## 21. Failure and fallback — v1과 동일

## 22. Golden Tests

- [Hyatt 60–90s](../golden-tests/HYATT-60-90S-GOLDEN-SEQUENCE.md): synthetic contract fixture 명시, v2 typed overlay 계약, 측정 절차 3건 반영.
- [Bangjja style](../golden-tests/BANGJJA-STYLE-ACCEPTANCE-TEST.md): 항목별 배점표(영역 합계 20점), 합격은 blocker 0 + 영역 하한, 총점 85는 calibration 전 참고.

## 23. Implementation phases (개정)

### Phase 0: design cross-review — **완료** (독립검수 2건, 교차검수 2건, final-consensus, 본 v2 candidate). 남은 것: 사용자 Human Gate.

### Phase 1: contracts and local dry run

- semantic validator (§20.1 규칙, 오류 코드 고정, AJV 툴체인 CI)
- VisualPlan v2 → scene_plan compiler + **loss-accounting test** (§5.1)
- contract lock 검증 CI (§15)
- **`mk-hybrid.yaml` manifest + gate 정지 dry-run 증거** (§19)
- title-thumbnail approval artifact 구현
- beat map artifact 스키마
- Source Registry·Claim Ledger·Visual Grammar loader (우선 grammar 3종)
- placeholder animatic. **유료 생성 없음.**

### Phase 2: HyperFrames core — v1과 동일 + overlay item claim resolve (§14)

### Phase 3: TopView pilot adapter — v1과 동일 + endpoint 2–3개 한정, 실패 과금 실측 fixture (CLD-022)

### Phase 4: Golden Pilot — v1과 동일 (720p review build까지, cross-model benchmark는 calibration 이후)

### Phase 5: production hardening + Director Memory 설계

## 24. Acceptance criteria (재판정 현황)

| # | 기준 | v2 상태 |
|---|---|---|
| 1 | schema로 Hyatt Golden Sequence 표현 가능 | **충족** — 구간 2·3·7 typed overlay fixture가 v2 schema를 통과 (examples/) |
| 2 | REAL/AI/GRAPHIC 경계·표기 규칙 합의 | **충족** — contains_ai + 통제 어휘 (§2.4) |
| 3 | TopView billing 경계 반영 | **충족** — 공식 확인 사실 반영 (§12.2), 실패 과금은 pilot 실측 |
| 4 | Human Gate 우회 상태 전이 없음 | **명세 충족, 실행 증거는 Phase 1** — mk-hybrid manifest + approval artifact (§19) |
| 5 | 즉시 로컬 보존·checksum 규칙 | 충족 (v1 유지) |
| 6 | clean plate·overlay 독립 재렌더 | 충족 (v1 유지 + typed payload로 강화) |
| 7 | license·provenance 기록 | 충족 (v1 유지 + rights_basis 일반화) |
| 8 | adapter와 공용 grammar 분리 | 충족 (v1 유지) |
| 9 | Golden Test pass/fail 측정 가능 | **충족** — 배점표 + 측정 절차 (golden-tests/) |
| 10 | OpenMontage canonical 충돌 없음 | **충족** — contract lock으로 검증 가능 (§15) |
| 11 | runtime·composition 잠금 | 충족 (v1 유지, pilot은 HyperFrames 잠금 제안) |
| 12 | 사용자 Final Design v2 명시 승인 | **대기 — READY_FOR_USER_GATE** |

## 25. Sources and evidence date

v1 §27의 출처 목록 유지. 추가 확인(2026-08-11, 교차검수):

- https://github.com/calesthio/OpenMontage (commit `4eab34c5cfcccaa4f1970554928feccce73ee930`, AGPL-3.0)
- https://docs.topview.ai/reference/query_user_credit (`GET /user/credit/detail`)
- https://docs.topview.ai/docs/billing-rules (크레딧 공유, Ultra API 불가)
- https://docs.topview.ai/docs/concurrency-and-storage (URL 7일 유효)
