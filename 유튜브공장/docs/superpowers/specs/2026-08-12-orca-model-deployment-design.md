# 유튜브공장 Orca 모델 배치 설계

작성일: 2026-08-12  
상태: 구현 기준선

## 1. 목적

`유튜브공장`을 기존 Hyatt·OpenMontage 작업공간과 분리된 Orca 프로젝트로
등록하고, 조사·검증·연출·제작관리·최종 QC를 각 모델의 강점에 맞게 배치한다.
첫 실증은 「무너진 이유」 주제 후보를 생성하고 독립 검증하는 무과금
파일럿으로 한다.

Orca는 여러 작업공간과 모델의 협업을 조정한다. 제작 상태와 승인 기록의
진실원은 최상위 OpenMontage Control Plane이다. Orca의 작업 완료나 모델의
자기 보고는 OpenMontage Human Gate 승인을 대체하지 않는다.

## 2. 최종 계층

```text
Orca — 유튜브공장 협업·격리 계층
└─ OpenMontage Control Plane — 산출물·상태·승인의 진실원
   ├─ 총괄 감독 / Coordinator
   │  └─ Codex gpt-5.6-sol, max
   ├─ 주제·자료 조사
   │  └─ Hermes + LM Studio Qwen3.6-35B-A3B-MLX
   ├─ 사실·출처·계약 검증
   │  └─ Codex gpt-5.6-sol, high
   ├─ Human Gate — 사용자의 주제 승인
   ├─ 스토리·MK Visual Director
   │  └─ Claude Opus 5, max
   ├─ 제작 관리자
   │  └─ Hermes + LM Studio Qwen3.6-35B-A3B-MLX
   ├─ 실행 도구
   │  ├─ 실제 자료 ingest
   │  ├─ TopView 수동·반자동 handoff
   │  ├─ HyperFrames / Remotion
   │  └─ ComfyUI / Blender / Houdini
   └─ 최종 기술·영상 QC
      └─ Codex gpt-5.6-sol, high
```

## 3. 역할 계약

### 3.1 Coordinator

- 모델: Codex `gpt-5.6-sol`, effort `max`
- 책임: 작업 DAG, 범위·Human Gate·비용·리소스 레인 통제, 검증 결과 병합
- 쓰기: 조정 기록, 승인 대기 상태, 검증된 커밋 통합
- 금지: 사용자 승인 대행, 유료 호출, 자동 게시, 사실 근거 없는 제작 진행

### 3.2 Research

- 모델: Hermes 프로필 `ytf-research` + LM Studio
  `qwen3.6-35b-a3b-mlx`
- 책임: 폭넓은 후보 발굴, 공식·1차 출처 우선 수집, 출처가 붙은 임시 점수 초안
- 쓰기: `research/topic-candidates/`의 후보 초안만
- 금지: 자기 검증, Human Gate 승인, 대본·장면·미디어 생성
- 검색 범위: 공식 조사기관·정부·대학·법원·기술기관을 우선하고,
  YouTube·Reddit·GitHub·Hugging Face는 관심도·도구·사례 확인용 보조면으로만
  사용한다.

### 3.3 Verification

- 모델: Codex `gpt-5.6-sol`, effort `high`
- 책임: 사건 범위, 날짜·원인·출처, 점수 근거, 스키마와 결정론 테스트 검증
- 쓰기: `reviews/`의 검증 보고서만
- 금지: 조사 결과를 몰래 고치기, 후보 승인, 제작 시작

### 3.4 Story and Visual Director

- 모델: Claude Opus 5, effort `max`
- 책임: 승인된 사실을 이야기 구조, Visual Grammar, Sequence, Shot, 카메라,
  조명, 속도 곡선, 사진-영상 전환, 타이포·모션그래픽·음향 큐로 변환
- 쓰기: 승인된 주제의 대본·VisualPlan·animatic 지시
- 금지: 검증된 사실 변경, 출처 삭제, 미승인 주제로 제작 진행, Gate 승인

### 3.5 Production Manager

- 모델: Hermes 프로필 `ytf-production` + 같은 로컬 Qwen
- 책임: 승인된 VisualPlan을 provider-neutral 작업 묶음으로 분해하고,
  에셋 ledger와 TopView 수동 handoff 패킷을 관리
- 금지: 자동 provider 변경, 유료 실행, 에셋 선택 자기 승인, 게시

### 3.6 QA

- 모델: Codex `gpt-5.6-sol`, effort `high`
- 책임: 산출물 메타데이터, 프레임, 오디오, 자막, 사실 overlay, manifest 일치 검증
- 쓰기: QC 보고서만
- 금지: 원본 수정, 자동 수리, 최종 승인·게시

### 3.7 선택적 Second Opinion

LM Studio의 `gemma-4-31b-it-mlx`는 중요한 상충 판단에만 임시로 호출한다.
상시 로드하거나 Qwen과 동시 상주시키지 않으며, 최종 판정 권한은 없다.

## 4. 작업공간과 데이터 이동

부모 Git 저장소 `youtubefac`을 Orca에 등록하되 모든 역할의 실행 시작점은
반드시 각 worktree의 `유튜브공장/`으로 고정하고 역할별 Git worktree를 사용한다.

```text
youtubefac 원본 작업공간
├─ control-codex
├─ research-hermes-qwen
├─ verification-codex
├─ visual-director-claude
├─ production-hermes-qwen
└─ qa-codex
```

- 추적 가능한 조사·설계·검증 산출물은 역할 브랜치 커밋으로 이동한다.
- Coordinator는 Verification이 통과한 커밋만 통합한다.
- 대용량 미디어는 Git으로 이동하지 않는다. 원본 `유튜브공장/projects/`를
  canonical runtime root로 사용하고 역할별 단일 작성자 하위 경로를 둔다.
- 모든 역할의 비밀이 아닌 runtime 환경에 동일한 절대
  `OPENMONTAGE_PROJECTS_DIR`을 주입한다. Backlot도 이 경로만 관찰한다.
- 다른 역할은 필요한 경로만 명시적으로 읽는다. 광범위한 홈 디렉터리 공유와
  기존 OpenMontage `projects/` 공유는 금지한다.
- 기존 Orca Run·worktree·Hyatt 프로젝트는 참조하거나 재사용하지 않는다.
- 역할 간 handoff에는 `source_commit`, 상대 artifact 경로, SHA-256을 포함한다.
  검증 보고서도 verdict와 동일 세 필드, 검증 시각, 확인 URL을 기계 판독
  형태로 저장하며 Coordinator는 커밋과 해시가 모두 같을 때만 통합한다.

## 5. 모델 라우팅과 장애 시 정책

모델과 역할은 `config/orca-model-routing.yaml`에 고정한다. 실행기는 요청 모델이
없거나 인증되지 않은 경우 조용히 다른 모델로 바꾸지 않는다.

- Codex/Claude 장애: 해당 역할을 `BLOCKED_MODEL_UNAVAILABLE`로 멈춘다.
- LM Studio/Qwen 장애: Research·Production을 멈추고 재시도한다. Codex가
  조사 역할을 자동 인수하지 않는다.
- Gemma는 명시적 `second_opinion` 작업에서만 사용한다.
- TopView는 API provider가 아니다. 사용자가 웹 UI에서 실행하고, 내보낸
  결과를 checksum·모델명·작업 지시와 함께 수동 ingest한다.

## 6. 리소스 레인

M5 Max 128GB에서 Qwen 로드는 약 37.75GB를 사용한다. ComfyUI의 고용량
영상 생성과 LM Studio의 대형 로컬 추론을 동시에 실행하지 않는다.

```text
Cloud lane: Codex + Claude                      병렬 허용
Local text lane: LM Studio Qwen 또는 Gemma      한 번에 하나
Local media lane: ComfyUI / Blender / Houdini   Qwen과 배타 실행
Manual lane: TopView 브라우저                   사용자 조작
```

Orca 작업 상태는 `LOCAL_TEXT_ACTIVE`, `LOCAL_MEDIA_ACTIVE`, `IDLE` 중 하나로
기록한다. 상태 문자열만 믿지 않고 owner/task ID·획득 시각·TTL을 가진 원자적
lease를 canonical runtime root에 둔다. 충돌 시 새 작업을 제출하지 않고,
만료 lease는 PID·작업 상태 확인 뒤 Coordinator만 복구한다.

## 7. 비밀키 최소 권한

- canonical `.env`: mode `0600`, Git ignored
- Research: 필요한 경우 `YOUTUBE_API_KEY`만 별도 역할 `.env`에 복사
- Production: `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `UNSPLASH_ACCESS_KEY`만
  별도 역할 `.env`에 복사
- Coordinator, Verification, Visual Director, QA: API 비밀 없음
- 복사 도구는 allowlist만 허용하고 값은 출력·로그·리뷰 문서에 남기지 않는다.
- Pexels·Pixabay·Unsplash는 연결 상태만 사전 점검한다. 유료 provider 키는
  배치하지 않는다.

## 8. Human Gates

다음 상태는 모델이나 Orca가 변경할 수 없다.

1. `topic_approval`: 주제 선택
2. `animatic_approval`: 구성·사실·예산 검토
3. `budget_approval`: 유료 호출 직전
4. `asset_selection`: 생성·수집 에셋 선택
5. `final_edit_approval`: 최종 편집 승인
6. `publish_approval`: 공개·업로드 승인

첫 파일럿은 `topic_approval: PENDING`에서 반드시 멈춘다.

## 9. 첫 실증 작업

### 입력

- 고정된 `config/topic-selection-scorecard.yaml`
- 과거 후보 목록은 사실 자료가 아니라 검색 seed로만 사용
- 범위: 사람이 만든 건축물·구조물의 실제 물리적 전체 또는 부분 붕괴

### 흐름

1. OpenMontage `topic_search` stage를 시작하고 Research/Qwen이 10개 이상의
   후보와 각 후보의 공식·1차 출처를 수집한다.
2. 결정론 점수 엔진으로 임시 점수와 순위를 계산하고 canonical
   `topic_shortlist` artifact와 checkpoint를 기록한다.
3. Research 커밋에서 Verification 입력 worktree를 만들고 Verification/Codex가
   범위·출처·점수 근거와 정확한 artifact 해시를 독립 확인한다.
4. `topic_verification` artifact와 checkpoint를 기록한다.
5. Coordinator가 커밋·해시가 일치한 통과 artifact만 원본 브랜치에 통합한다.
6. `topic_selection` artifact를 `selection_status: PENDING`으로 만들고
   `topic_approval` checkpoint를 `awaiting_human`, `human_approved: false`로
   기록한 뒤 중지한다.

### 출력

- `research/topic-candidates/2026-08-12-collapse-topic-shortlist.json`
- `research/topic-candidates/2026-08-12-collapse-topic-shortlist.md`
- `reviews/2026-08-12-collapse-topic-shortlist-verification.md`
- Orca Run의 역할별 task 상태와 handoff 기록

## 10. 완료 조건

- 새 저장소가 Orca에 등록되고 base ref가 현재 유튜브공장 기준 커밋으로 고정됨
- 여섯 역할 worktree가 기존 프로젝트와 분리되어 생성됨
- Codex·Claude 인증과 Hermes/Qwen 실제 응답을 역할별 작업공간에서 확인함
- 역할·권한·비밀·리소스 계약 테스트가 통과함
- Research → Verification → Coordinator handoff를 실제 Orca Run에서 수행함
- 후보 JSON/Markdown과 독립 검증 보고서가 생성되고 모든 관련 테스트가 통과함
- 유료 호출·TopView 자동화·게시 없이 `topic_approval: PENDING`에서 정지함
- 복구 절차와 사용 명령이 운영 문서에 기록됨
