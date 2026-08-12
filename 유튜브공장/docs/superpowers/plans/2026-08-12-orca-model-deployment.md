# Orca 모델 배치 구현 계획

> 실행 기준: `docs/superpowers/specs/2026-08-12-orca-model-deployment-design.md`

목표는 역할 계약을 코드로 잠그고, 새 Orca Run에서 실제 모델 handoff를
검증하는 것이다. 기존 Orca 저장소·Run·worktree는 수정하거나 삭제하지 않는다.

## Task 1 — 모델 라우팅 계약

1. `tests/contracts/test_orca_model_routing.py`에 다음 실패 테스트를 먼저 추가한다.
   - 여섯 역할과 정확한 모델·effort·실행기
   - 역할별 허용/금지 쓰기 범위
   - TopView manual-only 및 provider fallback 금지
   - Human Gate 자동 승인 금지
   - 로컬 텍스트/미디어 배타 레인
   - 역할별 secret allowlist
   - 모든 역할의 시작 위치가 `<worktree>/유튜브공장`인지
   - canonical `OPENMONTAGE_PROJECTS_DIR` 공유 계약
   - handoff commit·artifact SHA-256 exact match
   - 로컬 text/media 원자적 lease와 충돌 거부
2. `schemas/orchestration/orca-model-routing.schema.json`을 추가한다.
3. `config/orca-model-routing.yaml`을 추가한다.
4. `lib/orca_model_routing.py`에서 스키마 검증과 의미 불변식을 검사한다.
5. 새 계약 테스트와 기존 계약 테스트를 실행한다.

## Task 2 — 역할 프롬프트와 사전 점검

1. `orchestration/prompts/` 아래에 control, research, verification,
   story-visual, production, qa 프롬프트를 추가한다.
2. 각 프롬프트에 입력·출력·쓰기 소유권·금지 행동·완료 신호를 명시한다.
3. `scripts/orca/model_preflight.py` 테스트를 먼저 작성한다.
4. 사전 점검은 Codex/Claude/Hermes 인증, LM Studio 모델, Orca 연결,
   Git 상태, 역할 계약을 확인하고 비밀값은 출력하지 않는다.
5. `scripts/orca/provision_role_env.py` 테스트를 먼저 작성한다.
6. allowlist에 포함된 키만 역할별 `.env`로 복사하고 mode `0600`을 강제한다.

## Task 3 — 깨끗한 기준 커밋

1. 기존 untracked Task 2 shortlist 템플릿·테스트가 본 작업과 충돌하지 않는지
   확인하고 그대로 보존한다.
2. 설계, 계획, 역할 계약, 프롬프트, 스크립트를 의도별 커밋으로 저장한다.
3. 비밀값, `.env`, runtime cache, 기존 프로젝트 결과물이 diff에 없는지 확인한다.
4. 전체 관련 테스트를 실행한다.

## Task 4 — Orca 저장소와 역할 환경

1. `/opt/homebrew/bin/orca repo add`로 현재 `youtubefac` 저장소를 새로 등록한다.
2. Orca base ref를 새 기준 커밋으로 설정한다.
3. 새 Run `유튜브공장 모델배치 파일럿`을 생성한다.
4. 역할별 독립 worktree와 branch를 생성한다.
5. Codex coordinator/verification/qa, Claude visual-director 터미널을 실제
   해당 모델과 effort로 시작한다.
6. Hermes `ytf-research`, `ytf-production` 프로필을 기존 프로필과 분리해
   생성하고 LM Studio Qwen endpoint를 고정한다.
7. Research에는 YouTube 키만, Production에는 stock media 키만 배치한다.
8. 비밀이 아닌 `OPENMONTAGE_PROJECTS_DIR`을 모든 역할에 동일하게 배치한다.
9. 각 역할에서 `유튜브공장/` 시작 위치, 짧은 무과금 응답, 쓰기 경로와
   shared project visibility를 확인한다.

## Task 5 — 주제 검색 파일럿

1. Orca task DAG를 Research → Verification → Coordinator 순서로 생성한다.
2. Research/Qwen에 10개 이상 후보, 공식·1차 출처, 한국어 YouTube 검색면,
   임시 점수 근거를 요청한다.
3. OpenMontage project를 초기화하고 `topic_search` canonical artifact와
   checkpoint를 같은 shared projects root에 기록한다.
4. handoff에 source commit, artifact path, SHA-256을 기록하고 그 커밋에서
   Verification 입력 작업공간을 만든다.
5. Verification/Codex에 원문·점수 근거·정확한 입력 바이트의 독립 검증을 요청한다.
6. 검증 실패 항목은 Research에 한 차례 제한된 수정 작업으로 되돌린다.
7. verdict의 commit·SHA-256이 일치하는 통과 커밋만 Coordinator가 통합한다.
8. JSON에서 Markdown을 생성·대조하고 전체 주제검색 테스트를 실행한다.
9. `topic_selection`을 PENDING으로 만들고 `topic_approval` checkpoint를
   `awaiting_human`, `human_approved: false`로 기록한다.

## Task 6 — 운영·복구 문서와 완료 감사

1. `docs/operations/ORCA-MODEL-DEPLOYMENT.md`에 시작, 상태 확인, 재연결,
   모델 장애, 리소스 레인 전환, 역할 해제 절차를 기록한다.
2. Orca Run/task/worktree 상태를 읽어 모든 worker가 settled·released 또는
   의도적으로 retained인지 확인한다.
3. secret scan, Git diff, 테스트, 모델 preflight를 새로 실행한다.
4. 기존 Hyatt/OpenMontage Run과 worktree가 변하지 않았음을 확인한다.
5. 산출물 경로, 모델 배치 결과, 남은 Human Gate를 최종 보고한다.
