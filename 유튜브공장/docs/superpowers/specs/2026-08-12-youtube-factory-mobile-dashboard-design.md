# 유튜브공장 Tailscale 모바일 대시보드 설계

작성일: 2026-08-12  
상태: 화면·원격 접속 방식 사용자 승인 완료, 구현 명세  
대상 파이프라인: `youtube-factory`

## 1. 목적

기존 OpenMontage Backlot을 `유튜브공장` 운영 대시보드로 확장한다.
사용자는 Mac과 동일한 Tailscale tailnet에 속한 휴대폰에서 현재
제작 상태, 주제 후보, 자료·출처, 대본·VisualPlan, 에셋, 편집,
검수, 모델 상태를 확인하고 Human Gate를 승인·거부·수정 요청한다.

대시보드는 OpenMontage를 대체하지 않는다. 산출물·상태·승인의 진실원은
계속 `projects/<project-id>/` 아래의 canonical artifact와 checkpoint다. Orca는
승인된 다음 작업을 모델에 전달하는 조정 계층으로만 남는다.

## 2. 성공 조건

1. iPhone·Android의 홈 화면에 PWA로 설치할 수 있다.
2. 같은 Wi-Fi가 아니어도 Tailscale에 로그인된 허용 사용자는 접속한다.
3. Mac의 라우터 인바운드 포트를 열지 않고 Tailscale Serve만 사용한다.
4. 주제, 증거, 구성, 대본, Animatic, 예산, 에셋 선택, 최종 편집,
   제목·썸네일, 게시 Human Gate를 휴대폰에서 처리할 수 있다.
5. 현재 화면이 읽은 checkpoint와 승인 요청 시점의 checkpoint가 다르면
   stale approval로 거부한다.
6. 중복 터치·네트워크 재시도가 동일 승인을 두 번 기록하지 않는다.
7. 승인은 유료 호출·게시를 즉시 실행하는 명령이 아니라 다음 단계를
   허용하는 결정으로 기록된다.
8. Mac이 꺼져 있거나 dashboard service가 다운되면 휴대폰은 오프라인을
   명시하고, 승인을 저장·예약·재실행하지 않는다.
9. 기존 Backlot, OpenMontage pipeline, Hyatt 작업공간과 Hermes Tailscale 프로필을
   오염·변경하지 않는다.

## 3. 범위에서 제외하는 것

- App Store·Play Store에 등록하는 네이티브 앱
- Tailscale Funnel을 통한 공개 인터넷 노출
- OpenMontage artifact를 클라우드 DB로 복제하는 이중 진실원
- 휴대폰이 임의 쉘 명령, 임의 파일 경로, 임의 Orca 프롬프트를 전송하는 기능
- 오프라인 승인 큐와 Mac 재접속 시 자동 실행
- 사용자 확인 없는 모델·provider 변경, 유료 호출, 게시

## 4. 전체 구조

```text
휴대폰 PWA
└─ Tailscale tailnet HTTPS
   └─ 유튜브공장 전용 Tailscale Serve
      └─ 127.0.0.1에만 bind된 Dashboard Gateway
         ├─ GET  → 기존 Backlot read model
         ├─ POST → 제한된 Human Action Service
         └─ SSE  → 프로젝트 변경 알림
              ├─ OpenMontage canonical projects/
              ├─ 승인 receipt·checkpoint history
              └─ Orca 상태 adapter
```

### 4.1 격리 원칙

- Dashboard Gateway는 `127.0.0.1`에만 bind한다.
- Tailscale Serve가 tailnet HTTPS endpoint와 로컬 Gateway를 연결한다.
- 기존 Hermes 프로필의 `tailscaled.sock`, state, port, SOCKS proxy를 재사용하지
  않는다. 유튜브공장 전용 Tailscale state와 lifecycle을 사용한다.
- Tailscale Funnel은 금지하며 `serve status` 결과에 public endpoint가 있으면
  preflight를 실패한다.
- 대시보드 실행자는 다른 OpenMontage·Orca 저장소를 스캔하지 않고,
  `OPENMONTAGE_PROJECTS_DIR`로 지정된 유튜브공장 전용 root만 읽고 제한적으로 쓴다.

## 5. 구성 요소

### 5.1 Backlot Read Model

기존 `backlot/state.py`와 SSE watcher를 재사용한다. 대시보드 조회는 다음
파일에서 파생된다.

- `project.json`: 프로젝트 식별자, 제목, pipeline
- `checkpoint_<stage>.json`: 단계 상태, Human Gate, cost snapshot
- `history/`: checkpoint 변경·승인 이력
- `artifacts/*.json`: 주제, 증거, 대본, VisualPlan, 에셋, 렌더 결과
- `events.jsonl`: 작업 활동
- `renders/`, `assets/`: 미디어·썸네일

파일이 누락되거나 부분 기록이면 전체 API를 중단하지 않고 해당
카드만 `데이터 부족`으로 표시한다. 검증되지 않은 값을 추측하지 않는다.

### 5.2 Human Action Service

쓰기 기능은 기존 Backlot 조회 코드와 분리한다. 허용된 action은 다음뿐이다.

- `approve_topic`: 검증된 shortlist의 candidate ID 하나를 선택하고
  `topic_selection` + `topic_approval` checkpoint를 완료한다.
- `approve_gate`: 현재 `awaiting_human` gate를 승인한다.
- `reject_gate`: gate를 거부하고 사유를 receipt에 기록한다.
- `request_revision`: 수정 범위와 메모를 기록하고 Coordinator가 소비할
  작업 요청을 생성한다.
- `request_stop`: 현재 프로젝트에 `stop_requested`를 기록하고 다음 작업 배치를
  즉시 중단한다. 실행 중 작업의 종료가 확인되기 전에는 UI에
  `중지됨`이 아니라 `중지 요청됨`으로 표시한다.

API는 action 이름, 프로젝트 ID, 대상 stage, 사용자가 본 checkpoint SHA-256,
idempotency key, 필요한 선택값·메모만 받는다. 파일 경로, 쉘 명령, 모델명,
provider, checkpoint status를 클라이언트가 임의로 지정하지 못한다.

### 5.3 Approval Receipt

모든 action은 canonical project에 append-only receipt를 원자적으로 남긴다.

```json
{
  "version": "1.0",
  "receipt_id": "019ff4c2-6ca0-7aa0-b100-891f1935c101",
  "project_id": "collapse-topic-pilot-2026-08-12",
  "action": "approve_topic",
  "stage": "topic_approval",
  "expected_checkpoint_sha256": "35e61b9d0317332bed154021a84d23bdfd4852b6544f4b51e22784ce88ef8182",
  "resulting_checkpoint_sha256": "8c6c8c7e72d69eab796f17041540428a2d4b10a57d0a33a1f3214603c4554d4e",
  "selected_candidate_id": "hyatt-regency-walkways",
  "actor": {
    "tailscale_login": "owner@example.com",
    "tailscale_user_id": "123456789012345678"
  },
  "idempotency_key": "019ff4c2-6ca0-7aa0-b100-891f1935c102",
  "created_at": "2026-08-12T10:20:00Z"
}
```

- 승인전 receipt는 없다. artifact·checkpoint와 receipt를 하나의 journaled 트랜잭션으로
  준비한다.
- 임시 파일을 내구적으로 쓴 뒤 atomic rename하고, 프로세스 충돌을 파일 lease로
  거부한다.
- 재시도는 `idempotency_key`로 기존 receipt를 반환하며 새 checkpoint를 쓰지 않는다.
- 장애 복구는 prepared journal과 resulting hash를 확인해 완료·롤백 중 하나로
  결정하며 중복 승인을 만들지 않는다.

### 5.4 Orca Status Adapter

대시보드는 model assignment을 `config/orca-model-routing.yaml`에서 읽는다. 실행
상태는 다음 순서로 표시한다.

1. OpenMontage checkpoint의 단계 상태
2. project-bound Orca task ID의 완료·실패·실행 상태
3. 모델 preflight의 마지막 실행 결과와 시각

Orca 명령은 서버가 직접 자유형 쉘로 조합하지 않는다. 고정된 인자의
adapter를 사용하고 timeout·결과 크기를 제한하며, 장애 시 `모델 상태 확인
불가`로 표시하고 checkpoint 화면은 계속 제공한다.

## 6. 인증·권한·보안

### 6.1 Tailscale 인증

- 휴대폰과 Mac은 동일한 tailnet에 로그인한다.
- Tailscale Serve가 전달한 검증된 identity header를 사용한다.
- `config/mobile-dashboard.yaml`의 정확한 Tailscale login/user ID allowlist에 있는
  사용자만 조회·action을 허용한다. domain 전체·`Everyone`은 허용하지 않는다.
- 클라이언트가 임의로 identity header를 보내더라도 공개 네트워크에서 Gateway에
  접속할 수 없게 Gateway를 loopback으로 제한한다.
- 위협 모델은 외부 인터넷·탈취한 휴대폰·허용되지 않은 tailnet 사용자를
  포함한다. 같은 macOS 사용자 계정의 악성 로컬 프로세스는 이 대시보드만으로
  격리할 수 없으며 OS 계정·디스크 암호화·로컬 접근 제어의 범위로 둔다.

### 6.2 요청 보호

- 모든 POST는 same-origin `Origin` 확인과 CSRF token을 요구한다.
- action payload 크기, 메모 길이, 요청 빈도를 제한한다.
- 클라이언트는 현재 checkpoint의 SHA-256를 보내고 서버는 재계산해 일치할
  때만 action을 실행한다.
- 프로젝트 ID, stage, candidate ID는 정규화·allowlist·schema로 검증한다.
- 승인 결과가 아닌 비밀키, 환경변수, 모델 프롬프트, 파일시스템 경로를
  response·receipt·log에 포함하지 않는다.

### 6.3 2단계 확인

다음 gate는 모바일 UI에서 요약 확인 후 별도 최종 확인을 요구한다.

- `budget`
- `asset_selection`
- `final_review`
- `title_thumbnail`
- `publish`

최종 확인 화면은 예상 비용, provider/model, 대상 에셋·파일, 공개 범위를
표시한다. 누락된 필수 정보가 있으면 승인 버튼을 활성화하지 않는다.
`publish` 승인은 게시를 즉시 실행하지 않고, 게시를 허용하는 승인
receipt만 남긴다.

## 7. 화면 구성

사용자가 승인한 데스크톱 시안을 기준으로 한다. 휴대폰에서는 좌측
사이드바를 하단 탐색으로 접고, 가장 중요한 `현재 단계 + Human Gate`를
첫 화면 상단에 둔다.

### 7.1 제작 현황

- 프로젝트 제목·ID·마지막 동기화
- OpenMontage stage rail
- 현재 Human Gate와 승인·거부·수정 요청
- 상위 주제 후보·점수·검증 상태
- Codex·Claude·Qwen 역할별 작업 상태
- 비용, 로컬 리소스 lease, 테스트, 승인 대기 건수
- YouTube·Pexels·Pixabay·Unsplash 연결 상태와 TopView 수동 모드

### 7.2 세부 메뉴

1. `제작 현황`: 전체 관제 화면
2. `주제 후보`: 후보별 점수, 질문, 공식 출처, 검증 결과, 주제 선택
3. `자료·출처`: claim, 출처 pinpoint, 권리 상태, 사실 고정 여부
4. `대본·VisualPlan`: 대본, Sequence, Shot, 카메라, 속도 곡선, 타이포·모션 지시
5. `에셋·TopView`: 실제 자료, 생성 후보, manual handoff, manifest, 선택 Gate
6. `편집·렌더`: OpenMontage edit/compose, 미리보기, 자막·오디오·렌더 상태
7. `검수 보고서`: Claude·Codex 리뷰, FAIL/PASS, 수정 이력
8. `모델·도구`: 역할 배치, 실제 모델, preflight, 자료원 연결, lease

### 7.3 PWA

- `manifest.webmanifest`, 192/512px icon, `display: standalone`, 주제색을 제공한다.
- service worker는 app shell과 아이콘만 cache한다.
- API state, checkpoint, approval form, CSRF token, receipt, 출처 본문은 cache하지 않는다.
- 오프라인에서는 마지막 승인 버튼을 보여주지 않고 `Mac에 연결할 수
  없음`을 표시한다.

## 8. 승인 데이터 흐름

### 8.1 조회

```text
파일 변경
→ Backlot watcher
→ SSE change event
→ PWA state refetch
→ 최신 checkpoint SHA-256와 Human Gate 표시
```

### 8.2 승인

```text
사용자가 요약 열기
→ 대상·비용·영향 확인
→ 최종 확인
→ POST + CSRF + idempotency key + expected checkpoint SHA-256
→ Tailscale identity allowlist 검증
→ canonical checkpoint 재로드·재해시
→ gate·artifact 스키마·선행 단계 검증
→ journaled artifact/checkpoint/receipt 기록
→ SSE 갱신
→ Coordinator가 승인된 다음 작업 검토
```

마지막 단계는 승인과 실행의 분리다. 대시보드는 승인만 기록하며,
Coordinator는 비용, 리소스 lease, 현재 task, model availability를 다시 확인한 뒤
작업을 배치한다.

## 9. 오류·충돌 처리

| 상황 | UI 표시 | 서버 동작 |
|---|---|---|
| Mac/dashboard 오프라인 | `Mac에 연결할 수 없음` | action 저장·예약 없음 |
| Tailscale 인증 없음 | 접근 거부 | 본문 없는 401/403 |
| 허용되지 않은 사용자 | 접근 거부 | 감사 log, action 없음 |
| checkpoint 변경 | `상태가 바뀌었습니다` | 409, 최신 상태 refetch |
| 중복 요청 | 기존 결과 표시 | 기존 receipt 반환 |
| 스키마·선행 단계 실패 | 승인 불가·이유 | 422, 쓰기 없음 |
| Orca 상태 조회 실패 | 모델 현황만 `확인 불가` | checkpoint UI는 계속 제공 |
| 승인 저장 중 crash | `결과 확인 중` | journal 복구 후 단일 결과 확정 |
| stop 요청 | `중지 요청됨` | 새 task 배치 금지, 실행 task 종료 확인 |

## 10. Tailscale 운영

### 10.1 현재 상태

- Tailscale CLI `1.98.8`이 설치되어 있다.
- 일반 system service는 현재 활성 tailnet session이 없다.
- 실행 중인 `tailscaled`는 Hermes `egonari` 프로필의 독립 socket/state를
  사용하며 `NeedsLogin`이다.
- 대시보드는 이 프로필을 사용·수정·중지하지 않는다.

### 10.2 전용 연결

- 유튜브공장 전용 state directory·socket·launch lifecycle을 만든다.
- 로그인 URL이 필요한 시점에서 사용자에게 보여주고, 사용자가 직접
  tailnet 인증을 완료한다.
- 휴대폰 Tailscale app을 동일 tailnet에 로그인한다.
- Serve는 고정 HTTPS 이름으로 Gateway를 reverse proxy한다.
- launch 후 health, identity, Funnel disabled, DNS, HTTPS, 재부팅 자동 복구를 검증한다.

## 11. 테스트 전략

### 11.1 상태·UI

- 기존 Backlot API·SSE·media·thumbnail 테스트를 모두 보존한다.
- `youtube-factory` 18단계, Human Gate, 주제 후보 12건, 모델 역할, 비용,
  provider 상태를 fixture로 렌더한다.
- 390px 휴대폰과 1180px 데스크톱에서 글자 중첩·가로 오버플로우·작은
  터치 대상이 없는지 시각 검사한다.
- PWA manifest·icon·standalone·online/offline 표시를 검사한다.
- service worker가 API·receipt·checkpoint를 cache하지 않는지 검사한다.

### 11.2 인증·action

- identity header 없음, 위조, allowlist 불일치를 모두 거부한다.
- GET·SSE·media route가 파일을 쓰지 못하는지 검사한다.
- CSRF·Origin·payload 크기·rate limit·path traversal·미선언 action을 거부한다.
- stale checkpoint hash를 409로 거부하고 쓰기 없음을 확인한다.
- 같은 idempotency key를 동시에 4개 요청해 receipt/checkpoint가 하나만 생기는지
  확인한다.
- approval transaction의 파일 쓰기·rename·receipt 경계에 crash를 주입해 재시작 후
  중복·부분 승인이 없는지 확인한다.
- 주제 승인은 PASS로 검증된 shortlist candidate만 선택할 수 있다.
- 2단계 gate가 한 번의 터치로 완료되지 않는지 검사한다.
- `publish` 승인이 외부 게시 도구를 호출하지 않는지 검사한다.

### 11.3 Tailscale·운영

- Gateway가 loopback에만 bind되는지 확인한다.
- Serve status에 Funnel/public endpoint가 없는지 확인한다.
- 허용된 휴대폰에서 HTTPS 조회, SSE 갱신, 승인 요청을 실제 확인한다.
- tailnet에 없는 장치와 허용되지 않은 tailnet 사용자의 접근을 거부한다.
- Gateway, Tailscale service, Mac 재부팅 후 자동 복구를 확인한다.

## 12. 구현 단계

1. 기존 Backlot read model을 보존하며 유튜브공장 현황 화면과 PWA shell을 추가한다.
2. action schema, approval receipt, 원자적 transaction, 충돌·장애 복구를 구현한다.
3. Tailscale identity middleware, allowlist, CSRF, rate limit, stale-hash 방어를 구현한다.
4. 주제 승인 fixture로 첫 모바일 Human Gate 테스트를 실행한다.
5. 기존 Hermes Tailscale state와 분리된 전용 service를 구성하고 사용자 로그인
   시점에 중지한다.
6. 휴대폰에서 조회·승인·중복 터치·네트워크 재시도·오프라인 표시를
   실증한다.
7. 승인 receipt와 checkpoint history를 Codex가 독립 검수한 뒤 운영용 연결을
   유지한다.

## 13. 운영 경계

- 휴대폰 승인은 Human Gate 사용자 의사표시로 인정한다.
- 승인 후에도 Coordinator는 현재 커밋·artifact hash·비용·리소스·모델을
  재검사한다.
- 승인된 모델·provider가 불가능하더라도 다른 provider로 자동 변경하지 않는다.
- 에셋 선택·최종 편집·게시는 휴대폰에서도 자동 승인하지 않는다.
- 대시보드 오류는 제작 pipeline의 사실·산출물을 수정하거나 우회할 권한이
  없다.
