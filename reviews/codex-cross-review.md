# Codex Cross-Review — Stage 2

- Reviewer: Codex
- Date: 2026-08-11
- Inputs: `reviews/claude-independent-review.md`, `reviews/claude-cross-review.md`, `reviews/codex-independent-review.md`
- Method: Claude finding 23건 개별 반증, CLD-001/002 재현 검증, 로컬·upstream OpenMontage 계약 비교, 공식 TopView 문서 재확인
- Scope: 리뷰 문서만 추가. 설계·스키마·grammar·vendor 파일은 수정하지 않음.
- Human Gate: **어떤 gate도 승인하지 않음.** 모든 승인 상태는 사용자 결정 전까지 그대로 유지한다.

## 1. Stage 2 필요성 및 종합 판정

Claude가 요청한 Stage 2는 필요하다. 독립검수의 의견을 단순 병합하는 단계가 아니라, 두 검수 사이의 가장 큰 차이였던 overlay payload와 OpenMontage 기준선 문제를 실행 가능한 증거로 판정하는 단계이기 때문이다.

종합 판정은 **`DESIGN_NOT_READY` 유지**다.

- 구현 전 blocker: **CLD-002, CLD-003**
- 기준선 확인 후 blocker에서 하향: **CLD-001 → PARTIAL**
- 외부 실측이 더 필요한 항목: **CLD-022 → NEEDS_EVIDENCE**
- 공식 문서로 반증된 항목: **CLD-021 → REJECT**
- 나머지 유효 finding: **ACCEPT 18건**

여기서 `ACCEPT`는 Claude의 지적이 유효해 v2 수정 또는 명시적 계약이 필요하다는 뜻이다. `BLOCKER`는 구현 승인 전에 반드시 해결해야 한다는 뜻이며 Human Gate 승인과는 무관하다.

## 2. Claude finding 23건 판정

| ID | Codex 판정 | 결론과 근거 |
|---|---|---|
| CLD-001 | **PARTIAL** | ADR이 인용한 로컬 HEAD `a9f1417…`은 upstream에 없다는 지적은 맞다. 그러나 대상 3개 계약 파일은 upstream 고정 커밋 `4eab34c5…`과 blob·SHA-256이 모두 동일하다. 전체 사본 vendoring은 현시점 blocker가 아니며, v2에는 경량 contract lock을 권한다. |
| CLD-002 | **BLOCKER** | 재현 결과, 실제 날짜 문자열과 claim binding을 overlay의 typed payload로 넣으면 `additionalProperties:false` 때문에 실패한다. `prompt_intent` 자유 텍스트에 숨기면 통과하지만 기계 역추적이 불가능하다. 핵심 정확성 계약이므로 blocker에 동의한다. |
| CLD-003 | **BLOCKER** | upstream과 동일한 `hybrid.yaml`에서 edit·compose의 `human_approval_default`가 모두 `false`다. final edit은 custom manifest, title/thumbnail은 별도 approval artifact 또는 전용 stage가 필요하다. 문서상의 gate 목록만으로 우회를 막지 못한다. |
| CLD-004 | **ACCEPT** | scene 객체가 닫힌 계약이고 production-critical 필드의 자연 대응이 없다. Claude가 답한 필드 단위 loss-accounting 표와 drop 금지 불변식을 채택한다. CLD-002 해결과 contract lock이 선행돼야 한다. |
| CLD-005 | **ACCEPT** | `script_ref`/`script_sha256` 부재로 script→VisualPlan freshness를 검증할 수 없다. JSON Schema 단독이 아니라 semantic validator가 실제 대본 해시를 대조해야 한다. |
| CLD-006 | **ACCEPT** | HYBRID가 REAL+GRAPHIC과 REAL+AI를 함께 뜻해 disclosure를 과잉 강제한다. enum 분리보다 `contains_ai`와 통제된 disclosure vocabulary가 작은 변경이다. 단 CDX-X-001의 모순 방지 규칙이 필요하다. Severity는 HIGH에 동의한다. |
| CLD-007 | **ACCEPT** | 편집 이후 실제 컷의 최종 권위는 `edit_decisions`로 두고 VisualPlan의 edit 필드는 GATE_ANIMATIC까지의 계획 가설로 본다. 차이는 자동 역수정 대신 divergence report로 남기는 편이 감사 가능하다. |
| CLD-008 | **ACCEPT** | ±2 frames와 anchor 3%는 현재 문자열 필드만으로 계산할 수 없다. canonical beat-map artifact, 시간값, 정규화 좌표, 측정 도구·절차가 필요하다. Golden Test는 실제 `edit_decisions`를 기준으로 측정해야 한다. |
| CLD-009 | **ACCEPT** | VisualPlan 내부 승인과 OpenMontage checkpoint가 이중 진실을 만든다. VisualPlan approval을 `gate_ref`로 축소하고 승인 기록은 checkpoint에 단일화하는 안을 지지한다. 인간 행위자 증명은 JSON Schema만으로 해결되지 않는다. |
| CLD-010 | **ACCEPT** | rejected/needs_revision에서도 결정자와 시간이 감사에 필요하다. CLD-009 방식으로 approval 객체를 제거하면 checkpoint decision record에서 해결하고, 유지한다면 `decided_by`/`decided_at`으로 일반화한다. |
| CLD-011 | **ACCEPT** | format 검증 강도는 validator 설정에 따라 달라진다. 추가 재현에서 현재 schema는 AJV 8 `strict:true`가 conditional `minItems`의 로컬 type 부재를 이유로 컴파일 거부했다. Phase 1 계약에 Draft 2020-12, AJV, `ajv-formats`, 버전, strict-mode 정책을 고정하고 잘못된 date/date-time과 schema-compile fixture를 CI에 둬야 한다. |
| CLD-012 | **ACCEPT** | 순수 GRAPHIC 숏에 물리 camera·lighting 값을 강제하면 허구 데이터가 생긴다. 조건은 representation만 보지 말고 구성 요소와 실제 생성 route를 함께 고려해야 한다. |
| CLD-013 | **ACCEPT** | `cost_tier`만으로 GATE_BUDGET의 수치 근거를 만들 수 없다. endpoint별 quote 시점·estimated credits·실측 credits를 연결하는 cost ledger가 필요하다. provider 전체에 하나의 단가 의미를 강제해서는 안 된다. |
| CLD-014 | **ACCEPT** | 항목별 배점과 부분점 규칙이 없어 85점을 재현할 수 없다. 먼저 항목별 배점과 영역 하한을 정의하고, calibration 전까지 총점 85는 참고 지표로만 사용한다. |
| CLD-015 | **ACCEPT** | 공식 제품 페이지상 3D blocking은 Canvas가 아니라 3D Shot Composer 기능이다. Canvas는 자동 submit/status provider가 아니라 manual ingest provenance로 분리하는 안에 동의한다. |
| CLD-016 | **ACCEPT** | 네 semantic gap은 모두 유효하다. 다만 `rights.status=verified → license non-null`은 public-domain·직접 허가 자료를 놓칠 수 있으므로 `rights_basis`, 근거 locator, local-copy/checksum 조건으로 일반화해야 한다. |
| CLD-017 | **ACCEPT** | 실제 참사를 synthetic contract fixture로 다루더라도 피해 순간의 사실적 재현 금지, 구조·역학 중심 허용, 불확실성 표시라는 편집 윤리 경계가 필요하다. 이는 disclosure와 별개다. |
| CLD-018 | **ACCEPT** | 독립 재검사에서 스페이스 포함 토큰 1개, failure pattern에 없는 fallback 키 2개, required coverage에 없는 `evidence_insert`를 재현했다. YAML parse pass와 semantic consistency pass는 다른 검사다. |
| CLD-019 | **ACCEPT** | sequence와 shot이 경계 transition을 동시에 소유하면 충돌한다. sequence가 외부 경계를 소유하고 첫/마지막 shot의 외향 transition은 `none`으로 제한하는 semantic rule이 가장 단순하다. |
| CLD-020 | **ACCEPT** | `OPENMONTAGE_ONLY`는 schema에만 있고 의미가 없다. OpenMontage는 제작 orchestration/runtime이지 원천 provider가 아니므로 enum에서 제거하는 편을 권한다. |
| CLD-021 | **REJECT** | 현재 공식 reference에서 정확한 `GET /user/credit/detail` 경로와 curl 예제를 확인했다. ADR-001 경로는 맞다. 실제 필드·인증·200 fixture는 pilot adapter test로 남는다. |
| CLD-022 | **NEEDS_EVIDENCE** | 일부 공식 endpoint는 실패 시 환불 또는 성공 시만 차감한다고 명시하지만 billing rule은 feature별 차이를 허용한다. provider 전체 규칙으로 일반화할 수 없으므로 선택 endpoint의 실패 task와 credit log 실측이 필요하다. 설계의 “확인하라”는 안전장치는 유지한다. |
| CLD-023 | **ACCEPT** | QC별 owner를 명시해야 한다. Sequence 15–60초는 창작상 예외가 있으므로 hard schema error보다 semantic warning과 waiver reason이 적절하다. |

판정 분포: `ACCEPT 18 / PARTIAL 1 / REJECT 1 / NEEDS_EVIDENCE 1 / BLOCKER 2`.

## 3. 필수 재현 검증 A — CLD-002 Hyatt 날짜 overlay

### 3.1 검증 질문

Hyatt Golden Sequence 구간 2의 실제 날짜 **`1981년 7월 17일`**을 현재 VisualPlan schema 안에서 다음 두 조건을 만족하게 표현할 수 있는가?

1. 화면에 렌더할 실제 문자열이 typed field에 존재한다.
2. 그 문자열이 `CLAIM_HYATT_DATE`와 기계적으로 연결된다.

### 3.2 Fixture 1 — 원하는 구조를 직접 추가

기존 valid example을 바탕으로 해당 shot의 overlay에 다음 값을 추가했다.

```json
{
  "mode": "COMPOSITED_BY_HYPERFRAMES",
  "module": "TYPOGRAPHY",
  "safe_area": "title",
  "exact_text_from_claims": true,
  "claim_id": "CLAIM_HYATT_DATE",
  "display_text": "1981년 7월 17일"
}
```

AJV Draft 2020-12 + `ajv-formats` 결과: **INVALID**.

- 원인: `$defs.overlay.additionalProperties=false`
- 거부 필드: `claim_id`, `display_text`
- fixture SHA-256: `3faf4d0f1a3cbce8f0d00001e4b922e6771c9ec285758132559404f97e64403e`

### 3.3 Fixture 2 — 자유 텍스트로 우회

overlay는 기존 네 필드만 유지하고 `prompt_intent`에 `1981년 7월 17일 / CLAIM_HYATT_DATE`를 문장으로 넣었다.

AJV 결과: **VALID**.

- fixture SHA-256: `0493c7423b004b825a29b26afc3fb6e6abf0652377f7b8a2126837aec2175a0c`
- 그러나 renderer가 읽을 표준 payload 경로가 없고, claim resolver가 역추적할 구조도 없다.
- 따라서 이는 표현 성공이 아니라 **opaque prose 우회**다.

### 3.4 판정과 최소 계약

**CLD-002는 BLOCKER로 ACCEPT한다.** 현재 schema는 날짜를 “언급”할 수는 있지만, 정확한 표시 내용과 claim binding을 계약으로 표현할 수 없다.

권장 최소 형태는 단일 `module`을 `overlay.items[]`로 바꾸는 것이다.

```json
{
  "overlay_id": "OVL_HYATT_DATE",
  "module": "TYPOGRAPHY",
  "claim_id": "CLAIM_HYATT_DATE",
  "text_key": "hyatt.collapse_date",
  "locale": "ko-KR",
  "position_hint": "upper_left",
  "safe_area": "title",
  "exact_text_from_claims": true
}
```

필수 불변식:

- 한 shot에 TYPOGRAPHY+NUMBER, CALLOUT+UNDERLINE처럼 여러 item을 허용한다.
- `exact_text_from_claims=true`이면 `claim_id`가 필수다.
- exact/high factual text는 claim resolver의 canonical value에서 생성한다.
- `literal`을 허용하더라도 claim value와의 일치 검사를 통과해야 한다(CDX-X-002).
- 다국어는 renderer 문자열을 복제하기보다 `text_key + locale` 또는 claim의 localized value로 해결한다.

## 4. 필수 재현 검증 B — CLD-001 OpenMontage 기준선

### 4.1 저장소 관계

| 항목 | 결과 |
|---|---|
| local repository | `/Users/mk-macbook/Desktop/openmontage` |
| local HEAD | `a9f1417ab4a9770bb6ebe24f51aa948a98aaa238` |
| fetched `origin/main` | `4eab34c5cfcccaa4f1970554928feccce73ee930` |
| divergence `HEAD...origin/main` | local-only 7 commits / upstream-only 0 commits |
| upstream commit API | `4eab34c5cfcccaa4f1970554928feccce73ee930` 확인 |

Claude의 지적대로 로컬 HEAD 자체는 upstream 공개 commit으로 재현할 수 없다. 그러나 compiler가 실제 의존하는 세 파일을 로컬 HEAD·working tree·upstream 고정 commit에서 각각 비교하니 모두 동일했다.

### 4.2 계약 파일 비교

| 파일 | Git blob (local = upstream) | SHA-256 |
|---|---|---|
| `schemas/artifacts/scene_plan.schema.json` | `751665bfe28152207c00ecbd3bcacc51f7d8a6fc` | `7b833b7643a73921011270189e5baf645ca67d09390a5d143f6a4b55a667d7a9` |
| `schemas/checkpoints/checkpoint.schema.json` | `1249c8f051520a30977bddc24961ed9c21f9c0c3` | `39db408cd797cc5902ee55835a1f659ba26ba3d94c218d7111a6ff4df3da0833` |
| `pipeline_defs/hybrid.yaml` | `b46dd642d9b31ef6ed2d41c5efbc70178963d9e1` | `e853359af0bea59c53f617ab3101aa26ea66ea519e3a5177e9ae0c9a5578f226` |

local-only 7개 commit 중 위 세 파일을 변경한 commit은 없었다. 따라서 현재 설계가 본 계약은 공개 upstream commit `4eab34c5…`로 재현 가능하다.

### 4.3 vendor 판정

**세 파일의 전체 사본을 지금 `vendor/`에 커밋하지 않는다.** 이유는 다음과 같다.

1. 공개 upstream의 immutable commit과 현재 로컬 파일이 동일해 재현 기준선이 이미 있다.
2. 전체 사본은 OpenMontage의 AGPL 라이선스 고지, 동기화, drift 관리 부담을 새 저장소로 가져온다.
3. Stage 2의 허용 범위는 리뷰 문서 추가뿐이며, vendor 변경은 사용자 지시를 위반한다.

v2 수정 시에는 전체 사본 대신 `vendor/openmontage/contract-lock.json` 같은 **경량 lock manifest**를 먼저 권한다. 포함할 값은 upstream URL, commit, 세 path, Git blob, SHA-256, license identifier, verification command다. 오프라인·air-gapped CI가 실제 요구될 때만 LICENSE/NOTICE와 함께 exact copy를 vendor한다.

따라서 **CLD-001은 PARTIAL**이다. “로컬 HEAD 인용이 재현 불가능하다”는 claim은 맞지만, “세 파일의 전체 vendoring 없이는 compiler 계약을 검증할 수 없다”와 BLOCKER severity는 이번 증거로 반증됐다.

## 5. Claude §7 질문 8개에 대한 답

### Q1. scene_plan 사본 없이 계약을 검증할 수 있는가?

가능하다. upstream immutable commit `4eab34c5…`, 세 path, blob, SHA-256을 lock manifest로 고정하고 CI가 다시 계산하면 된다. 이번 비교에서 로컬 HEAD와 해당 upstream 계약이 동일했다. 전체 vendoring은 offline CI가 요구될 때만 필요하다.

### Q2. overlay payload 부재와 최소 schema는?

부재에 동의한다. `overlay.items[]`를 채택하되 item에는 `overlay_id`, `module`, `claim_id/source_id`, `text_key 또는 제한된 literal`, `locale`, `position_hint`, `safe_area`, `exact_text_from_claims`가 필요하다. 정확한 사실 텍스트는 claim binding 없이 literal만으로 통과하면 안 된다.

### Q3. HYBRID 분리와 `contains_ai` 중 어느 쪽이 작은가?

`contains_ai` 추가가 작다. 기존 representation 네 값을 유지하고 disclosure 조건만 바꿀 수 있다. 다만 자유 boolean은 모순 상태를 만들 수 있으므로 representation/component/provider intent와의 semantic invariant가 필수다(CDX-X-001). label은 자유 텍스트가 아니라 통제 어휘여야 한다.

### Q4. 편집 이후 권위를 `edit_decisions`에 두는가?

동의한다. 실제 컷·타이밍·runtime 결정은 `edit_decisions`가 최종 권위다. VisualPlan edit 필드는 animatic까지의 연출 의도다. 부작용은 승인된 VisualPlan과 최종 영상이 달라 보일 수 있다는 점인데, 자동 역수정보다 `{planned, actual, reason, actor, decided_at}` divergence report와 checksum chain이 안전하다. Golden Test도 actual edit 기준으로 측정한다.

### Q5. Bangjja 85점 배점을 독립적으로 정의했는가?

아니다. Codex 독립검수도 85점을 calibration 전 임시값으로 봤지만 항목별 배점표를 완성하지 않았다. Claude의 지적처럼 배점 정의가 선행한다. 합격 규칙은 `blocker=0 + 영역별 하한`, 총점 85는 두 pilot과 사용자 판단이 쌓일 때까지 참고치가 적절하다.

### Q6. 실패 generation 과금을 확인했는가?

provider-global 규칙은 확인하지 못했다. 공식 문서상 일부 기능은 실패 시 자동 환불 또는 성공 시만 차감하지만, billing rules는 기능별 차이를 허용한다. 따라서 선택한 2–3 endpoint에 대해 submit 전 balance, 실패 task의 `costCredit`, credit log, submit 후 balance를 함께 fixture로 남겨야 한다.

### Q7. GATE_FINAL_EDIT은 custom manifest와 approval artifact 중 무엇인가?

혼합안에 동의한다. edit·compose는 기존 checkpoint 경로를 재사용하는 MK custom manifest가 가장 작다. GATE_TITLE_THUMBNAIL은 대응 stage가 없으므로 전용 stage 또는 최소 approval artifact가 필요하다. 둘 다 승인 행위의 source of truth는 OpenMontage checkpoint/event 계층에 둔다.

### Q8. `additionalProperties:false`는 득인가 실인가?

안정된 IR 경계에서는 득이 더 크다. LLM hallucinated field를 즉시 거부하고 adapter 결과를 비교 가능하게 만든다. 다만 provider raw response나 실험 metadata까지 닫으면 사소한 확장마다 schema churn이 생긴다. 안정된 core는 닫고, `extensions`를 namespaced object로 열며, 호환 가능한 optional field 추가는 minor schema revision으로 관리한다. schema version bump를 breaking change에만 한정할 필요는 없지만 migration 의무는 breaking change에만 둔다.

## 6. Claude가 답한 Codex 질문 6개 반영 결과

| Codex 질문 | Claude 답 반영 | Stage 2 판정 |
|---|---|---|
| HYBRID를 둘로 나눌 가치 | `contains_ai`가 더 작은 계약 | **채택**, CLD-006 ACCEPT. 단 모순 방지 semantic invariant 추가. |
| compiler 최소 loss-accounting | 필드별 disposition + shot ID/drop 금지 불변식 | **채택**, CLD-004 ACCEPT. round-trip 대신 소비 위치를 증명한다. |
| custom manifest vs approval artifact | edit/compose는 manifest, title/thumbnail은 artifact | **채택**, CLD-003 BLOCKER 해결안으로 사용. |
| endpoint-specific 값 | 모델 파라미터·오류·cancel·비용 의미는 raw/provider metadata | **채택**, 공통 정규화는 status·수치 비용·URL·timestamp에 제한. |
| statement-level quote hash | 새 필드보다 기존 `excerpt_sha256`의 semantic rule | **채택**, verified claim의 supports citation 중 hash 1개 이상을 요구. |
| 85점 대 blocker+영역 하한 | 배점 정의 후 blocker 0 + 영역 하한, 총점은 참고 | **채택**, CLD-014 ACCEPT 및 CDX-007과 병합. |

## 7. 신규 finding

### CDX-X-001 — `contains_ai`가 새로운 자기모순 필드가 될 위험

- Severity: HIGH
- Disposition: **ACCEPT**
- Trigger: CLD-006에 대한 Claude의 최소 변경안
- Claim: `contains_ai`를 단순 boolean으로 추가하면 `representation=AI_RECONSTRUCTION, contains_ai=false` 또는 AI 생성 component가 있는데 false인 모순 plan이 생길 수 있다.
- Failure mode: disclosure gate가 작성자의 자기신고 하나에 의존해 우회된다.
- Minimal change: `contains_ai`를 component 목록에서 파생하거나 semantic validator가 representation·component provenance와 일관성을 검사한다. `AI_RECONSTRUCTION`은 항상 true, HYBRID는 component provenance 중 하나라도 generated/reconstructed이면 true여야 한다.
- Verification: 위 두 모순 fixture가 실패하고 REAL+GRAPHIC만 있는 HYBRID는 false로 통과해야 한다.

### CDX-X-002 — overlay `literal`이 claim binding을 우회할 위험

- Severity: HIGH
- Disposition: **ACCEPT**
- Trigger: CLD-002의 `overlay.items[]` 제안
- Claim: `text_key 또는 literal`만 허용하면 새 schema에서도 정확한 숫자·날짜를 literal로 넣어 claim 연결을 피할 수 있다.
- Failure mode: schema는 payload를 갖게 되지만 “every displayed exact fact maps to claim_id” 검사는 여전히 실패한다.
- Minimal change: `factual_precision ∈ {high, exact}` 또는 `exact_text_from_claims=true`인 item은 `claim_id` 필수. renderer는 claim canonical/localized value를 resolve하고, literal을 함께 보관할 경우 두 값이 일치해야 한다. 비사실적 제목·브랜드 copy만 unbound literal을 허용한다.
- Verification: exact 날짜+literal only는 실패, 같은 날짜+claim binding은 통과, 비사실적 title literal은 명시된 예외로 통과해야 한다.

## 8. 합의안과 구현 전 종료 조건

### 8.1 합의된 방향

1. TopView는 **조건부 주력 provider로 유지**하고 월간 pilot의 선택 endpoint 2–3개만 구현한다.
2. OpenMontage는 canonical production contract로 유지하되 upstream commit 기반 contract lock을 추가한다.
3. VisualPlan은 sidecar IR로 유지하고 compiler는 field-level loss-accounting으로 검증한다.
4. overlay payload와 claim binding을 먼저 고친 뒤 compiler fixture를 만든다.
5. edit·compose Human Gate는 custom manifest로, title/thumbnail은 전용 stage/artifact로 강제한다.
6. 첫 pilot은 synthetic fixture와 720p review build까지이며 publish automation은 범위 밖이다.

### 8.2 `READY_FOR_IMPLEMENTATION_REVIEW` 재판정 조건

- CLD-002: Hyatt 구간 2·3·7 typed overlay fixtures가 통과하고 exact fact→claim 역추적 test가 통과한다.
- CLD-003: edit/compose가 `awaiting_human`에서 정지하고 title/thumbnail approval source가 단일화된다.
- CLD-004/005/008/009/011/016: semantic validator 규칙과 negative fixtures가 고정되고, schema가 선택한 AJV strict-mode에서 컴파일된다.
- CLD-014: 항목 배점과 partial-score 규칙이 재현 가능해진다.
- contract lock이 upstream commit·blob·SHA-256을 검증한다.
- `git diff --check`, JSON/YAML/schema tests, local-link tests가 모두 통과한다.

이 조건은 구현 준비도 재판정을 위한 것이며, 구현·유료 생성·최종 편집·제목/썸네일·게시 Human Gate를 승인하지 않는다.

## 9. 외부 근거

- OpenMontage upstream: `https://github.com/calesthio/OpenMontage`
- NIST Hyatt Regency walkway collapse record: `https://www.nist.gov/el/walkway-collapse-kansas-city-missouri-1981`
- TopView Query User Credit: `https://docs.topview.ai/reference/query_user_credit`
- TopView Query Credit Logs: `https://docs.topview.ai/reference/query_credit_logs`
- TopView Billing Rules: `https://docs.topview.ai/docs/billing-rules`
- TopView Canvas: `https://www.topview.ai/canvas`
- TopView 3D Shot Composer: `https://www.topview.ai/3d-shot-composer`

---

Stage 2 최종 판정: **`DESIGN_NOT_READY`**. 두 blocker는 아키텍처 폐기 없이 v2 계약 보강으로 해결 가능하지만, 해결 전 구현 승인으로 넘어가면 안 된다.
