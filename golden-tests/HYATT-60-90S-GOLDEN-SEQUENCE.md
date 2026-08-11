# Hyatt 60–90s Golden Sequence

## Purpose

실제 자료에서 AI 재현으로 이동하고, 다시 실제 공학 자료로 돌아오는 전체 계약을 60–90초 안에서 검증한다.

**이 문서는 synthetic contract fixture다** (final-consensus, CDX-006). 여기 담긴 사건·수치·구간은 계약 형태를 검증하기 위한 자리표시자이며 사실 확정본이 아니다. 실제 제작 전에는 대상 사건과 공학 주장을 Source Registry에서 별도로 잠가야 하고, `GATE_EVIDENCE_LOCK` 승인 없이는 어떤 유료 생성 단계도 시작할 수 없다.

## Preconditions

- `GATE_SCRIPT`: approved
- `GATE_EVIDENCE_LOCK`: approved
- 사용 사진·도면의 권리 상태: verified 또는 permission_required 처리 완료
- 정확한 날짜·수치·구조 명칭: claim_id 연결
- 유료 생성 전 `GATE_BUDGET`: approved

## Target timeline

목표 길이: 74초, 허용 범위 60–90초.

| 구간 | 길이 | Representation | 핵심 동작 | 검증 포인트 |
|---|---:|---|---|---|
| 1. 실제 호텔 사진 | 0–7초 | REAL | 정지 프레임과 미세 push | 출처와 권리 |
| 2. 날짜 타이포 | 7–13초 | HYBRID | 날짜·장소 등장 | claim_id, 정확한 글자 |
| 3. walkway callout | 13–20초 | HYBRID | underline/callout | 실제 구조 위치와 일치 |
| 4. locked push | 20–27초 | REAL | 기준점까지 동일 방향 push | 다음 숏 match anchor |
| 5. AI 재현 match | 27–38초 | AI_RECONSTRUCTION | 같은 구도에서 짧은 움직임 | 공개 라벨, 구조 왜곡 없음 |
| 6. freeze to explain | 38–46초 | HYBRID | freeze, dim, 대상 분리 | clean plate 재사용 |
| 7. load diagram | 46–56초 | GRAPHIC | 행어 로드/하중 설명 | 수치·화살표는 overlay |
| 8. 실제 도면 | 56–64초 | REAL | 도면 원본과 source label | 읽기 가능, 오인 없음 |
| 9. return | 64–70초 | AI_RECONSTRUCTION | 재현으로 복귀, rack focus | 방향·색·identity 연속성 |
| 10. consequence/hold | 70–74초 | HYBRID | 최종 문장과 hold | 내레이션 종료 여유 |

## Required artifacts

- `sources.json`과 `claims.json`
- schema-valid `visual-plan.json`
- source photo와 drawing checksum
- AI keyframe image master
- generated clean plate
- HyperFrames overlay의 독립 렌더
- temp narration, BGM, SFX
- `animatic.mp4`
- `review-build.mp4`
- `qc-report.json`
- 모든 Human Gate checkpoint

## Pass/fail criteria

### Contract

- [ ] `visual-plan.json`이 `schemas/visual-plan.v2.schema.json`을 통과한다.
- [ ] 화면에 표시되는 모든 정확한 텍스트·수치는 typed `overlay.items[]`에 있고 claim_id에 바인딩된다 (CLD-002).
- [ ] 모든 sequence_id, shot_id, source_id, claim_id가 유일하다.
- [ ] 모든 claim citation에 page·figure·section·timestamp 중 적용 가능한 pinpoint가 있다.
- [ ] high/exact factual shot에는 evidence_id가 하나 이상 있다.
- [ ] 승인되지 않은 gate를 자동으로 `approved`로 기록하지 않는다.

### Evidence and ethics

- [ ] REAL과 AI_RECONSTRUCTION의 경계를 보통 시청자가 이해할 수 있다.
- [ ] 모든 표시 날짜·수치·구조 명칭이 claim_id에 연결된다.
- [ ] 실제 도면과 사진의 출처·권리·local checksum이 기록된다.
- [ ] 재현 장면은 생성 사실을 숨기지 않는다.

### Visual continuity

- [ ] 4→5 전환에서 지정 anchor의 위치 오차가 프레임 너비의 3% 이하다.
- [ ] 카메라 진행 방향이 유지된다.
- [ ] 5와 9에서 주요 구조·공간·조명 family가 일치한다.
- [ ] AI 숏에 읽히는 가짜 글자, 로고, 워터마크가 없다.

### Graphics

- [ ] 날짜·수치·화살표는 clean plate와 분리되어 있다.
- [ ] overlay만 수정해 clean plate 재생성 없이 재렌더할 수 있다.
- [ ] title/action safe area를 침범하지 않는다.
- [ ] source label과 reconstruction label이 목표 해상도에서 읽힌다.

### Edit and audio

- [ ] 목표 길이가 60–90초다.
- [ ] 내레이션 문장과 화면의 근거가 충돌하지 않는다.
- [ ] 이벤트 기반 컷은 목표 transient 또는 clause에서 ±2 frames 이내다.
- [ ] 마지막 문장 뒤 최소 12 frames의 시각적 hold가 있다.
- [ ] 음성 clipping이 없고 BGM이 핵심 내레이션을 가리지 않는다.

### Media verification

- [ ] review build가 실제로 decode된다.
- [ ] 해상도, fps, 길이, 오디오 stream을 검사했다.
- [ ] 시작·중간·끝 및 모든 전환의 대표 프레임을 육안 검수했다.
- [ ] 검은 프레임, 의도치 않은 freeze, 손상 파일이 없다.

## Measurement procedures

정량 기준의 측정 절차 (final-consensus, CLD-008). 편집 타이밍의 측정 기준은 VisualPlan이 아니라 실제 `edit_decisions`다 (CLD-007).

### Anchor 3% 검사 (4→5 전환)

1. 두 숏의 `match_anchors[]`에 같은 `name`의 anchor가 정규화 좌표(`x_pct`, `y_pct`)로 기록되어 있어야 한다.
2. review build에서 컷 직전 프레임과 직후 프레임을 추출한다: `ffmpeg -ss <cut_time> -i review-build.mp4 -frames:v 1 ...`
3. 추출 프레임에서 anchor 대상의 실제 위치를 측정하고, 두 프레임 간 오차를 계산한다: `error = |x_after − x_before| / frame_width` (y 동일).
4. 오차가 3% 이하면 통과. 측정 프레임 2장과 측정값을 `qc-report.json`에 기록한다.

### ±2 frames 검사 (이벤트 기반 컷)

1. beat map artifact의 대상 이벤트(`event_id`, `time_seconds`)를 기준으로 한다.
2. 오디오 transient는 파형에서 onset을 검출하고, 내레이션 clause는 강제 정렬 또는 수동 마킹으로 시각을 확정한다.
3. `edit_decisions`의 해당 컷 시각과 이벤트 시각의 차를 프레임으로 환산한다: `|cut_time − event_time| × fps ≤ 2`.
4. 검사한 모든 이벤트의 목표 시각·실제 시각·오차 프레임을 `qc-report.json`에 기록한다.

### 주관 기준의 판정 규약

"REAL과 AI_RECONSTRUCTION의 경계를 보통 시청자가 이해할 수 있다"는 계측이 아니라 판정 항목이다. 두 리뷰어(Claude·Codex)가 독립적으로 판정하고, 불일치하면 사용자가 최종 판정한다. 판정 근거 문장을 review record에 남긴다.

## Blockers

다음 하나라도 존재하면 Golden Test는 실패다.

- 근거 없는 공학 주장을 화면이 사실처럼 단정
- 실제 자료를 AI 재현으로 바꾸면서 표기 없음
- 생성 영상 안에 날짜·수치·구조 명칭이 구워짐
- Human Gate가 사람 승인 없이 approved
- 결과 URL만 있고 로컬 파일·checksum 없음
- 화면 검수 없이 렌더 성공만으로 완료 선언

## Review record

| Reviewer | Independent result | Cross-review result | Date | Commit |
|---|---|---|---|---|
| Claude | pending | pending | — | — |
| Codex | pending | pending | — | — |
