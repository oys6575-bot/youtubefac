# Codex Independent Review

- Review date: 2026-08-11
- Reviewed design: MK Visual Director Final Design v1
- Method: document trace, official provider recheck, local OpenMontage contract comparison, JSON/YAML/link validation
- Independence rule: written before Claude review
- Final verdict: `DESIGN_NOT_READY`

`DESIGN_NOT_READY`는 설계 폐기가 아니라 구현 전 교차검수와 아래 blocker 해결이 남았다는 뜻이다. 현재 패키지 상태 `DESIGN_READY_FOR_CROSS_REVIEW`와 모순되지 않는다.

## Strengths worth preserving

1. 대본에서 바로 클립을 만들지 않고 의미→Sequence→Shot 순서로 내리는 구조
2. REAL, AI_RECONSTRUCTION, GRAPHIC, HYBRID 표현 구분
3. clean plate와 정확한 overlay의 분리
4. provider를 source of truth로 두지 않고 즉시 다운로드·checksum을 남기는 원칙
5. 공용 Visual Grammar와 모델별 LLM adapter의 분리
6. 생성 전 animatic·evidence·budget Human Gate
7. reference를 표면적 룩이 아니라 coverage·리듬·오디오 grammar로 추출한 방식
8. Golden Test를 60–90초 단위로 제한한 구현 순서

## Findings ordered by severity

### CDX-001

- Severity: BLOCKER
- Disposition: BLOCKER
- Location: `docs/MK_VISUAL_DIRECTOR_FINAL_DESIGN_v1.md` §19, `docs/ADR-002-OPENMONTAGE-INTEGRATION.md`
- Claim: 현재 OpenMontage `hybrid` manifest는 edit와 compose를 자동 진행할 수 있어 MK 시스템의 `GATE_FINAL_EDIT`을 자체적으로 강제하지 않는다.
- Evidence: 로컬 `pipeline_defs/hybrid.yaml`에서 edit/compose의 `human_approval_default`가 false이고 publish만 true다.
- Failure mode: review build를 사람이 승인하지 않았는데 compose 또는 다음 단계가 진행될 수 있다.
- Minimal change: Phase 1에서 MK용 custom hybrid manifest 또는 final-edit approval artifact를 만들고 checkpoint writer가 이를 검증하게 한다.
- Verification: 승인 기록이 없는 review build로 compose/publish 진행을 시도했을 때 contract test가 실패해야 한다.

### CDX-002

- Severity: HIGH
- Disposition: PARTIAL
- Location: `schemas/visual-plan.schema.json`, Final Design §20.1
- Claim: JSON Schema만으로 ID referential integrity, start<end, shot duration 합계, top-level status/approval consistency를 모두 검증할 수 없다.
- Evidence: positive/negative schema test는 구조 제약을 검증하지만 cross-file reference와 합계는 외부 로직이 필요하다.
- Failure mode: schema-valid이지만 존재하지 않는 claim을 참조하거나 Sequence 타이밍이 겹치는 plan이 production으로 넘어간다.
- Minimal change: Phase 1에 deterministic semantic validator를 별도 contract로 만들고 오류 코드를 고정한다.
- Verification: orphan evidence, 중복 ID, 역전된 시간, stale checksum fixture가 모두 실패해야 한다.

### CDX-003

- Severity: HIGH
- Disposition: NEEDS_EVIDENCE
- Location: `docs/ADR-002-OPENMONTAGE-INTEGRATION.md`
- Claim: VisualPlan→OpenMontage scene plan compiler는 충돌을 피하는 올바른 방향이지만 아직 정보 보존 가능성이 fixture로 증명되지 않았다.
- Evidence: current OpenMontage `scene_plan`은 scene 중심이고 `additionalProperties: false`; VisualPlan은 shot-level evidence·continuity·overlay를 가진다.
- Failure mode: compiler가 중요한 shot 제약을 metadata로만 밀어 넣거나 누락해 후속 asset/edit agent가 읽지 못한다.
- Minimal change: Hyatt VisualPlan fixture 하나를 컴파일하고 모든 shot_id와 production-critical field의 소비 위치를 mapping table로 고정한다.
- Verification: round-trip이 아니라 loss-accounting test를 사용해 각 필드가 canonical scene plan, sidecar, asset manifest 중 어디에서 소비되는지 확인한다.

### CDX-004

- Severity: MEDIUM
- Disposition: NEEDS_EVIDENCE
- Location: `schemas/visual-plan.schema.json` `representation=HYBRID` conditional
- Claim: 모든 HYBRID shot에 disclosure label을 강제하면 실제 자료+일반 설명 그래픽에도 불필요한 라벨이 생길 수 있다.
- Evidence: HYBRID는 REAL+GRAPHIC과 REAL+AI를 모두 포괄하지만 윤리적 disclosure 요구가 동일하지 않다.
- Failure mode: 화면 라벨이 과밀해지거나 사용자가 AI 재현이 없는 장면도 AI로 오해한다.
- Minimal change: Claude가 `HYBRID_REAL_GRAPHIC`과 `HYBRID_REAL_AI` 분리 또는 disclosure reason enum을 비교 검토한다.
- Verification: 실제 사진+날짜 overlay, 실제 사진→AI match, AI+diagram 세 fixture에서 기대 label을 비교한다.

### CDX-005

- Severity: MEDIUM
- Disposition: NEEDS_EVIDENCE
- Location: `docs/ADR-001-TOPVIEW-PRIMARY-PROVIDER.md`, Final Design §12
- Claim: TopView 채택은 통합성 기준으로 타당하지만 endpoint별 status, cost, failure billing, cancellation 계약이 동일하다고 가정하면 안 된다.
- Evidence: 공식 문서는 async task와 credit log를 제공하지만 일부 feature의 API billing/usage가 웹과 다를 수 있다고 명시한다.
- Failure mode: Router의 공통 contract가 특정 모델 endpoint의 raw response를 잘못 정규화하거나 실패 비용을 누락한다.
- Minimal change: 월간 pilot에서 사용할 정확한 2–3 endpoint만 contract fixture로 캡처하고 나머지는 unsupported로 둔다.
- Verification: submit/query/success/fail/insufficient-credit 응답 fixture와 cost ledger 대조.

### CDX-006

- Severity: MEDIUM
- Disposition: NEEDS_EVIDENCE
- Location: `golden-tests/HYATT-60-90S-GOLDEN-SEQUENCE.md`
- Claim: Hyatt sequence는 전환 contract 검증에는 좋지만 현재 공학 사실과 권리 자료가 placeholder라 factual Golden Test로 실행할 수 없다.
- Evidence: 문서 자체가 실제 사건과 공학 주장을 Source Registry에서 잠가야 한다고 명시한다.
- Failure mode: 시각적으로 그럴듯한 fixture가 사실 검증을 통과했다고 오인된다.
- Minimal change: Phase 1에서는 synthetic contract fixture로 명시하고 실제 pilot 주제 승인 후 evidence pack을 별도 생성한다.
- Verification: `GATE_EVIDENCE_LOCK` 없이는 유료 generation 단계가 시작되지 않아야 한다.

### CDX-007

- Severity: LOW
- Disposition: PARTIAL
- Location: `config/visual-grammars/HERITAGE_FORGE.yaml`
- Claim: 정량 기준은 유용하지만 85점 단일 합격선이 채널 품질을 대표한다는 근거는 없다.
- Evidence: 아직 실제 pilot score와 사용자 선호 data가 없다.
- Failure mode: 체크리스트 최적화가 실제 몰입·취향보다 우선한다.
- Minimal change: 85점은 calibration 전 임시값으로 유지하고 사용자 평가와 두 pilot 결과로 조정한다.
- Verification: reviewer score와 사용자 승인/거절의 상관을 기록한다.

## Findings resolved during this review

### CDX-R01 — OpenMontage parallel-contract conflict

초기 설계의 임의 프로젝트 폴더와 확장 checkpoint 상태가 OpenMontage canonical contract와 충돌했다. ADR-002를 추가하고 project layout, checkpoint enum, VisualPlan sidecar compiler 방식으로 수정했다.

### CDX-R02 — Runtime ownership ambiguity

HyperFrames를 항상 합성 runtime으로 고정한 표현을 제거했다. 두 runtime이 사용 가능하면 HyperFrames와 Remotion을 모두 제시하고 사용자가 선택한 하나를 proposal에서 잠그도록 수정했다.

### CDX-R03 — Evidence pinpoint omission

Claim이 source_id만 참조하던 구조를 page·section·figure·timestamp pinpoint가 있는 citation 구조로 보강했다.

### CDX-R04 — Evidence namespace weakness

VisualPlan evidence ID를 `SRC_` 또는 `CLAIM_` namespace로 제한했다.

### CDX-R05 — TopView billing statement drift

“웹/API credit이 분리될 수 있다”는 오래되거나 부정확할 수 있는 표현을 공식 billing rule에 맞춰 수정했다. 표준 credit 공유, feature별 차이 가능성, Ultra credit의 API 사용 불가를 분리해 기록했다.

## Schema validation findings

| Test | Expected | Result |
|---|---|---|
| VisualPlan valid example | pass | pass |
| Source Registry valid example | pass | pass |
| anonymous approved gate | fail | fail as expected |
| high-precision undisclosed AI with no evidence | fail | fail as expected |
| JSON syntax for schemas/examples | pass | pass |
| HERITAGE_FORGE YAML parse | pass | pass |
| local Markdown links | pass | pass |

남은 한계: schema test는 cross-file reference와 시간 합계를 검증하지 않는다. CDX-002의 semantic validator가 필요하다.

## Golden Test dry-run

| Test | Contract expressible | Media executable now | Main blocker |
|---|---|---|---|
| Hyatt 60–90s | yes | no | evidence/rights pack and compiler not implemented |
| Bangjja style | yes | no | actual pilot assets and calibrated scoring absent |

## TopView decision

`KEEP WITH PILOT CONDITIONS`.

Newtake의 수동 연출 UX는 매력적이지만 주력 자동화 provider로는 공개 API 계약을 확인하지 못했다. TopView는 공식 REST API, async task, billing, storage, Canvas, 3D Shot Composer, MCP 연결 지점을 제공한다. 다만 연간 구매나 광범위한 model support를 전제로 하지 않고 월간 pilot의 실제 실패율·비용·대기 시간을 기준으로 재평가해야 한다.

## Five simplifications

1. OpenMontage core schema를 바로 fork하지 않고 VisualPlan sidecar+compiler 하나로 시작한다.
2. Golden Pilot 전에는 8개 overlay module과 2개 Visual Grammar만 구현한다.
3. TopView pilot endpoint를 실제 필요한 image master/video 2–3개로 제한한다.
4. Director Memory는 승인/거절된 규칙만 저장하고 자동 취향 학습을 뒤로 미룬다.
5. 첫 pilot은 720p review build까지만 만들고 최종 1080p·publish automation은 제외한다.

## Open questions for Claude

1. HYBRID representation을 둘로 나누는 것이 schema 복잡성보다 가치가 큰가?
2. VisualPlan compiler의 최소 loss-accounting contract는 무엇인가?
3. final-edit gate는 custom manifest와 별도 approval artifact 중 어느 쪽이 upstream 호환성이 높은가?
4. TopView provider contract에서 공통 필드로 두면 안 되는 endpoint-specific 값은 무엇인가?
5. Source Registry citation 구조에 statement-level quote hash가 필요한가?
6. HERITAGE_FORGE의 85점 합격선 대신 blocker+영역별 하한만 두는 편이 나은가?

## Verification evidence

검수 시 사용한 범위:

- official TopView API, billing, concurrency/storage, Canvas, 3D Composer, MCP pages
- official Newtake site and terms
- local OpenMontage `AGENT_GUIDE.md`, `pipeline_defs/hybrid.yaml`, `scene_plan`, `edit_decisions`, `proposal_packet`, checkpoint schemas
- AJV Draft 2020 validation with formats
- Ruby Psych YAML parse
- local Markdown target existence check
- `git diff --check`

## Final verdict

`DESIGN_NOT_READY`

Claude 독립검수와 상호 교차검수, CDX-001의 gate 설계 합의, CDX-002/003의 Phase 1 contract가 확정되면 `READY_FOR_IMPLEMENTATION_REVIEW`로 재평가할 수 있다. 이는 구현 승인과 별개이며 사용자 Human Gate가 필요하다.
