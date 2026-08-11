# Final Consensus — MK Visual Director Design v1 교차검수 합의안 (Stage 3)

- Date: 2026-08-11
- Drafted by: Claude (Fable 5), PR #1의 Codex Stage 2 cross-review를 기준으로 작성
- Inputs: `claude-independent-review.md`, `codex-independent-review.md`, `claude-cross-review.md`, `codex-cross-review.md`(PR #1)
- 상태: **Codex ACK 대기 → 사용자 Human Gate 대기.** 이 문서는 어떤 gate도 승인하지 않는다.

## 0. 합의 전 상호 재검증

runbook 규칙 4("의견 차이는 평균내지 않고 evidence로 판정")에 따라, Claude는 Codex Stage 2의 결정적 증거를 독립 재검증했다. **전부 사실로 확인됐다.**

| Codex 주장 | Claude 재검증 결과 |
|---|---|
| upstream 고정 커밋 `4eab34c5…`의 세 계약 파일 blob | GitHub API로 확인 — `scene_plan.schema.json` `751665bf…`, `checkpoint.schema.json` `1249c8f0…`, `hybrid.yaml` `b46dd642…` 모두 Codex 표와 일치 |
| `GET /user/credit/detail` 경로 실재 | docs.topview.ai/reference/query_user_credit의 OpenAPI 정의에서 확인 — CLD-021에 대한 Codex의 REJECT가 옳다 |
| OpenMontage는 AGPL | GitHub license API로 `agpl-3.0` 확인 — 전체 사본 vendoring 대신 경량 contract lock을 권한 근거가 유효하다 |

이에 따라 Claude는 CLD-001의 BLOCKER→PARTIAL 하향과 CLD-021의 REJECT를 **수용한다.** Stage 2 이후 양측 사이에 사실 관계 다툼은 남아 있지 않다.

## 1. 합의 표

Disposition 규칙: `BLOCKER`는 해결되거나 사용자가 명시적으로 위험을 수락해야 닫힌다. `RESOLVED`는 추가 조치 불요. Owner는 해결 산출물 기준.

| Finding | Claude | Codex | Evidence | Final disposition | Owner | Target version |
|---|---|---|---|---|---|---|
| Overlay payload·claim binding 부재 | CLD-002 BLOCKER | BLOCKER (fixture 재현) + CDX-X-002 | typed payload 추가 시 `additionalProperties:false`로 INVALID, 자유 텍스트는 opaque 우회 (fixture SHA 기록됨) | **BLOCKER — OPEN** | schema v2 (`overlay.items[]` + literal-bypass 금지 규칙) | visual-plan schema 2.0.0 |
| Final-edit·title/thumbnail gate 미강제 | CLD-003 BLOCKER | CDX-001 BLOCKER | `hybrid.yaml` edit/compose `human_approval_default:false` — 로컬·upstream blob 동일 확인 | **BLOCKER — OPEN** | v2 문서 + MK custom manifest 명세 + title/thumbnail approval artifact 최소 스키마 | Design v2 + Phase 1 |
| OpenMontage 기준선 재현 불가 | CLD-001 BLOCKER | PARTIAL (blob 동일성 증명) | 세 파일이 upstream `4eab34c5…`와 blob·SHA-256 동일 (양측 검증); AGPL로 전체 사본은 부담 | **PARTIAL → HIGH.** `vendor/openmontage/contract-lock.json`(upstream URL·commit·path·blob·SHA-256·license·검증 명령)으로 해결 | v2 | Design v2 |
| Compiler 매핑·정보 손실 | CLD-004 HIGH | CDX-003 → ACCEPT | scene 객체 닫힌 계약 + representation 자연 대응 없음 (upstream 실물) | **HIGH — 합의.** 필드별 loss-accounting 표(`compile | metadata 이관 | QC 직접 소비 | 정당화된 drop`) + drop 금지 집합 + shot_id 보존 불변식 | Phase 1 compiler 계약 | Phase 1 (CLD-002·contract lock 선행) |
| script_ref/sha256 부재 | CLD-005 HIGH | ACCEPT | 스키마에 대본 참조 필드 전무 — stale plan 감지 불가 | **HIGH — 합의** | schema v2 (top-level 필수 필드) | visual-plan schema 2.0.0 |
| HYBRID 과적재·disclosure 희석 | CLD-006 HIGH | CDX-004 + CDX-X-001, severity HIGH 동의 | valid 예제가 AI 없는 HYBRID에 라벨 강제 | **HIGH — 합의.** `contains_ai`는 자기신고 boolean이 아니라 component provenance에서 파생·검증(AI_RECONSTRUCTION→항상 true), 라벨은 통제 어휘 | schema v2 + validator | visual-plan schema 2.0.0 |
| Edit 이후 권위 순서 | CLD-007 HIGH | ACCEPT | End-anchor edit은 재배열 전제 — 충돌 필연 | **HIGH — 합의.** `edit_decisions`가 컷 최종 권위, VisualPlan edit 필드는 GATE_ANIMATIC까지 계획 가설, 차이는 `{planned, actual, reason, actor, decided_at}` divergence report | v2 문서 | Design v2 |
| ±2 frames·anchor 3% 측정 구조 부재 | CLD-008 HIGH | ACCEPT | sync_event 자유 문자열, 좌표 필드 없음, beat map artifact 미정의 | **HIGH — 합의.** beat-map canonical artifact + 정규화 좌표 + 측정 절차 명문화, 측정 기준은 실제 `edit_decisions` | v2 + golden-tests | Design v2 |
| 승인 이중 진실·전이 규칙 부재 | CLD-009/010 MEDIUM | ACCEPT | self-approval·상태 모순 probe 통과, rejected 주체 기록 불가 | **MEDIUM — 합의.** visual-plan approval을 `gate_ref`로 축소, 승인 기록은 checkpoint 단일화(거절 주체 문제도 함께 해소) | schema v2 | visual-plan schema 2.0.0 |
| Validator 툴체인 미고정 | CLD-011 MEDIUM | ACCEPT + 신규 증거 | Python jsonschema 기본 설정은 date-time 미검증; **AJV 8 strict-mode는 현 스키마 컴파일 거부**(conditional minItems) — 도구별 결과가 실제로 갈렸다 | **MEDIUM — 합의.** Phase 1 계약에 AJV 버전·`ajv-formats`·strict 정책 고정 + 잘못된 날짜·컴파일 fixture CI | Phase 1 validator 계약 | Phase 1 |
| GRAPHIC 숏의 허구 camera/lighting | CLD-012 MEDIUM | ACCEPT | dry-run에서 허구 값 강제 확인 | **MEDIUM — 합의.** representation+route 조건부 required | schema v2 | visual-plan schema 2.0.0 |
| 예산 수치 필드 부재 | CLD-013 MEDIUM | ACCEPT | cost_tier enum만 존재 | **MEDIUM — 합의.** `estimated_credits` + quote 시점·실측을 잇는 cost ledger, provider별 단가 의미 강제 금지 | schema v2 + Phase 3 | schema 2.0.0 / Phase 3 |
| 채점 rubric·85점 근거 | CLD-014 MEDIUM | CDX-007 병합 | 항목별 배점 부재로 총점 재현 불가 + calibration 데이터 없음 | **MEDIUM — 합의.** 항목별 배점·부분점 규칙 정의 → 합격은 `blocker 0 + 영역 하한`, 총점 85는 calibration 전 참고치(가설 격하 규칙 적용) | golden-tests | Golden test v2 |
| Canvas 3D 오귀속·수동 도구의 route enum | CLD-015 MEDIUM | ACCEPT | 공식 페이지 대조 — 3D blocking은 3D Shot Composer | **MEDIUM — 합의.** §12.1 수정, `TOPVIEW_CANVAS` mode 제거, Canvas 산출물은 manual ingest provenance | v2 + schema v2 | Design v2 / schema 2.0.0 |
| Registry semantic gap 4건 | CLD-016 MEDIUM | ACCEPT + 일반화 | probe 4건 통과 확인 | **MEDIUM — 합의.** Codex 수정안 채택: `license non-null` 강제 대신 `rights_basis` + 근거 locator + local-copy 조건으로 일반화; verified claim은 supports 인용 ≥1 + `excerpt_sha256` ≥1 | validator 계약 | Phase 1 |
| 참사 희생자 묘사 윤리 경계 부재 | CLD-017 MEDIUM | ACCEPT | 설계 전체에 피해 묘사 정책 부재 | **MEDIUM — 합의.** 공통 규칙: 피해 순간의 사실적 재현 금지, 구조·역학 중심 허용, 불확실성 표시 — disclosure와 별개 계약 | v2 grammar 공통 규칙 + Factual QC | Design v2 |
| HERITAGE_FORGE 데이터 결함 3건 | CLD-018 LOW | ACCEPT (독립 재현) | 스페이스 토큰·fallback 키 2개 불일치·evidence_insert 누락 — 양측 재현 | **LOW — 합의** | grammar 파일 수정 | HERITAGE_FORGE 1.0.1 |
| 경계 transition 이중 소유 | CLD-019 LOW | ACCEPT | 우선순위 규칙 부재 | **LOW — 합의.** sequence가 외부 경계 소유, 첫/마지막 shot 외향 transition은 `none` (semantic rule) | validator 계약 | Phase 1 |
| OPENMONTAGE_ONLY 미정의 | CLD-020 LOW | ACCEPT (제거 권고) | 스키마에만 존재 | **LOW — 합의.** enum에서 제거 | schema v2 | schema 2.0.0 |
| `/user/credit/detail` 경로 | CLD-021 NEEDS_EVIDENCE | **REJECT** | 공식 OpenAPI 정의로 경로 확인 (Claude 재검증 완료) | **RESOLVED — ADR-001이 옳다.** 200 fixture만 pilot adapter test로 | — | 조치 불요 |
| 실패 generation 과금 | CLD-022 NEEDS_EVIDENCE | CDX-005와 병합, NEEDS_EVIDENCE | billing rules가 feature별 차이 허용 — 전역 규칙 없음 | **NEEDS_EVIDENCE — 실험 정의됨:** 선택 endpoint별 submit 전/후 balance + 실패 task `costCredit` + credit log fixture (Phase 3 pilot) | pilot | Phase 3–4 |
| Hyatt는 synthetic fixture | (dry-run 한계 기술) | CDX-006 ACCEPT | 문서 자체가 사실 잠금 선행을 요구 | **합의.** Golden test 헤더에 "synthetic contract fixture" 명시, 실 pilot 주제 승인 후 evidence pack 별도 생성, `GATE_EVIDENCE_LOCK` 없이 유료 생성 금지 | golden-tests | Golden test v2 |
| QC owner·15–60초 미강제 | CLD-023 LOW | ACCEPT | §20 owner 열 부재 | **LOW — 합의.** owner 열 추가, 15–60초는 warning + waiver reason | v2 문서 | Design v2 |
| `contains_ai` 자기모순 위험 | (§5 답변에서 파생) | **CDX-X-001 HIGH** | 신규 — boolean 자기신고의 우회 가능성 | **HIGH — 합의.** 위 HYBRID 행에 통합: provenance 파생 + invariant 검사 | schema v2 + validator | schema 2.0.0 |
| overlay literal의 claim 우회 | (§5 답변에서 파생) | **CDX-X-002 HIGH** | 신규 — literal-only 정확 사실 텍스트 | **HIGH — 합의.** 위 overlay 행에 통합: exact/high는 `claim_id` 필수 + literal-claim 일치 검사, 비사실 title만 예외 | schema v2 + validator | schema 2.0.0 |

**집계: BLOCKER 2 (OPEN) / HIGH 7 / MEDIUM 8 / LOW 4 / RESOLVED 1 / NEEDS_EVIDENCE 1.**

## 2. Blocker 종료 조건 (구현 검토 재판정의 필요조건)

1. **CLD-002/CDX-X-002**: `overlay.items[]` 반영 schema 2.0.0에서 Hyatt 구간 2·3·7의 typed overlay fixture가 통과하고, "표시된 exact fact → claim_id" 역추적 검사가 자동으로 수행되며, literal-only exact 텍스트 fixture가 실패한다.
2. **CLD-003/CDX-001**: MK custom manifest로 edit·compose checkpoint가 `awaiting_human`에서 실제로 정지하는 dry-run 증거 + title/thumbnail approval artifact의 최소 스키마와 단일 작성 주체 정의.
3. 부속 조건: contract-lock.json이 upstream commit·blob·SHA-256을 검증하고, semantic validator 계약(오류 코드 고정·AJV strict 정책·negative fixture 목록)이 존재하며, Bangjja 항목별 배점표가 재현 가능하다.

## 3. 합의된 단순화 (중복 제거 후 8건)

1. Runtime: 사용자 선택 gate는 유지하되 "Remotion 동등 contract 구현" 명세는 v1 범위에서 제외 — Golden Pilot은 HyperFrames 단일 runtime을 사용자 승인으로 잠근다.
2. Visual Grammar: 정의 문서는 golden test가 실제 선택하는 것만 우선(EVIDENCE_TO_RECONSTRUCTION, FREEZE_TO_EXPLAIN, HERITAGE_FORGE), 나머지는 이름 목록만 유지.
3. Director Memory 전체를 Phase 5로 이연.
4. visual-plan approval 객체 → `gate_ref` 축소 (승인 단일화와 동일 수정).
5. `TOPVIEW_CANVAS`·`OPENMONTAGE_ONLY` route mode 제거 — provider 상태 기계는 자동 경로에만 적용.
6. TopView pilot은 실제 필요한 2–3개 endpoint만 contract fixture로 구현, 나머지는 unsupported.
7. 첫 pilot은 synthetic fixture + 720p review build까지 — publish automation과 최종 1080p는 범위 밖.
8. Multi-LLM adapter 비교(cross-model benchmark)는 채점 체계 calibration 이후로 이연.

## 4. Design v2 candidate 반영 지침 (Stage 4 입력)

- **파일별 변경 범위**: `docs/MK_VISUAL_DIRECTOR_FINAL_DESIGN_v2.md`(신규 — v1 보존), visual-plan schema **2.0.0**(breaking: overlay.items[], script_ref, contains_ai, gate_ref, 조건부 camera, enum 정리), source-registry schema는 1.0.0 유지(변경은 validator 규칙으로), `HERITAGE_FORGE.yaml` 1.0.1, 두 golden test 문서(배점표·측정 절차·synthetic 명시), `vendor/openmontage/contract-lock.json`(신규), ADR-001 소폭 수정(Canvas 문구), ADR-002 개정(contract lock 방식).
- **가설 격하 규칙 적용 확인**: AI 35–45% 비율(§17), 85점 합격선, 모델별 강점(§12.4)은 v2에서도 pilot 관측 가설로 유지한다.
- **v2 첨부 의무**(runbook Stage 4): 변경 요약, 해결 finding ID, 남은 위험(NEEDS_EVIDENCE 1건 포함), schema version 변경(2.0.0), Golden Test 변경, Phase 1 범위. 상태는 `READY_FOR_USER_GATE`까지만.

## 5. 최종 판정

- 양측 독립검수·교차검수 4개 문서 모두 **`DESIGN_NOT_READY`** — 만장일치 유지.
- 아키텍처(IR+compiler, Evidence Layer, clean plate, provider 추상화, TopView 조건부 채택)는 양측 모두 보존 판정. 폐기 대상 없음.
- 재판정 경로: §2 종료 조건 충족 → Design v2 candidate → `READY_FOR_USER_GATE` → **사용자 Human Gate**. 이 문서와 후속 v2는 구현·유료 생성·최종 렌더·공개를 승인하지 않는다.

## 6. Completion checklist (runbook 기준 현황)

- [x] Claude independent review
- [x] Codex independent review
- [x] Claude cross-review
- [x] Codex cross-review (PR #1)
- [x] Every BLOCKER has a final disposition (2건 모두 OPEN + 종료 조건 정의)
- [x] final-consensus.md
- [ ] Design v2 candidate (다음 단계, v1 보존)
- [x] schemas validate (v1 기준; v2는 §2 조건)
- [x] Golden Test criteria remain measurable (배점·측정 절차 반영 조건부)
- [x] Human Gate remains `awaiting_human` — **어떤 gate도 승인되지 않음**

## 7. 남은 절차 메모

이 합의안은 Claude가 초안했다. Codex의 명시적 ACK(PR 코멘트 또는 후속 커밋)와 사용자 승인이 남아 있다. PR #1(`codex-cross-review.md`)은 아직 미머지 상태이므로, 이 문서와 함께 main에 반영되어야 4개 리뷰 문서가 한 브랜치에서 완결된다.
