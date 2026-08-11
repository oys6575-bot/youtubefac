# Claude Cross-Review — Codex 독립검수 대조

- Reviewer: Claude (Fable 5)
- Date: 2026-08-11
- 전제: `reviews/claude-independent-review.md`를 저장한 뒤에 `reviews/codex-independent-review.md`를 처음 읽었다.
- 목적: 합의율을 높이는 것이 아니라(runbook Goal), 두 검수의 탐지 차이를 이용해 blocker와 불필요한 복잡성을 제거한다.

## 1. Codex finding별 판정

### CDX-001 (final-edit gate 미강제) — **ACCEPT, BLOCKER 유지**

CLD-003과 동일한 발견이다. 나는 upstream `pipeline_defs/hybrid.yaml` 원문에서 edit/compose `human_approval_default: false`를 독립적으로 재확인했으므로 Codex의 로컬 근거는 upstream과도 일치한다. 확장 제안 두 가지: (a) GATE_TITLE_THUMBNAIL도 같은 구멍에 있다 — 대응 stage 자체가 없으므로 manifest 수정만으로는 못 막는다. (b) "checkpoint writer가 검증"이라는 Codex의 minimal change는 검증 주체가 결국 에이전트라는 한계가 있다 — checkpoint의 `human_approval_required`를 manifest 수준에서 true로 강제하는 쪽이 방어선이 더 깊다.

### CDX-002 (semantic validator 필요) — **ACCEPT**

CLD-009·011·016·023과 같은 방향이며 Codex의 "오류 코드를 고정한 별도 contract" 제안에 동의한다. 추가할 것: 내 probe에서 확인된 구체 통과 사례 목록(에이전트 self-approval, plan/approval 상태 모순, 빈 registry 잠금, contradicts 인용만으로 verified, community 출처 tier 1)을 validator 규칙의 초기 fixture로 쓰자. 또한 validator 툴체인 명세가 필요하다(CLD-011): Codex는 AJV+formats를 썼기 때문에 date-time이 검증됐지만, Python jsonschema 기본 설정에서는 `approved_at:"yesterday sometime"`이 통과한다. 설계가 툴체인을 못 박지 않으면 두 구현이 서로 다른 검증 강도를 갖게 된다 — 이것 자체가 두 독립검수의 도구 차이로 실증됐다.

### CDX-003 (compiler 정보 보존 미증명) — **PARTIAL**

문제 인식은 CLD-004와 같고, "round-trip이 아니라 loss-accounting"이라는 검증 프레임은 내 제안보다 낫다 — 채택하자. 다만 disposition을 NEEDS_EVIDENCE로 남길 필요는 없다. 나는 upstream `scene_plan.schema.json` 실물로 이미 확인했다: scene 객체는 `additionalProperties: false`이고 disclosure·evidence·provider·fallback에 해당하는 필드가 없으며, 자유 확장점은 top-level `metadata` 하나다. 즉 "손실이 발생하는가"는 증거가 더 필요한 질문이 아니라 확정 사실이고, 남은 질문은 "손실 필드를 어디로 이관하고 누가 소비하는가"뿐이다. 매핑 표(특히 representation→scene type: HYBRID는 자연 대응이 없다)와 loss-accounting fixture를 합쳐 하나의 Phase 1 계약으로 만들자.

단, 전제 조건이 있다: **CLD-001(기준선 미고정)이 먼저 해결되어야 한다.** Codex는 로컬 OpenMontage checkout을 읽을 수 있었지만 ADR-002가 인용한 커밋 `a9f1417`은 upstream에 존재하지 않아(404) 제3자는 같은 검증을 재현할 수 없다. Codex의 CDX-003 evidence 역시 이 재현 불가능한 로컬 계약에 의존한다. 검토 시점의 `scene_plan.schema.json`·`checkpoint.schema.json`·`hybrid.yaml` 사본을 이 저장소에 vendoring하는 것이 CDX-003 검증의 선행 조건이다.

### CDX-004 (HYBRID disclosure 과잉) — **ACCEPT, 단 severity는 HIGH로 상향 제안**

CLD-006과 동일하다. Codex는 MEDIUM으로 봤지만 나는 HIGH를 주장한다. 근거: 이것은 라벨 과밀이라는 UX 문제를 넘어 §2.4(AI 표시 원칙)의 실효성 문제다 — 라벨이 자유 텍스트인 채로 모든 HYBRID에 강제되면, "AI 재현 라벨 존재" QC를 기계적으로 판정할 방법이 없어지고 시청자는 라벨을 장식으로 학습한다. repo의 valid 예제 자체가 AI 없는 HYBRID에 라벨을 달고 있다. Codex가 요청한 비교 검토(representation 분리 vs reason enum)는 아래 §5 답변 1에 있다.

### CDX-005 (endpoint별 계약 차이) — **ACCEPT**

내 검증과 충돌하지 않고 보완적이다. 나는 공통 사실(크레딧 공유, Ultra 크레딧 API 불가, 7일 URL, init/success/fail, costCredit)을 확인했고, Codex는 feature별 차이 가능성을 경고한다. "pilot에서 쓸 2–3개 endpoint만 fixture로 캡처하고 나머지는 unsupported"는 내 CLD-021(`/user/credit/detail` 경로 미확인)·CLD-022(실패 과금 미확인)의 자연스러운 해법이기도 하다. 합의 후보로 그대로 올리자.

### CDX-006 (Hyatt는 synthetic fixture) — **ACCEPT**

내 독립검수에서 같은 사실을 dry-run 한계로만 기술하고 별도 finding으로 만들지 않았는데, Codex의 "synthetic contract fixture로 명시"라는 minimal change가 더 명확하다. 채택. 연관 신규 지적으로 CLD-017(참사 희생자 묘사 윤리 경계 부재)을 함께 검토해 달라 — Hyatt가 실제 사망 사고라는 점에서 CDX-006과 같은 뿌리를 공유한다.

### CDX-007 (85점 합격선의 근거 부재) — **ACCEPT, CLD-014와 병합 제안**

Codex는 "85점이 품질을 대표하는가"를, 나는 "85점을 애초에 계산할 수 있는가"를 지적했다. 논리적으로 내 것이 선행한다(배점 규칙이 없으면 calibration도 불가능하다). 병합안: 항목별 배점을 먼저 정의(CLD-014)하고, 총점은 calibration 전까지 참고치로만 쓰며, 합격 판정은 blocker 0 + 영역별 하한으로 한다(Codex 질문 6과 동일 방향).

## 2. 일치점 요약

| 주제 | Claude | Codex | 상태 |
|---|---|---|---|
| final-edit/compose gate 구멍 | CLD-003 (BLOCKER) | CDX-001 (BLOCKER) | **완전 일치** — 양측 모두 실물 manifest로 확인 |
| semantic validator 필요 | CLD-009/011/016/023 | CDX-002 | 일치 — Claude가 fixture 목록 추가 |
| compiler 정보 손실 | CLD-004 (HIGH) | CDX-003 (NEEDS_EVIDENCE) | 일치하되 disposition 차이 — upstream 실물 확인으로 사실 확정 가능 |
| HYBRID disclosure 과잉 | CLD-006 (HIGH) | CDX-004 (MEDIUM) | 일치하되 severity 차이 |
| TopView 유지 + pilot 조건 | §5 유지(조건부) | KEEP WITH PILOT CONDITIONS | **완전 일치** |
| Golden Test는 계약 검증용 | dry-run 한계 기술 | CDX-006 | 일치 |
| 채점 기준 미성숙 | CLD-014 | CDX-007 | 상호 보완 |
| 최종 판정 | DESIGN_NOT_READY | DESIGN_NOT_READY | **완전 일치** |
| 단순화: grammar/모듈 축소, Director Memory 이연, pilot 범위 제한 | §6의 2·3·6 | simplifications 2·3·4·5 | 방향 일치 |

## 3. 충돌점과 탐지 차이

runbook 규칙("의견 차이는 평균내지 않고 evidence로 판정")에 따라 정리한다.

1. **CLD-002(overlay payload 부재)를 Codex가 다루지 않았다.** 이것이 가장 큰 divergence다. 나는 이를 BLOCKER로 본다 — "정확한 타이포·수치"가 시스템의 핵심 약속인데 그 내용물(날짜 문자열, 수치, claim 바인딩)이 VisualPlan 어디에도 들어갈 자리가 없다. Codex에게 요청: Hyatt 구간 2(날짜 타이포)의 실제 날짜 텍스트를 현 스키마로 표현하는 fixture를 시도해 보고, 불가능하다는 데 동의하는지 판정해 달라. 동의하면 CDX-003의 loss-accounting 이전에 스키마 수정이 필요하다(없는 데이터는 이관할 수도 없다).
2. **CLD-001(기준선 vendoring)을 Codex가 다루지 않았다.** Codex는 로컬 checkout 접근이 가능해 이 문제를 체감하지 못했을 수 있다. 그러나 교차검수·CI·미래 구현자는 로컬 환경이 없다. 재현 가능성은 runbook이 요구하는 검증 문화의 전제이므로 BLOCKER 유지를 주장한다.
3. **HERITAGE_FORGE YAML: Codex는 "parse pass", 나는 결함 3건.** 충돌이 아니라 검증 깊이 차이다 — 구문 파싱은 통과하는 것이 맞고(나도 동일), 내 지적(CLD-018)은 파싱 후 의미 검사에서 나왔다: 스페이스 포함 토큰, fallback 키 2개가 failure_patterns에 부재, required coverage와 sequence_pattern의 evidence_insert 불일치. 스크립트 출력으로 재현 가능하므로 사실 관계 다툼은 없을 것이다.
4. **CDX-003 disposition.** 위 §1 참조 — NEEDS_EVIDENCE가 아니라 사실 확정으로 처리 가능.
5. **CDX-004 severity.** MEDIUM vs HIGH — 판정 근거는 §1 참조. evidence(예제 파일이 이미 문제를 보여줌)로 HIGH를 주장한다.
6. **Claude 고유 발견 중 Codex 검토가 필요한 것**: CLD-005(script_ref/sha256 부재 — evidence_lock과 같은 패턴의 누락이라 반박 여지가 적을 것), CLD-007(edit 이후 권위 순서), CLD-008(±2f/3% 측정 데이터 구조), CLD-010(rejected 주체 기록 불가 — 스키마 else절이 강제), CLD-012(GRAPHIC 숏의 허구 camera), CLD-013(estimated_credits 부재), CLD-015(Canvas 3D blocking 오귀속 — 공식 페이지 대조로 확인), CLD-017(희생자 묘사 윤리), CLD-019/020(경계 transition 이중 정의, OPENMONTAGE_ONLY 미문서화).

## 4. Codex가 옳고 내가 보완해야 할 것

- **loss-accounting 프레임**(CDX-003): 내 "매핑 표" 제안보다 정확한 검증 모델이다. 각 VisualPlan 필드에 대해 `{scene field로 컴파일 | metadata로 이관 | QC가 visual-plan 직접 소비 | 정당화된 drop}` 중 하나를 배정하고 CI에서 검사한다.
- **synthetic fixture 명시**(CDX-006): 내 dry-run 결과 기술보다 실행 가능한 규정이다.
- **endpoint 최소화**(CDX-005): 내 NEEDS_EVIDENCE 2건을 흡수하는 더 작은 계약이다.
- Codex의 simplification 5("첫 pilot은 720p review build까지, publish automation 제외")는 내 목록에 없던 유효한 항목이다 — 합의 후보로 지지한다.

## 5. Codex의 Open questions에 대한 답

1. **HYBRID를 둘로 나눌 가치가 있는가?** representation enum 분리(HYBRID_REAL_GRAPHIC/HYBRID_REAL_AI)보다 `contains_ai: boolean` 1개 추가 + disclosure 조건 변경 + 라벨 통제 어휘를 권한다. runbook의 "더 작은 계약 우선" 규칙에 부합하고, 기존 예제·문서의 representation 값 4개를 보존하며, disclosure 강제 조건을 `AI_RECONSTRUCTION ∨ contains_ai`로 바꾸는 한 줄 수정이다. enum 분리는 §2.4 정의·모든 예제·grammar 호환 라우팅까지 연쇄 수정을 만든다.
2. **compiler의 최소 loss-accounting contract는?** 필드 단위 배정표(위 §4) + 두 불변식: (a) 모든 shot_id가 scene_id 또는 metadata map에 존재, (b) disclosure·evidence·overlay처럼 'drop 금지' 필드 집합을 명시하고 이 집합은 반드시 소비처가 있어야 한다. 단 CLD-002가 먼저다 — overlay payload가 스키마에 없으면 배정할 대상 자체가 없다.
3. **custom manifest vs approval artifact?** custom manifest가 upstream 호환성이 높다. checkpoint 스키마가 이미 `human_approval_required`/`human_approved`를 갖고 stage 목록을 manifest에서 런타임 검증하므로, manifest의 default만 바꾸면 기존 검증 경로를 그대로 탄다. approval artifact는 새 계약 표면을 만든다. 예외: GATE_TITLE_THUMBNAIL은 대응 stage가 없으므로 이 gate에만 approval artifact가 필요하다 — 두 방식의 혼합이 정답이라고 본다.
4. **공통 필드로 두면 안 되는 endpoint-specific 값은?** 모델별 생성 파라미터(참조 이미지 개수, 길이 제한), feature별 costCredit 의미(단위·차감 시점), 오류 코드 체계, cancel 지원 여부. 이들은 `raw_response` 보존 + provider metadata로 두고 정규화하지 않는다. 정규화 대상은 상태 5종·비용 수치·파일 URL·타임스탬프로 한정.
5. **statement-level quote hash가 필요한가?** 이미 스키마에 `citations[].excerpt_sha256`(nullable)이 있다. 새 필드보다 "claim.status=verified인 경우 supports 인용 중 최소 1개는 excerpt_sha256 non-null"이라는 semantic 규칙을 권한다 — 스키마 변경 없이 목적을 달성한다.
6. **85점 대신 blocker+영역 하한만?** 부분 동의. blocker 0 + 영역별 하한(15/20)을 합격의 필요조건으로 유지하고, 총점 85는 calibration 데이터가 쌓일 때까지 참고 지표로 격하한다. 단 전제는 CLD-014(항목별 배점 정의) — 배점 없이는 영역 하한 15점도 계산 불가능하다.

## 6. 합의 후보 (final-consensus.md 초안 입력)

| Finding | Claude | Codex | 제안 disposition |
|---|---|---|---|
| final-edit/title gate 강제 | CLD-003 | CDX-001 | BLOCKER — manifest(edit/compose) + artifact(title/thumbnail) 혼합안으로 v2 명세 |
| overlay payload 부재 | CLD-002 | — | BLOCKER — Codex 검증 요청 후 확정 |
| OpenMontage 계약 vendoring | CLD-001 | — | BLOCKER — Codex 검증 요청 후 확정 |
| compiler 매핑/loss-accounting | CLD-004 | CDX-003 | HIGH — 병합, loss-accounting 프레임 채택 |
| semantic validator 계약 | CLD-009/011/016/023 | CDX-002 | HIGH — 오류 코드 고정 + probe fixture 목록 채택 |
| HYBRID disclosure | CLD-006 | CDX-004 | HIGH(Claude) vs MEDIUM(Codex) — contains_ai 안으로 수렴 제안 |
| script 바인딩 부재 | CLD-005 | — | HIGH — Codex 판정 대기 |
| edit 이후 권위 순서 | CLD-007 | — | HIGH — Codex 판정 대기 |
| 측정 데이터 구조(±2f, 3%) | CLD-008 | — | HIGH — Codex 판정 대기 |
| TopView 유지 + endpoint fixture 한정 | §5 + CLD-021/022 | CDX-005 + KEEP | 합의 — pilot 조건 목록 병합 |
| Hyatt synthetic fixture 명시 | dry-run 한계 | CDX-006 | 합의 |
| 채점 규칙 | CLD-014 | CDX-007 | 합의 — 배점 정의 후 총점은 참고치 |
| 단순화 | §6 1–6 | simplifications 1–5 | 병합 — 중복 제거 시 8개 항목 |

## 7. 종합

두 독립검수는 서로 다른 방법(Codex: 로컬 계약 대조 + AJV / Claude: upstream 실물 대조 + probe 스위트 + dry-run 저작)으로 같은 최종 판정 `DESIGN_NOT_READY`에 도달했고, 최대 blocker(gate 미강제)와 provider 결정(TopView 유지)에서 완전히 일치한다. 충돌은 사실 관계가 아니라 탐지 범위와 severity 배정에 있으며, 전부 evidence로 판정 가능한 성격이다. Codex의 교차검수(CLD finding 판정)와 CLD-001·002에 대한 재현 시도가 다음 단계다. 이 문서는 어떤 Human Gate도 승인하지 않는다.
