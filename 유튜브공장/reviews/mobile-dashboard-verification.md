# 유튜브공장 모바일 승인 대시보드 검증

- 검증일: 2026-08-12
- 검증 범위: Human Gate 명세 승인, 모바일 PWA, Tailscale Serve 비공개 운영
- 판정: **PASS**

## 1. 기능·회귀 검증

- Python 전체 테스트: **1,138 passed, 10 skipped, 1 subtest passed, 0 failed**
- JavaScript syntax: `mobile.js`, `sw.js` **PASS**
- Python compile, JSON/YAML parse, `git diff --check`: **PASS**
- 기존 Backlot·contract 회귀를 포함해 실패 없음

## 2. 승인 정합성

- 동일 idempotency key의 순차 요청과 4개 동시 요청은 receipt 1건만 생성: **PASS**
- prepared journal 후 artifact, checkpoint, history, receipt, idempotency index 각 경계에서 강제 장애를 발생시켜도 재시작 복구가 정확히 1회만 수렴: **PASS**
- checkpoint 원본 bytes SHA-256가 바뀌 stale 승인 거부: **PASS**
- verification PASS 후보만 주제 승인 가능: **PASS**
- 고위험 gate는 `CONFIRM` 재확인 없이 전송 불가: **PASS**
- 승인은 제작·결제·게시를 직접 실행하지 않음: **PASS**

## 3. 안전·접근 검증

- Gateway listener: `127.0.0.1:8787` 단일 bind **PASS**
- 직접 loopback 모바일 session 요청은 Tailscale identity 없이 401 거부: **PASS**
- Tailscale backend: 대시보드 전용 socket에서 `Running` **PASS**
- Serve: tailnet 전용 HTTPS 443 -> `http://127.0.0.1:8787` **PASS**
- Funnel/public handler: 없음 **PASS**
- preflight: loopback listener, health, backend, private Serve 모두 **PASS**
- 기존 Hermes Tailscale state/socket/process 참조·변경 없음

## 4. 화면 검증

- 390x844: 가로 overflow 0, 가려진 작은 버튼 0, 하단 navigation 표시, Human Gate 상단 배치 **PASS**
- 1180x820: 가로 overflow 0, 가려진 작은 버튼 0, sidebar 표시, 하단 navigation 숨김 **PASS**
- PWA service worker는 shell만 cache하고 API·checkpoint·receipt를 cache하지 않음 **PASS**
- 오프라인 action queue, background sync, localStorage 승인 없음 **PASS**

## 5. 실제 프로젝트 보존

- 트랜잭션 테스트는 전용 fixture에서만 수행함.
- canonical pilot `collapse-topic-pilot-2026-08-12` topic approval은 계속 `awaiting_human`.
- canonical topic approval checkpoint SHA-256은 `35e61b9d0317332bed154021a84d23bdfd4852b6544f4b51e22784ce88ef8182`로 유지됨.
- Human Gate 승인, 유료 호출, 게시 실행을 하지 않음.

## 6. 휴대폰 접속

- 접속 URL: `https://youtube-factory.tail6d04f2.ts.net/mobile`
- 허용 신원: 동일 tailnet의 등록된 사용자 1명
- 사용자가 휴대폰 Tailscale을 켜고 URL을 열어 최종 단말 화면만 확인하면 된다.
