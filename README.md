# MK Visual Director

LLM 교체가 가능하고, 실제 자료·AI 재현·정밀 모션그래픽을 결합하는 시네마틱 다큐멘터리 제작 시스템의 최종 설계 검수 저장소입니다.

현재 상태는 **DESIGN_READY_FOR_CROSS_REVIEW**입니다.

이 저장소는 아직 구현 승인을 의미하지 않습니다. Claude 독립검수, Codex 독립검수, 상호 교차검수, 최종 합의, 사용자 Human Gate가 끝나기 전에는 구현·유료 API 대량 호출·최종 렌더·외부 공개를 시작하지 않습니다.

## 최종 결정

- 주력 클라우드 생성 provider: **TopView**
- 시각 감독: **MK Visual Director**
- 정밀 타이포·수치·도면·자료 전환 contract: **HyperFrames 우선 권고**
- 편집·오디오·출처·비용·QC·납품: **OpenMontage**
- 로컬 초안·fallback: **LTX 계열 로컬 provider**
- Newtake: 주력 시스템이 아니라 수동 연출 UX와 방짜유기 레퍼런스의 학습 대상

## 문서 읽는 순서

1. [최종 설계안](docs/MK_VISUAL_DIRECTOR_FINAL_DESIGN_v1.md)
2. [TopView 채택 결정 기록](docs/ADR-001-TOPVIEW-PRIMARY-PROVIDER.md)
3. [OpenMontage 통합 결정 기록](docs/ADR-002-OPENMONTAGE-INTEGRATION.md)
4. [방짜유기 영상·Newtake 분석](docs/REFERENCE-BANGJJA-NEWTake-ANALYSIS.md)
5. [VisualPlan JSON Schema](schemas/visual-plan.schema.json)
6. [Source Registry Schema](schemas/source-registry.schema.json)
7. [Hyatt Golden Sequence](golden-tests/HYATT-60-90S-GOLDEN-SEQUENCE.md)
8. [방짜유기 스타일 검증](golden-tests/BANGJJA-STYLE-ACCEPTANCE-TEST.md)
9. [Claude 독립검수 프롬프트](reviews/CLAUDE-INDEPENDENT-REVIEW-PROMPT.md)
10. [Claude↔Codex 교차검수 Runbook](reviews/CROSS-REVIEW-RUNBOOK.md)
11. [Codex 독립검수 결과](reviews/codex-independent-review.md) — Claude 독립검수가 끝난 뒤 읽기

## 교차검수 순서

~~~text
FINAL DESIGN v1
   ├─ Claude independent review
   └─ Codex independent review
          ↓
Claude reviews Codex findings
Codex reviews Claude findings
          ↓
final_consensus.md
          ↓
FINAL DESIGN v2 candidate
          ↓
USER HUMAN GATE
          ↓
implementation planning
~~~

## 핵심 원칙

1. 대본에서 바로 영상을 만들지 않는다. **대본 → 의미 → Sequence → Shot → 제작** 순서를 지킨다.
2. 생성 영상에 정확한 글자·수치·화살표를 굽지 않는다. 항상 clean plate와 overlay를 분리한다.
3. 실제 자료와 AI 재현을 화면상·메타데이터상 구분한다.
4. TopView는 생성·프리비즈 provider이며 프로젝트의 source of truth가 아니다.
5. OpenMontage 프로젝트와 로컬 asset registry를 source of truth로 둔다.
6. 유료 생성 전 Animatic Human Gate를 통과해야 한다.
7. “작업 완료”는 파일 존재가 아니라 미디어·출처·프레임·오디오·상태를 검증한 뒤에만 선언한다.
8. OpenMontage가 HyperFrames와 Remotion을 모두 사용할 수 있으면 proposal에서 두 경로를 제시하고, 사용자가 고른 하나의 `render_runtime`을 잠근다.

## 주요 외부 근거

- [TopView API](https://www.topview.ai/openapi)
- [TopView API 문서](https://docs.topview.ai/docs/getting-started)
- [TopView Canvas](https://www.topview.ai/canvas)
- [TopView 3D Shot Composer](https://www.topview.ai/3d-shot-composer)
- [TopView 가격](https://www.topview.ai/pricing)
- [Newtake](https://www.newtake.com/ko)
- [분석한 YouTube 영상](https://www.youtube.com/watch?v=APJcwbxWtfY)
