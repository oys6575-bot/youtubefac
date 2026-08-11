# 유튜브공장 독립 제작 시스템 설계

**상태:** 사용자 승인됨  
**승인된 핵심 결정:** OpenMontage가 최상위 총괄 제작 시스템이며, TopView는 API 없이 수동 UI 핸드오프로 사용한다.

## 1. 목표

`유튜브공장`은 기존 `/Users/mk-macbook/Desktop/openmontage`와 기존 제작 프로젝트를 건드리지 않는 완전 독립형 영상 제작 저장소다. 조사와 증거 관리에서 시작해 대본, MK Visual Director의 숏 설계, 애니매틱, 에셋 제작, 편집, 합성, QC, 납품까지 OpenMontage가 일관된 상태와 승인 기록을 관리한다.

## 2. 지휘 구조

```text
사용자 — 최종 승인권자
  ↓
OpenMontage AI Executive Producer — 전체 상태·순서·승인·산출물의 진실원
  ├─ Evidence Director — 출처·주장·실제 자료
  ├─ Script Director — 대본과 주장 연결
  ├─ MK Visual Director — Visual Grammar·Sequence·Shot·전환·타이포
  ├─ Animatic Director — 제작 전 저비용 검토본
  ├─ Production Router — 경로 계획과 승인 후 실행
  ├─ Asset Director — 후보 관리와 선택 승인
  ├─ Edit/Compose Director — 편집·합성·오디오·자막
  └─ QC/Publish Director — 검증·납품·게시 승인
```

MK Visual Director는 OpenMontage와 경쟁하는 별도 감독이 아니라 OpenMontage 내부의 강화된 Scene Director다. OpenMontage checkpoint가 승인 상태의 유일한 진실원이다.

## 3. 파이프라인

```text
research
  → evidence_lock [Human Gate]
  → proposal [Human Gate]
  → script [Human Gate]
  → visual_plan
  → animatic [Human Gate]
  → budget [Human Gate]
  → assets
  → asset_selection [Human Gate]
  → edit
  → compose
  → final_review [Human Gate]
  → package
  → publish [Human Gate]
```

Router는 두 단계로 분리한다.

- Router Plan: VisualPlan 안에 숏별 경로와 비용 등급을 기록한다. 외부 생성은 실행하지 않는다.
- Router Execute: `GATE_ANIMATIC`과 `GATE_BUDGET` 이후에만 실제 자료 수집, 로컬 생성, 그래픽 제작 또는 TopView 작업지시서 생성을 수행한다.

## 4. 제작 경로

숏의 `provider_route.mode`는 다음 네 값만 허용한다.

- `REAL_INGEST`: 실제 사진·영상·문서·아카이브 자료
- `TOPVIEW_HANDOFF`: TopView 웹 UI에서 사람이 생성하는 반자동 경로
- `LOCAL_LTX`: 로컬 ComfyUI/LTX 생성
- `HYPERFRAMES`: 정확한 타이포·수치·도표·모션그래픽

Remotion은 최종 편집·합성 런타임으로 사용할 수 있고, HyperFrames는 정밀 그래픽 생성 및 필요 시 전체 런타임으로 선택할 수 있다. 런타임은 제안 단계에서 사용자에게 제시하고 승인된 값을 조용히 바꾸지 않는다.

## 5. TopView 반자동 계약

TopView에는 API 요청을 보내지 않는다. API 키, 자동 제출, 자동 폴링, 자동 결제 조회 및 브라우저 자동 클릭을 구현하지 않는다.

### 5.1 자동화되는 부분

OpenMontage는 숏별 `TopView Job Pack`을 만든다.

- 프로젝트·시퀀스·숏 ID
- 장면 목적과 내러티브 기능
- 양성·부정 프롬프트
- 참고 이미지·비디오의 로컬 사본과 SHA-256
- 권장 모델명, 화면비, 해상도, 길이, 카메라 움직임
- AI 재현 공개 라벨
- 기대 출력 파일명
- 사용자가 기록할 실제 모델명·사용 크레딧·생성 메모 필드

작업 묶음은 프로젝트 내부 `handoff/topview/outbox/<batch-id>/`에 생성되며 `job.json`, `INSTRUCTIONS.md`, `references/`로 구성한다.

### 5.2 사람이 수행하는 부분

사용자는 TopView 웹 UI에서 작업지시서를 보고 생성·재생성·비교·선택·다운로드한다. Canvas와 3D Shot Composer는 선택적 수동 탐색 도구이며 자동 Router 경로가 아니다.

### 5.3 다시 자동화되는 부분

선택 결과는 `handoff/topview/inbox/<batch-id>/`에 넣는다. 반입기는 파일명과 숏 ID, 확장자, ffprobe 메타데이터, 해상도, 화면비, 길이, SHA-256 및 provenance 기록을 검사한다. 통과한 파일은 후보 에셋으로 등록하지만 `GATE_ASSET_SELECTION` 이전에는 편집에 자동 유입시키지 않는다.

## 6. 핵심 산출물

- `evidence_registry.json`: source와 claim, exact literal의 근거
- `script.json`: 승인된 대본과 checksum
- `visual_plan.json`: Sequence/Shot, route, AI 포함 여부, 공개 라벨, overlay claim binding
- `scene_plan.json`: OpenMontage 호환 편집 계획
- `animatic_review.json`: 검토본과 사용자 판단
- `budget_approval.json`: 로컬/무료/수동 유료 경로의 예상량과 승인
- `topview_job_pack.json`: 수동 TopView 작업 계약
- `asset_manifest.json`: 모든 후보 에셋과 provenance
- `asset_selection.json`: 승인된 에셋만 기록
- `edit_decisions.json`, `render_report.json`, `final_review.json`, `publish_log.json`

정확한 날짜·수치·인용문은 `evidence_registry`의 claim을 통해서만 overlay에 들어갈 수 있다. AI 재현 또는 AI가 섞인 HYBRID 숏은 `contains_ai=true`와 통제된 공개 라벨을 가져야 한다.

## 7. 독립성 및 오염 방지

기준 소스는 OpenMontage 공식 `main` SHA `4eab34c5cfcccaa4f1970554928feccce73ee930`이다. 현재 로컬 작업 폴더 전체를 복사하지 않는다.

반드시 제외한다.

- `.env`, 토큰, 서비스 계정, 인증 설정
- 기존 `projects/`, 렌더, 다운로드 미디어
- `.venv/`, `node_modules/`
- `.cache/`, `.remotion/`, `.pytest_cache/`, `__pycache__/`, `tmp/`
- 기존 `.git/`

프로젝트, 캐시, 음악 라이브러리, TopView 전달 폴더는 모두 `유튜브공장` 내부 경로를 사용한다. 사용자 홈의 기존 OpenMontage 캐시를 기본값으로 사용하지 않는다.

## 8. 이관 및 업데이트 정책

- 공식 OpenMontage tracked 파일 전체를 깨끗한 기준본으로 가져온다.
- 로컬 승인 정책 스키마 패치 `6fa66e1f3a46`만 기능 단위로 재검증 후 적용한다.
- 로컬 모션 스킬 9종은 출처·라이선스·SHA-256을 기록하고 선별 이관한다.
- HyperFrames CLI와 스킬은 검증된 `0.7.106`에 맞춘다.
- Remotion은 기준본의 `4.0.484`로 첫 baseline을 통과한 뒤 `4.0.508`을 별도 변경으로 시험한다. 모든 `remotion` 계열 패키지는 같은 버전을 사용한다.
- Python은 이 Mac에서 검증된 3.11을 독립 `.venv`로 사용하고 설치 후 lock 파일을 남긴다.
- Three.js 의존성은 실제 3D composition 테스트가 통과할 때만 추가한다.

## 9. 오류 처리

- 승인되지 않은 단계의 실행 요청은 실패하고 다음 Gate를 알려준다.
- TopView inbox에 누락되거나 잘못 이름 붙은 파일은 이동·덮어쓰기 없이 거부 보고서를 만든다.
- 손상 영상과 규격 불일치는 후보 에셋에 등록하지 않는다.
- 동일 job과 동일 checksum의 중복 반입은 멱등하게 처리한다.
- 외부 생성 대기 상태는 실패가 아니라 `awaiting_manual_external`로 checkpoint에 남긴다.
- 유료 호출, 게시, 삭제 및 기존 프로젝트 변경은 자동으로 수행하지 않는다.

## 10. 검증 기준

구축 완료 판정에는 다음 증거가 필요하다.

1. 기준 SHA와 이관 manifest가 일치한다.
2. 비밀·기존 프로젝트·캐시가 새 저장소에 섞이지 않았다.
3. 새 파이프라인 manifest가 OpenMontage schema로 컴파일된다.
4. VisualPlan 유효 fixture는 통과하고 literal bypass·AI 공개 모순 fixture는 실패한다.
5. VisualPlan에서 OpenMontage scene_plan을 재현할 수 있다.
6. TopView job pack이 참조 파일과 checksum을 포함해 생성된다.
7. 유효 영상은 inbox에서 후보 에셋으로 반입되고, 잘못된 파일은 이유와 함께 거부된다.
8. TopView 결과가 asset selection 승인 전 편집 산출물에 들어가지 않는다.
9. Python 계약 테스트와 무과금 3~5초 smoke render가 통과한다.
10. Human Gate 승인·유료 호출·게시 없이도 전체 dry run이 가능하다.

