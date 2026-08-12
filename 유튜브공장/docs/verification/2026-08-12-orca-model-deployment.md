# Orca 모델 배치·주제검색 파일럿 최종 검증

검증일: 2026-08-12  
통합 기준 커밋: `486e118aa005b67a640dc5a380b3bd3a2903c8e5`  
판정: **PASS — 실제 모델 배치와 첫 파일럿이 사용자 주제 선택 Human Gate에 정상적으로 도달함**

## 1. 검증 범위

- 새 `youtubefac` Orca 저장소와 여섯 역할 worktree의 격리
- 각 역할에 지정된 실제 모델·effort·실행 루트
- OpenMontage canonical `projects/` 공유와 checkpoint/Human Gate 계약
- Research → Verification → Coordinator 커밋·SHA-256 핸드오프
- 로컬 텍스트/미디어 리소스의 원자적 lease 배타 제어
- YouTube·Pexels·Pixabay·Unsplash 연결과 비밀키 최소 권한
- 물리적 붕괴 건축물·구조물 주제 후보 12건의 생성·독립 검증·승인 대기
- 기존 Hyatt/OpenMontage Orca 환경 보존

## 2. 격리와 진실원

| 항목 | 확인 결과 |
|---|---|
| 새 Orca 저장소 | `72c83ff9-bf6e-4b0c-8507-4b7184305c11` |
| Orca Run | `run_e1a94da8c81f` |
| Git base branch | `agent/youtube-factory-runtime` |
| 역할 worktree | control, research, verification, story/visual, production, qa의 6개 |
| 모든 역할 시작 위치 | 각 worktree의 `유튜브공장/` |
| canonical runtime root | 원본 worktree의 `유튜브공장/projects/` |
| 공유 방식 | 모든 역할에 동일한 절대 `OPENMONTAGE_PROJECTS_DIR` 주입 |
| 기존 Hyatt 환경 | 별도 Orca 저장소 `94d9b113-dc57-421c-b1d6-a72547797ef1` 및 기존 7개 worktree 그대로 보존 |

Orca는 역할·작업공간·작업 DAG를 조정한다. 산출물, 진행
상태, 사용자 승인의 진실원은 OpenMontage checkpoint이다. Orca task의
`completed`는 Human Gate 승인으로 해석하지 않는다.

## 3. 실제 모델 배치

| 역할 | 실행기·모델 | 역할 확인 |
|---|---|---|
| Control/Coordinator | Codex `gpt-5.6-sol`, `xhigh` | DAG, 비용, Gate, 커밋 통합 |
| Research | Hermes + LM Studio `qwen3.6-35b-a3b-mlx` | 후보 탐색·점수 초안 |
| Verification | Codex `gpt-5.6-sol`, `high` | 출처·범위·점수·해시 독립 검증 |
| Story/MK Visual Director | Claude Opus 5, `max` | Visual Grammar, Sequence/Shot, 카메라 속도 곡선, 사진-영상 전환, 타이포·모션 |
| Production Manager | Hermes + LM Studio `qwen3.6-35b-a3b-mlx` | provider-neutral 작업 묶음·에셋 ledger·TopView 수동 handoff |
| QA | Codex `gpt-5.6-sol`, `high` | 산출물·프레임·오디오·자막·사실 overlay 기술 QC |

`scripts/orca/model_preflight.py`는 Orca, Codex, Claude, Hermes, Git, LM Studio와
지정 Qwen 모델의 실재 가용성을 모두 PASS로 보고했다. Production 역할은
지정 worktree에서 실제 `PRODUCTION_MODEL_READY` 응답을 받았고, 완료 후
로컬 lease를 반납했다.

## 4. 비밀키와 무료 자료원

- canonical, Research, Production `.env`는 모두 mode `0600`이며 Git ignored이다.
- Research에는 `YOUTUBE_API_KEY`만, Production에는 `PEXELS_API_KEY`,
  `PIXABAY_API_KEY`, `UNSPLASH_ACCESS_KEY`만 허용된다.
- Control, Verification, Visual Director, QA에는 API 비밀을 배치하지 않았다.
- 2026-08-12 실제 연결 재검사: YouTube `200`, Pexels `200`, Pixabay `200`,
  Unsplash `200`.
- 연결 검사는 최소 검색 요청만 했으며 에셋 다운로드, 유료 provider
  호출, 제작을 시작하지 않았다.

## 5. 주제검색 파일럿 결과

1. 공식·1차 출처가 있는 물리적 붕괴 사건 12건을 후보로 구성했다.
2. 지정된 실제 Qwen 모델이 상한 폭이 고정된 8개 항목 점수를 생성했다.
3. 초기 Hermes 전체-agent 실행은 대형 문맥 누적으로 2회 시간 초과했고,
   환경 경로 누락 실패 1회를 기록했다. 실패 이력은 숨기지 않았다.
4. 작업을 `공식 출처 확인 → compact Qwen 점수 → Codex 검증`으로 분리해
   동일 Qwen 모델으로 실행을 완료했다.
5. Codex 1차 독립 검증은 Tacoma와 Québec의 점수 사유가 기존 영상
   자료의 양·유무를 평가한 문제를 발견하고 **FAIL**로 차단했다.
6. Research 이력에서 두 사유만 provider-neutral 사건·물리 메커니즘 기준으로
   교정했고, 96개 원점수·총점·순위는 유지했다.
7. Codex 2차 검증은 교정된 정확한 바이트에 대해 **PASS**를 기록했다.

### 핸드오프 결속

| 산출물 | 값 |
|---|---|
| 교정 Research commit | `a5b2984184993757ec0d68e976db160caac88a93` |
| 주제 후보 JSON SHA-256 | `b81d12af4557f71305c2dced638a4b0392f1e0112758c40272fd988d4d9bf3e4` |
| PASS review commit | `486e118aa005b67a640dc5a380b3bd3a2903c8e5` |
| canonical verification SHA-256 | `666694ef4cc960ecb923ce84a25567627b7bb23cbdc6e479d991e01b86adda40` |

Coordinator는 커밋과 SHA-256이 PASS 검증 artifact와 일치하는 직선
이력만 `--ff-only`로 통합했다.

## 6. 사용자 Human Gate

canonical project:
`projects/collapse-topic-pilot-2026-08-12/`

| 상태 | 현재 값 |
|---|---|
| `topic_search` | `completed`, `human_approved: false` |
| `topic_verification` | `completed`, verdict `PASS`, `human_approved: false` |
| `topic_approval` | `awaiting_human`, `human_approved: false` |
| `topic_selection.selection_status` | `PENDING` |
| `selected_candidate_id` | `null` |
| 제작 시작 | `false` |
| 유료 호출 시작 | `false` |

따라서 다음 단계는 모델이 임의로 진행할 수 없다. 사용자가 후보 하나를
명시적으로 선택해야 deep research로 이동한다.

## 7. 검사 결과

- `tests/contracts` + 리소스 lease + 모델 preflight + 비밀키 배치:
  **746 passed, 7 skipped**
- exact shortlist schema, 순위, 해시, canonical artifact/checkpoint: PASS
- Human Gate 우회 거부: PASS
- 로컬 text/media 동시 lease 충돌 거부와 만료·충돌 복구: PASS
- TopView API/automatic dispatch 금지, manual ingest manifest 요구: PASS
- 역할별 모델·effort·쓰기 권한·secret allowlist: PASS
- model preflight: PASS
- 활성 shared local-heavy lease: 없음
- Git 추적 파일에 `.env`: 없음

## 8. 현재 운영 판정

**모델 배치와 주제검색 파일럿 구조는 실제 운영 가능하다.**

이번 검증이 입증한 범위는 주제 탐색, 점수화, 독립 검증, 승인 대기까지다.
실제 대본·VisualPlan·TopView handoff·편집·렌더는 선택된 주제로 다음
파일럿을 시작할 때 별도 검증한다.
