# 휴대폰용 유튜브공장 운영 안내

## 무엇이 열리는가

휴대폰에서는 OpenMontage가 기록한 제작 현황과 Human Gate만 봅니다. 승인은
다음 단계 진행을 허용하는 receipt를 남길 뿐이며 유료 생성이나 YouTube 게시를
즉시 실행하지 않습니다. 외부 인터넷 공개 기능은 사용하지 않습니다.

## 최초 1회 설정

1. `config/mobile-dashboard.example.yaml`을 `config/mobile-dashboard.yaml`로 복사합니다.
2. Mac의 전용 Tailscale 로그인이 끝난 뒤 표시되는 `DNSName`을
   `canonical_origin`에 `https://`와 함께 적습니다.
3. 같은 상태 화면의 사용자 login을 `allowed_users.login`에 정확히 적고,
   `user_id`에는 그 사용자를 구별할 고정 문자열을 적습니다.
4. `.venv/bin/python scripts/mobile-dashboard.py`로 Gateway를 시작합니다.
5. `scripts/mobile-dashboard-tailscale.sh login`을 실행하고 표시된 로그인 URL을
   사용자가 직접 승인합니다.
6. `scripts/mobile-dashboard-tailscale.sh serve`로 tailnet 전용 HTTPS를 연결합니다.
7. `scripts/mobile-dashboard-preflight.py`가 PASS인지 확인합니다.

Hermes가 사용하는 Tailscale daemon, socket, state, SOCKS 포트는 이 과정에서
읽거나 변경하거나 중지하지 않습니다.
macOS의 Unix socket 길이 제한 때문에 전용 socket만 짧은
`/tmp/ytf-mobile-<사용자번호>/tailscaled.sock`에 두고, 영속 state와 로그는 계속
유튜브공장 `.runtime/mobile-dashboard/tailscale/`에 둡니다.

## 휴대폰에서 설치하고 승인하기

1. iPhone 또는 Android에 Tailscale 앱을 설치하고 Mac과 같은 tailnet에 로그인합니다.
2. Safari/Chrome에서 `canonical_origin/mobile`을 엽니다.
3. iPhone은 공유 메뉴의 `홈 화면에 추가`, Android는 브라우저 메뉴의
   `앱 설치`를 누릅니다.
4. 주제 후보를 누르고 Human Gate 카드에서 승인 또는 수정 요청을 선택합니다.
5. 예산, 에셋 선택, 최종 영상, 제목·썸네일, 게시 단계는 요약을 본 뒤
   `CONFIRM`을 입력해야 합니다.

Mac 또는 Tailscale 연결이 끊기면 승인 버튼이 꺼집니다. 오프라인 결정을 저장해
나중에 자동 실행하는 기능은 없습니다.

## 재부팅 후 자동 시작

설정과 최초 로그인이 검증된 뒤 다음 명령으로 두 개의 독립 사용자 서비스를
설치합니다.

```text
.venv/bin/python scripts/install-mobile-dashboard-services.py --install
```

- `com.mk.youtube-factory.dashboard`: 127.0.0.1 Gateway
- `com.mk.youtube-factory.tailscale`: 유튜브공장 전용 Tailscale daemon

삭제는 `--remove`, 실제 설치 전 확인은 `--dry-run`을 사용합니다. Serve 설정은
전용 Tailscale state에 보존되므로 daemon이 다시 뜨면 같은 private endpoint를
복구합니다.

## 고장 확인

- 화면에 `Mac에 연결할 수 없음`: Mac 전원, 두 서비스, 휴대폰 Tailscale을 확인합니다.
- `접근 거부`: 휴대폰 계정의 exact login과 allowlist가 다른 상태입니다.
- `상태가 바뀌었습니다`: 다른 작업이 checkpoint를 갱신했습니다. 새 화면을 보고 다시 결정합니다.
- 사전 점검 실패: 공개 노출 또는 loopback 이외의 proxy가 감지된 것이므로 Serve를
  재설정하기 전까지 사용하지 않습니다.
