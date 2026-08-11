# ADR-001: TopView를 주력 클라우드 생성 Provider로 채택

- 상태: Accepted for design review
- 결정일: 2026-08-11
- 최종 승인: 사용자 Human Gate 대기

## Context

MK Visual Director는 한 편의 영상을 수동으로 만드는 도구가 아니라, 여러 주제와 여러 LLM을 사용하면서도 동일한 제작 규칙·데이터 계약·검수 기준을 유지해야 한다.

Newtake는 방짜유기 레퍼런스 영상에서 다음 강점을 보여줬다.

- 한국어 중심의 노드 제작 UX
- 스크립트에서 스토리보드 생성
- 캐릭터·장소·소품 시트
- 디렉터 콘솔과 3D blocking
- 멀티앵글·9분할·조명 프리셋
- 빠른 수동 탐색

그러나 공개 범위에서 안정된 공식 API 계약을 확인하지 못했고, 약관상 로봇·스크레이퍼 기반 UI 자동화를 주력 통합 방식으로 삼기 어렵다.

TopView는 다음 공개 통합점을 제공한다.

- 공식 REST API와 인증 문서
- 하나의 API에서 여러 이미지·영상 모델 라우팅
- Canvas와 AI agent
- 3D Shot Composer
- 공식 MCP 연결 지점
- task 기반 비동기 처리
- 동시성·저장 기간·과금 문서

## Decision

TopView를 주력 클라우드 생성 provider로 사용한다.

~~~text
topview_canvas
= 아이디어 탐색, 프리비즈, 후보 비교, 3D blocking

topview_api
= 승인된 ShotPlan의 자동 생성

openmontage
= source of truth, task polling, 다운로드, metadata, 비용, QC
~~~

Newtake는 제거하지 않는다. 다음 두 용도로만 유지한다.

1. 수동 프리비즈·연출 UX의 벤치마크
2. HERITAGE_FORGE와 같은 Visual Grammar 레퍼런스

## Why TopView wins for this system

| 기준 | Newtake | TopView | 결정 영향 |
|---|---|---|---|
| 수동 영화 연출 UX | 매우 강함 | 강함 | Newtake 우위 |
| API 문서 | 확인 불가 | 공식 문서 존재 | TopView 결정적 우위 |
| MCP/agent 통합 | 공개 범위 불명확 | 공식 제공 | TopView 우위 |
| 모델 라우팅 | UI 중심 | API model field 중심 | TopView 우위 |
| 3D 프리비즈 | 강함 | 강함 | 대체 가능 |
| 한국어 접근성 | 우수 | 보통 | Newtake 우위 |
| OpenMontage 자동화 | 수동 export 의존 | task/poll/download 가능 | TopView 결정적 우위 |
| 장기 재현성 | 불명확 | 외부 registry로 관리 가능 | TopView 우위 |

## Consequences

### Positive

- Visual Director가 특정 영상 모델명에 종속되지 않는다.
- 승인된 ShotPlan만 API로 보내 비용을 제어할 수 있다.
- 결과물을 즉시 로컬에 수집해 원격 링크 만료에 대응할 수 있다.
- TopView 안의 모델이 바뀌어도 provider 인터페이스를 유지할 수 있다.

### Negative

- 웹 계정의 표준 크레딧은 API와 공유되지만 기능별 과금 방식은 다를 수 있다.
- Ultra 크레딧과 Unlimited·프로모션 혜택을 API 자동화 가용량으로 간주할 수 없다.
- 공유 자원 pool의 queue 우선순위는 존재하지만 제작 일정의 SLA로 간주할 수 없다.
- API 결과 URL은 별도 명시가 없으면 7일만 유효하므로 즉시 다운로드가 필요하다.
- 외부 provider이므로 미공개·민감 자료는 업로드 검토가 필요하다.

## Required safeguards

1. 첫 구매는 월간 pilot로 제한한다.
2. 연간·Unlimited 플랜은 실측 전 구매하지 않는다.
3. API 호출 전 estimated cost와 사용자 budget gate를 기록한다.
4. 결과 URL을 받은 즉시 로컬 저장하고 checksum을 기록한다.
5. 실패 generation도 비용이 발생했는지 실제 task metadata로 확인한다.
6. TopView 프로젝트를 source of truth로 간주하지 않는다.
7. `/user/credit/detail`과 credit log로 실제 차감액을 수집한다.

## Revisit triggers

다음 조건 중 하나가 발생하면 이 ADR을 재검토한다.

- Newtake가 공식 API·MCP·export contract를 공개
- TopView API의 안정성 또는 비용이 pilot 기준을 지속적으로 초과
- 로컬 모델이 목표 품질과 처리량을 충족
- 다른 provider가 동일 계약으로 더 낮은 실패율을 입증

## Sources

- https://www.topview.ai/openapi
- https://docs.topview.ai/docs/getting-started
- https://docs.topview.ai/docs/billing-rules
- https://docs.topview.ai/docs/concurrency-and-storage
- https://www.topview.ai/pricing
- https://www.topview.ai/canvas
- https://www.topview.ai/3d-shot-composer
- https://www.topview.ai/mcp
- https://www.newtake.com/ko
- https://www.newtake.com/ko/statement/terms-of-service
