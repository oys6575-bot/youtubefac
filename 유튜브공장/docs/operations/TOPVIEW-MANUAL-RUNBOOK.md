# TopView 수동 운용 안내

TopView는 `유튜브공장`의 감독이나 편집기가 아니다. 승인된 숏에 필요한 이미지·영상 후보를 사람이 만드는 외부 제작실이다. OpenMontage가 작업지시서를 만들고, 사용자가 TopView를 조작하고, OpenMontage가 다운로드 결과를 검사한다.

## 한 번의 작업 흐름

```text
승인된 VisualPlan + Animatic + Budget
  ↓
OpenMontage가 TopView Job Pack 생성
  ↓
사용자가 TopView Board/Canvas/3D Shot Composer에서 수동 생성
  ↓
정확한 모델명·설정·예상/실제 크레딧·시도 횟수 기록
  ↓
정해진 파일명으로 다운로드하여 inbox에 넣기
  ↓
OpenMontage 반입 검사 → candidate 등록
  ↓
사용자가 Asset Selection Gate에서 채택 또는 재작업
```

## 1. 시작 전 확인

- `GATE_ANIMATIC`과 `GATE_BUDGET`이 OpenMontage checkpoint에서 승인됐는지 확인한다.
- 작업지시서의 내러티브 목적, 시작·종료 화면, 카메라, 길이, 화면비, 참고자료 역할을 읽는다.
- 회차별 최대 시도 수와 총 크레딧 상한을 확인한다.
- 생성 화면에 정확한 날짜·수치·인용·출처 문구가 들어가도록 요구하지 않는다.
- 인물·음성·상표·자료의 사용 권리를 확인한다.

## 2. 작업 공간 선택

| 상황 | TopView 공간 | 판단 |
|---|---|---|
| 보통의 이미지·영상 후보 생성과 비교 | **Board** | 기본값. 결과 비교, 별점, 고정, 필터가 핵심 |
| 여러 장면을 길게 탐색 | Canvas | VisualPlan을 대체하지 않고 후보 탐색에만 사용 |
| 인물·소품·카메라의 위치 연속성이 중요 | 3D Shot Composer | 준비 시간이 이득보다 클 때는 사용하지 않음 |
| 대체 스토리보드가 필요 | Film Studio / Storyboard | 승인된 내부 숏 계획 뒤에만 보조 사용 |
| 연속극·가상 캐릭터 중심 시리즈 | Drama Studio | 사실 기반 다큐의 기본 경로가 아님 |

## 3. 생성 방식 선택

| 요구 | 방식 |
|---|---|
| 참고 프레임 없음 | Text to Video |
| 승인된 이미지 한 장을 움직임 | Image to Video |
| 첫 화면과 마지막 화면을 모두 잠금 | First and Last Frame |
| 인물·공간·물체·스타일 참조가 여러 개 | Omni/Multi Reference |
| 기존 영상을 제한적으로 수정 | Video Edit |
| 동작 레퍼런스를 따라야 함 | Motion Control |
| 공간 구도를 먼저 배치해야 함 | 3D Shot Composer 후 생성 |

모델은 “가장 새 모델”이 아니라 숏의 통제가 되는 모델을 고른다. 현재 Board에 Seedance, Kling, Veo, Sora, Hailuo/MiniMax, Wan, Vidu, Runway 계열이 소개돼 있지만, 실제 화면의 제공 버전과 기능은 바뀔 수 있다. 반드시 결제 직전에 보이는 전체 모델명을 기록한다.

## 4. 제출 직전 기록

매 시도마다 아래 항목을 `operator-result.json`과 설정 캡처에 남긴다.

- TopView 프로젝트 또는 Board 식별 메모
- 화면에 표시된 정확한 모델명과 도구명
- Text/Image/First-Last/Reference 등 실제 모드
- 길이, 화면비, 해상도, 오디오 여부
- 사용한 모든 참조와 각 역할
- 프롬프트와 부정 프롬프트
- 큐 종류 또는 플랜 표시
- 제출 전 예상 크레딧
- 시도 번호
- 제출 시각과 완료 시각
- 설정 화면 캡처 파일과 SHA-256

예상 비용이 승인 상한을 넘거나 원하는 설정이 보이지 않으면 제출하지 않는다. 비슷해 보이는 모델로 몰래 바꾸지 말고 OpenMontage의 Router로 되돌린다.

## 5. 후보 비교와 다운로드

- 한 숏에 여러 후보가 있으면 Board에서 나란히 재생한다.
- 연속성, 손·얼굴·물체 변형, 카메라 궤적, 배경 흔들림, 첫·끝 프레임을 본다.
- native audio가 있으면 대사·효과음·배경음의 겹침과 저작권 위험을 함께 본다.
- 별점이나 핀은 TopView 내부 비교 표시일 뿐 최종 승인으로 간주하지 않는다.
- 작업지시서의 `expected_filename` 그대로 다운로드한다.
- 후보와 `operator-result.json`, 설정 캡처를 같은 inbox 배치 폴더에 넣는다.

## 6. OpenMontage 반입 뒤

반입기는 파일명, 숏 ID, 길이, 해상도, 화면비, 체크섬, 실제 모델과 설정 증거를 확인한다. 통과한 파일도 `candidate`일 뿐이다. 다음 사항을 만족한 후보만 Asset Selection Gate에 올린다.

- 애니매틱의 내러티브 기능을 실제로 수행한다.
- 출처가 필요한 사실을 가짜로 재현하지 않는다.
- AI 재현 공개 라벨을 나중에 얹을 여백이 있다.
- 영상·음성에 심각한 생성 결함이 없다.
- 실제 사용 크레딧이 cost log에 기록돼 있다.

선택 승인이 나기 전에는 편집 타임라인으로 자동 유입시키지 않는다.

## 중단·대체 기준

다음 중 하나면 재시도를 계속하지 않고 Router로 되돌린다.

- 승인된 시도 수 또는 크레딧 상한 도달
- 긴 대기열 또는 반복 실패로 일정 초과
- 인물·물체·공간 연속성이 두 번 이상 무너짐
- 정확한 시작·종료 구도가 필요한데 제어 불가
- 중요한 텍스트나 도표를 모델이 계속 틀림
- 권리·동의·공개 라벨 문제가 해결되지 않음

대체 순서는 보통 실제 자료 → 고정 이미지와 2.5D 모션 → HyperFrames → 로컬 LTX 파일럿이다. “TopView로 끝까지 해결”이 목표가 아니라, 승인된 숏을 가장 안정적으로 완성하는 것이 목표다.

## 금지 사항

- TopView API, MCP, 공식 생성 스킬 또는 Codex 플러그인 호출
- 자동 로그인, 자동 클릭, 자동 제출, 자동 재시도, 자동 다운로드
- 결제나 크레딧 소비의 자동 승인
- TopView 별점이나 핀을 OpenMontage 승인으로 변환
- 생성된 영상 안의 글자를 검증된 사실로 사용
- 권리 확인 없는 얼굴·음성 복제 또는 워터마크 제거

기능의 기준 장부는 [`config/topview-capabilities.yaml`](../../config/topview-capabilities.yaml), 실제 작업 규칙은 [`.agents/skills/topview-manual-handoff/SKILL.md`](../../.agents/skills/topview-manual-handoff/SKILL.md)에 있다.
