# 유튜브공장 모바일 대시보드 구현 계획

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task by task. Apply superpowers:test-driven-development for every behavior change and superpowers:verification-before-completion before claiming completion.

**Goal:** OpenMontage canonical project를 진실원으로 유지하면서, 허용된 Tailscale 사용자만 휴대폰 PWA에서 제작 상태를 보고 Human Gate 결정을 안전하게 기록할 수 있게 한다.

**Architecture:** 기존 Backlot의 읽기 모델은 그대로 재사용하고, 쓰기는 별도의 `mobile_actions` 계층이 제한된 action 계약만 처리한다. 모든 결정은 checkpoint SHA-256 낙관적 잠금, 파일 잠금, prepared journal, append-only receipt, idempotency index를 거치며 승인과 실제 제작 실행은 분리한다. Gateway는 loopback에만 bind하고 전용 Tailscale Serve가 tailnet HTTPS를 제공한다.

**Tech Stack:** Python 3.11, FastAPI, Pydantic, jsonschema, pytest, vanilla HTML/CSS/JavaScript PWA, Tailscale Serve.

---

## 구현 파일 지도

- `backlot/mobile_actions.py`: action 계약, gate 판정, checkpoint/artifact/receipt 트랜잭션, 복구
- `backlot/mobile_security.py`: Tailscale identity allowlist, CSRF, Origin, 요청 크기·빈도 제한
- `backlot/mobile_state.py`: 모바일 화면용 읽기 전용 projection
- `backlot/server.py`: 모바일 API/PWA route와 보호 middleware 연결
- `backlot/ui/mobile.*`: 반응형 PWA shell과 승인 UX
- `schemas/mobile-dashboard/*.schema.json`: action·receipt 영속 계약
- `config/mobile-dashboard.example.yaml`: loopback, allowlist, Tailscale 운영 기본값
- `scripts/mobile-dashboard.py`: loopback 고정 실행 진입점
- `scripts/mobile-dashboard-tailscale.sh`: Hermes와 분리된 daemon/state/socket/Serve lifecycle
- `tests/backlot/test_mobile_*.py`: 단위·API·보안·트랜잭션 검증
- `tests/contracts/test_mobile_dashboard_contract.py`: PWA·운영 경계 정적 계약

## Task 1: Action 및 receipt 계약 고정

**Files:**
- Create: `schemas/mobile-dashboard/action.schema.json`
- Create: `schemas/mobile-dashboard/approval-receipt.schema.json`
- Create: `backlot/mobile_actions.py`
- Test: `tests/backlot/test_mobile_actions.py`

- [x] 실패 테스트로 허용 action, project/stage/candidate 정규화, 임의 경로·명령·provider 필드 거부를 고정한다.
- [x] 실패 테스트로 checkpoint canonical JSON SHA-256 계산과 stale hash 409 상당 오류를 고정한다.
- [x] 최소 계약 validator와 타입을 구현해 테스트를 통과시킨다.
- [x] topic 승인은 verification verdict가 PASS이고 candidate 결과도 PASS인 ID만 허용하도록 실패·성공 fixture를 추가한다.
- [x] `approve_gate`는 `awaiting_human`이면서 manifest가 승인 대상으로 선언한 stage만 `completed/human_approved=true`로 전이하게 한다.
- [x] `reject_gate`, `request_revision`, `request_stop`은 임의 checkpoint 상태를 쓰지 않고 제한된 request artifact와 receipt만 남기게 한다.

## Task 2: Crash-safe exactly-once 승인 트랜잭션

**Files:**
- Modify: `backlot/mobile_actions.py`
- Test: `tests/backlot/test_mobile_action_transaction.py`

- [x] 먼저 동일 idempotency key의 순차·4개 동시 요청이 receipt 하나만 만드는 실패 테스트를 작성한다.
- [x] 프로젝트별 `fcntl` 잠금과 idempotency index를 구현한다.
- [x] prepared journal에 목표 파일의 상대 경로·정확한 bytes·SHA-256를 기록한 뒤 fsync+atomic rename하는 transaction writer를 구현한다.
- [x] artifact, checkpoint, history, receipt, idempotency index 각 경계의 failpoint 테스트를 작성한다.
- [x] 재시작 복구가 prepared transaction을 한 번만 roll-forward하고 부분 승인·중복 receipt를 남기지 않게 한다.
- [x] 기존 awaiting checkpoint를 deterministic history 파일에 보존하고 현재 checkpoint·standalone artifact·embedded artifact가 동일 객체인지 검증한다.

## Task 3: 인증·요청 보호 API

**Files:**
- Create: `backlot/mobile_security.py`
- Modify: `backlot/server.py`
- Test: `tests/backlot/test_mobile_security.py`
- Test: `tests/backlot/test_mobile_api.py`

- [x] identity header 없음, 정확한 login/user-id allowlist 불일치, 비-loopback 직접 접근을 거부하는 실패 테스트를 작성한다.
- [x] 로컬 운영은 loopback에서만 허용하고 Tailscale 요청은 검증된 `Tailscale-User-*` header와 exact allowlist를 요구한다.
- [x] `GET /api/mobile/session`이 세션 cookie와 CSRF token을 발급하고 POST가 cookie/token/same-origin Origin을 모두 요구하게 한다.
- [x] payload 크기, 메모 길이, action rate limit, project traversal, unknown action 거부 테스트를 추가한다.
- [x] `POST /api/mobile/project/{id}/actions`를 action service에 연결하고 409/422/429를 안정된 오류 코드로 매핑한다.
- [x] response와 log에 secret, 환경변수, 로컬 경로가 포함되지 않는지 검사한다.

## Task 4: 모바일 읽기 projection과 상태 갱신

**Files:**
- Create: `backlot/mobile_state.py`
- Modify: `backlot/server.py`
- Test: `tests/backlot/test_mobile_state.py`

- [x] 18단계 rail, 현재 Human Gate, 각 checkpoint hash, 주제 후보 12건, 비용, 역할 배치, 저장된 provider 상태를 만드는 fixture 테스트를 먼저 작성한다.
- [x] `load_board_state`와 canonical topic artifacts, `config/orca-model-routing.yaml`만 읽어 projection을 구현한다.
- [x] 데이터 누락은 카드별 `unavailable`로 표시하고 provider/model을 실시간 확인한 것처럼 추측하지 않게 한다.
- [x] 기존 SSE를 모바일 project change feed로 재사용하며 event가 action response를 대신하지 않게 한다.

## Task 5: 반응형 PWA와 Human Gate UX

**Files:**
- Create: `backlot/ui/mobile.html`
- Create: `backlot/ui/mobile.css`
- Create: `backlot/ui/mobile.js`
- Create: `backlot/ui/manifest.webmanifest`
- Create: `backlot/ui/sw.js`
- Create: `backlot/ui/icons/icon.svg`
- Modify: `backlot/server.py`
- Test: `tests/contracts/test_mobile_dashboard_contract.py`

- [x] 정적 계약 테스트로 manifest/standalone/icon, shell-only cache, API 비캐시, offline action 금지, 44px 터치 영역을 고정한다.
- [x] 승인된 시안의 stage rail, Human Gate, 주제 순위, 역할 상태, 비용/provider 카드와 8개 하위 메뉴를 구현한다.
- [x] 390px에서는 좌측 sidebar를 하단 nav로 바꾸고 gate를 첫 화면 상단에 둔다.
- [x] `budget`, `asset_selection`, `final_review`, `title_thumbnail`, `publish`는 요약 modal 다음 문구 재확인까지 POST하지 않게 한다.
- [x] 오프라인에서는 action 버튼을 비활성화하고 큐·background sync·localStorage에 승인을 저장하지 않는다.
- [x] `publish`는 승인 action만 보내며 외부 게시 endpoint나 임의 명령 호출을 포함하지 않는다.

## Task 6: 전용 Tailscale 운영 구성

**Files:**
- Create: `config/mobile-dashboard.example.yaml`
- Create: `scripts/mobile-dashboard.py`
- Create: `scripts/mobile-dashboard-tailscale.sh`
- Create: `scripts/mobile-dashboard-preflight.py`
- Create: `docs/operations/mobile-dashboard.md`
- Test: `tests/contracts/test_mobile_dashboard_operations.py`

- [x] 실행기가 host를 `127.0.0.1`로 고정하고 public bind·Funnel 문자열을 거부하는 테스트를 작성한다.
- [x] 대시보드 전용 `.runtime/mobile-dashboard/tailscale/` state/socket을 사용하고 Hermes socket/state 문자열을 참조하지 않는 lifecycle을 구현한다.
- [x] `tailscale serve --bg`만 사용하고 preflight가 `serve status --json`에서 Funnel/public 노출을 fail closed 하게 한다.
- [x] login URL, 허용 Tailscale login/user ID 설정, 휴대폰 PWA 설치, 중지·재시작·복구 방법을 비기술 사용자 문서로 작성한다.
- [x] 실제 daemon 시작은 전용 socket으로만 수행하고 사용자의 tailnet 로그인 단계에서 URL을 제시한다.

## Task 7: 회귀·시각·운영 검증

**Files:**
- Create: `reviews/mobile-dashboard-verification.md`
- Modify only if tests expose defects: files from Tasks 1–6

- [x] 새 action/security/state/API/contract 테스트를 실행하고 모두 통과시킨다.
- [x] 기존 `tests/backlot tests/contracts` 전체 회귀를 실행한다.
- [x] 테스트 프로젝트에서 topic approval을 실행해 receipt, history, checkpoint, standalone artifact의 hash와 개수를 독립 확인한다. canonical pilot은 승인하지 않는다.
- [x] 390x844와 1180x820에서 브라우저 screenshot을 만들고 overflow, overlap, text legibility, disabled/offline 상태를 눈으로 검사한다.
- [x] Gateway가 loopback에만 listen하는지 확인하고 Tailscale Serve status에서 Funnel 비활성·전용 socket 사용을 확인한다.
- [x] 검증 결과, 남은 실제 사용자 단계(Tailscale 로그인·휴대폰 접속), 정확한 접속 URL을 리뷰 문서에 기록한다.
- [x] 의도한 파일만 commit하고 feature branch를 non-force push한다. Human Gate fixture 외 실제 프로젝트 승인이나 유료 호출·게시를 실행하지 않는다.
