# MK Visual Director

LLM 교체가 가능하고, 실제 자료·AI 재현·정밀 모션그래픽을 결합하는 시네마틱 다큐멘터리 제작 시스템의 설계 기록과 독립 실행 프로젝트입니다.

현재 설계 기록은 보존돼 있으며, 실제 실행 시스템은 [`유튜브공장/`](유튜브공장/)에 독립 구축됐습니다.

구축 완료는 유료 생성·최종 영상·외부 공개에 대한 승인을 의미하지 않습니다. TopView 결제, 모델 다운로드의 라이선스 동의, 최종 렌더 채택, 게시에는 각각 사용자 Human Gate가 필요합니다.

## 실행 프로젝트

1. [`유튜브공장 시작 안내`](유튜브공장/docs/operations/START-HERE.md)
2. [`도구·스킬·TopView·GitHub·Hugging Face·Reddit 전수 검수`](유튜브공장/docs/research/2026-08-11-tool-skill-capability-audit.md)
3. [`TopView 수동 운용 안내`](유튜브공장/docs/operations/TOPVIEW-MANUAL-RUNBOOK.md)

`유튜브공장/`은 자체 OpenMontage 소스, Python·Node lock, Remotion, HyperFrames 스킬, ComfyUI 안정판, 로컬 모델 리비전 장부를 포함한다. 기존 OpenMontage 프로젝트·환경파일·캐시·모델은 포함하지 않는다.

## 최종 결정

- 주력 클라우드 생성 provider: **TopView**
- 최상위 총괄 감독·진실원: **OpenMontage**
- 전문 장면 감독: **OpenMontage 내부의 MK Visual Director**
- 정밀 타이포·수치·도면·자료 전환 contract: **HyperFrames 우선 권고**
- 편집·오디오·출처·비용·QC·납품: **OpenMontage가 Remotion·HyperFrames·FFmpeg를 지휘**
- 로컬 초안·fallback: **LTX 계열 로컬 provider**
- TopView 운용: **API 없이 사용자 수동 UI handoff**
- Newtake: 주력 시스템이 아니라 수동 연출 UX와 방짜유기 레퍼런스의 학습 대상

## 문서 읽는 순서

1. [유튜브공장 시작 안내](유튜브공장/docs/operations/START-HERE.md)
2. [최종 설계안 v2](docs/MK_VISUAL_DIRECTOR_FINAL_DESIGN_v2.md)
3. [TopView 채택 결정 기록](docs/ADR-001-TOPVIEW-PRIMARY-PROVIDER.md)
4. [OpenMontage 통합 결정 기록](docs/ADR-002-OPENMONTAGE-INTEGRATION.md)
5. [방짜유기 영상·Newtake 분석](docs/REFERENCE-BANGJJA-NEWTake-ANALYSIS.md)
6. [VisualPlan v2 JSON Schema](schemas/visual-plan.v2.schema.json)
7. [Hyatt Golden Sequence](golden-tests/HYATT-60-90S-GOLDEN-SEQUENCE.md)
8. [방짜유기 스타일 검증](golden-tests/BANGJJA-STYLE-ACCEPTANCE-TEST.md)
9. [최종 교차검수 합의](reviews/final-consensus.md)
10. [Codex v2 검증](reviews/codex-v2-verification.md)

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
