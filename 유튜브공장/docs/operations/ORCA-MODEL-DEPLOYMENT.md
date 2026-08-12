# Orca 모델 배치 운영서

작성일: 2026-08-12  
적용 범위: `유튜브공장` 전용 Orca 작업환경

## 운영 원칙

- Orca는 역할별 작업공간과 대화를 분리하고 작업 전달을 기록한다.
- OpenMontage는 프로젝트 산출물, 체크포인트, Human Gate의 진실원이다.
- 모든 에이전트의 시작 폴더는 각 worktree의 `유튜브공장/`이다.
- 대용량·실행 상태는 원본 저장소의 `유튜브공장/projects/` 하나만 공유한다.
- `.env` 파일이 셸에 자동 적용된다고 가정하지 않는다. 에이전트를 시작할 때
  `OPENMONTAGE_PROJECTS_DIR`를 실행 명령에 명시한다.
- TopView는 API가 아니라 사람이 웹 UI에서 실행하는 수동·반자동 경로다.
- 유료 호출, 에셋 선택, 최종 편집, 게시, 주제 선택은 사용자가 승인한다.

## 역할과 실제 모델

| 역할 | 실행기와 모델 | effort | 전용 worktree | 쓰기 범위 |
|---|---|---:|---|---|
| 총괄·통합 | Codex `gpt-5.6-sol` | `xhigh` | `ytf-control-codex` | 조정 기록, 검증된 커밋 통합 |
| 주제·자료 조사 | Hermes + LM Studio `qwen3.6-35b-a3b-mlx` | 프로필 `high` | `ytf-research-hermes` | `research/topic-candidates/` |
| 사실·출처 검증 | Codex `gpt-5.6-sol` | `high` | `ytf-verification-codex` | `reviews/` |
| 스토리·영상연출 | Claude `claude-opus-5` | `max` | `ytf-visual-director-claude` | 승인 뒤 대본·VisualPlan·animatic |
| 제작관리 | Hermes + LM Studio `qwen3.6-35b-a3b-mlx` | 프로필 `high` | `ytf-production-hermes` | 제작 패킷·에셋 장부 |
| 최종 QC | Codex `gpt-5.6-sol` | `high` | `ytf-qa-codex` | `reviews/` |

Codex의 총괄 effort는 `max`가 아니다. 현재 Orca 1.4.180이
`gpt-5.6-sol/max` 조합을 거부하고 `xhigh`를 실제로 수락하므로, 조용한 강등
없이 지원되는 값을 계약에 고정했다.

## 고정 경로

```text
Git 원본
/Users/mk-macbook/Documents/Codex/2026-08-11/
  referenced-chatgpt-conversation-this-is-an/work/youtubefac

공용 OpenMontage 프로젝트 루트
/Users/mk-macbook/Documents/Codex/2026-08-11/
  referenced-chatgpt-conversation-this-is-an/work/youtubefac/유튜브공장/projects

Orca worktree 루트
/Users/mk-macbook/orca/workspaces/youtubefac/
```

현재 Orca 등록 저장소 ID는
`72c83ff9-bf6e-4b0c-8507-4b7184305c11`이고, 기준 브랜치는
`agent/youtube-factory-runtime`이다. 첫 배치 검증 Run은
`run_e1a94da8c81f`이다. 새 Run은 기존 Run이나 Hyatt worktree를 재사용하지
않는다.

## 사전 점검

저장소 원본의 `유튜브공장/`에서 실행한다.

```bash
PYTHONPATH=. ./.venv/bin/python scripts/orca/model_preflight.py
```

성공 조건은 다음과 같다.

- Orca runtime 응답
- Codex 로그인 상태
- Claude 인증 상태
- Hermes 실행 가능
- Git 상태 확인 가능
- LM Studio `/v1/models`에서 `qwen3.6-35b-a3b-mlx` 확인
- 역할에 필요한 키의 존재 여부 확인

보고서는 키 이름과 존재 여부만 출력하며 값을 출력하지 않는다.

## 역할 환경 배치

각 worktree에는 역할별 mode `0600` `.env`를 둔다. 비밀은 allowlist만
복사하고 공용 프로젝트 경로를 함께 기록한다.

```bash
PYTHONPATH=. ./.venv/bin/python scripts/orca/provision_role_env.py \
  --role research \
  --source .env \
  --target /Users/mk-macbook/orca/workspaces/youtubefac/ytf-research-hermes/유튜브공장/.env \
  --projects-root /Users/mk-macbook/Documents/Codex/2026-08-11/referenced-chatgpt-conversation-this-is-an/work/youtubefac/유튜브공장/projects
```

역할별 비밀 허용 범위는 다음뿐이다.

- Research: `YOUTUBE_API_KEY`
- Production: `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `UNSPLASH_ACCESS_KEY`
- Control, Verification, Visual Director, QA: 없음

## 실제 실행 명령

아래 예처럼 공용 프로젝트 경로를 **프로세스 시작과 동시에** 넣는다.

### Codex

```bash
export OPENMONTAGE_PROJECTS_DIR=/Users/mk-macbook/Documents/Codex/2026-08-11/referenced-chatgpt-conversation-this-is-an/work/youtubefac/유튜브공장/projects
exec codex -C 유튜브공장 -m gpt-5.6-sol -c model_reasoning_effort="high" -a never
```

총괄 역할만 `high` 대신 `xhigh`를 사용한다.

### Claude Visual Director

```bash
export OPENMONTAGE_PROJECTS_DIR=/Users/mk-macbook/Documents/Codex/2026-08-11/referenced-chatgpt-conversation-this-is-an/work/youtubefac/유튜브공장/projects
cd 유튜브공장
exec claude --model claude-opus-5 --effort max --permission-mode dontAsk
```

새 worktree에서 신뢰 확인 화면이 나오면 경로를 확인한 뒤 한 번만 승인한다.
Human Gate 승인과는 별개다.

### Hermes Research / Production

Hermes 프로필은 다음 위치에 분리되어 있다.

```text
/Users/mk-macbook/.hermes/profiles/ytf-research
/Users/mk-macbook/.hermes/profiles/ytf-production
```

두 프로필 모두 LM Studio의 정확한 Qwen 모델을 사용한다. 예전 Hyatt/OpenMontage
폴더를 가리키던 filesystem MCP는 제거했다. Research는 YouTube 키만,
Production은 스톡 미디어 키만 가진다.

## 로컬 메모리 충돌 방지

Qwen/Gemma와 ComfyUI·Blender·Houdini 고부하 작업은 동시에 실행하지 않는다.
상태 표지만 쓰지 않고 다음 단일 lease 파일을 원자적으로 획득한다.

```text
유튜브공장/.runtime/orca/local-heavy.lease
```

실행 예:

```bash
PYTHONPATH=. ./.venv/bin/python scripts/orca/run_with_resource_lease.py \
  --lock .runtime/orca/local-heavy.lease \
  --lane local_text \
  --owner '<run-id>-research' \
  -- hermes --profile ytf-research
```

- `local_text`와 `local_media`는 같은 lease를 사용하므로 서로 배타적이다.
- 소유자, lane, PID, 획득 시각, 만료 시각이 기록된다.
- 실행 종료 시 wrapper가 lease를 해제한다.
- 충돌 시 종료코드 75와 `RESOURCE_LANE_BUSY`로 중지한다.
- 만료 파일도 자동 삭제하지 않는다. 실제 프로세스·Orca task 상태를 확인한 뒤
  `control` 역할만 복구한다.

## Research → Verification 전달

1. Research가 shortlist JSON/Markdown을 자기 브랜치에 커밋한다.
2. handoff에 `source_commit`, 상대 경로, SHA-256을 기록한다.
3. Verification worktree를 그 정확한 커밋으로 fast-forward한다.
4. Verification은 입력 JSON을 수정하지 않고 공식·1차 출처, 범위, 날짜, 점수
   근거를 확인한다.
5. 기계 판독 검증 artifact에 `verdict`, `source_commit`, `input_sha256`,
   `verified_at`, `source_urls`, 후보별 판정을 기록한다.
6. Coordinator는 커밋과 SHA-256이 모두 같고 `PASS`일 때만 통합한다.

Markdown 보고서만 통과해도 병합하지 않는다. 검증 대상과 병합 대상의 바이트가
동일해야 한다.

## 첫 파일럿의 정지점

파일럿 프로젝트 ID는 `collapse-topic-pilot-2026-08-12`이다.

```text
topic_search         completed
  ↓
topic_verification   completed
  ↓
topic_approval       awaiting_human
                      human_approved: false
```

마지막 단계의 artifact는 `selection_status: PENDING`이며
`selected_candidate_id: null`이다. 여기서 사용자에게 후보를 보여주고 작업을
끝낸다. 사용자가 특정 후보를 명시적으로 선택하기 전에는 research, 대본,
VisualPlan, 생성, TopView, 게시 단계로 진행하지 않는다.

## 장애 복구

- 모델명·effort가 다르면 해당 terminal을 닫고 계약값으로 새로 시작한다.
- 공용 프로젝트 경로가 비어 있으면 `.env` 존재만 믿지 말고 terminal을 닫은 뒤
  위의 명시적 `export`가 포함된 명령으로 다시 시작한다.
- Research terminal이 끝났는데 lease가 남으면 먼저 terminal과 PID를 확인한다.
  살아 있으면 닫고 wrapper의 정상 해제를 기다린다.
- Research 커밋 뒤 Verification 입력 해시가 다르면 병합하지 않고 새 task로
  다시 검증한다.
- worker가 결과를 보냈으면 task 결과를 확인하고 terminal을 idle 또는 close로
  정리한다. 실패 task 기록은 삭제하지 않고 재시도 task와 함께 보존한다.
- 기존 Hyatt/OpenMontage worktree, Run, 프로젝트는 정리 대상으로 간주하지
  않는다.

## 계약 파일

- 모델·권한·Gate: `config/orca-model-routing.yaml`
- JSON Schema: `schemas/orchestration/orca-model-routing.schema.json`
- 역할 지시: `orchestration/prompts/`
- 전용 파이프라인: `pipeline_defs/youtube-factory.yaml`
- 역할 env 배치: `scripts/orca/provision_role_env.py`
- 실제 모델 사전 점검: `scripts/orca/model_preflight.py`
- 로컬 리소스 잠금: `lib/resource_lease.py`
- lease 실행 wrapper: `scripts/orca/run_with_resource_lease.py`

