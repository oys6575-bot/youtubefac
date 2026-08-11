# 방짜유기 스타일 Acceptance Test

## Purpose

방짜유기 레퍼런스의 표면적 색감이 아니라, 촉각적 공정·coverage·리듬·오디오·hero reveal로 구성된 `HERITAGE_FORGE` 문법이 다른 제작 도구에서도 재현되는지 검증한다.

레퍼런스 영상의 프레임이나 브랜드를 복제하지 않는다.

## Test asset

- 길이: 45–75초
- 숏 수: 12–24
- 동일 장인 또는 동일 주체 1명
- 주요 도구 1개 이상
- 공정의 시작·변형·결과가 확인되는 소재
- REAL, AI_RECONSTRUCTION, GRAPHIC 중 최소 2종 사용

## Required coverage

- [ ] establishing_wide 1개 이상
- [ ] action_medium 2개 이상
- [ ] object_closeup 2개 이상
- [ ] material_macro 2개 이상
- [ ] evidence_insert 1개 이상
- [ ] hero 1개 이상
- [ ] 서로 다른 coverage role 4종 이상

## Motif and visual system

- [ ] 하나의 형상·재료 모티프가 3회 이상 반복된다.
- [ ] 반복은 같은 프레임 복제가 아니라 크기·맥락이 달라진 변주다.
- [ ] warm practical과 cool/neutral shadow가 구분된다.
- [ ] rim 또는 backlight가 피사체 분리에 기여한다.
- [ ] 같은 카메라 패턴이 3개 숏 이상 연속되지 않는다.
- [ ] 느린 숏 내부 움직임과 빠른 컷 리듬이 동시에 존재한다.

## Continuity

- [ ] artisan identity, wardrobe, tool, workpiece stage가 shot metadata에 bind된다.
- [ ] 인물의 얼굴·손가락·도구 geometry 오류가 핵심 동작을 방해하지 않는다.
- [ ] motion match 구간은 화면 진행 방향이 유지된다.
- [ ] 공정 단계가 원인 없이 되돌아가지 않는다.

## Edit and audio

- [ ] impact cut 2회 이상, sync 오차 ±2 frames 이내
- [ ] shape match 또는 motion match 1회 이상
- [ ] sound bridge 1회 이상
- [ ] 공정 ambience가 최소 한 구간 유지된다.
- [ ] 음악이 타격 transient와 핵심 내레이션을 가리지 않는다.
- [ ] 마지막 hero reveal은 앞선 공정 또는 증거의 payoff다.

## Typography and disclosure

- [ ] 읽어야 하는 글자는 HyperFrames overlay다.
- [ ] generated plate에 가짜 글자·워터마크가 없다.
- [ ] AI 재현은 disclosure label을 갖는다.
- [ ] source label은 실제 자료와 함께 표시된다.
- [ ] opening의 제목 또는 핵심 모티프가 ending에서 회수된다.

## Scoring

| 영역 | 배점 |
|---|---:|
| Coverage | 20 |
| Motif and lighting | 20 |
| Continuity | 20 |
| Edit and audio | 20 |
| Typography and disclosure | 20 |

합격 조건:

- 총점 85점 이상
- 각 영역 15점 이상
- blocker 0개
- Claude와 Codex 중 한 명 이상이 독립적으로 프레임 단위 검수
- 사용자 Human Gate는 별도이며 자동 합격하지 않음

## Blockers

- 공정 또는 도구가 사실과 다르지만 재현 표시가 없음
- 생성 텍스트를 최종 제목·수치로 사용
- 장인 identity 또는 핵심 도구가 숏 사이에서 명백히 바뀜
- 실제 자료의 출처·권리 기록 없음
- audio sync를 실제 재생 없이 타임라인 값만으로 합격 처리
- 영상 파일의 decode와 대표 프레임을 확인하지 않음

## Failure diagnosis

| Failure | First repair |
|---|---|
| identity drift | 얼굴 대신 손/도구 cutaway, reference 강화, 클립 단축 |
| tool geometry drift | 실제 macro insert 또는 still+2.5D |
| plastic-looking metal | image master의 texture와 highlight 수정 |
| slow and monotonous | impact chain과 coverage size 변화 추가 |
| transition overload | cut, impact, shape/motion match만 남김 |
| unreadable title | plate에서 제거하고 HyperFrames 재합성 |
| weak hero reveal | sequence purpose와 evidence payoff 재설계 |

## Review record

| Reviewer | Score | Blockers | Result | Commit |
|---|---:|---:|---|---|
| Claude | — | — | pending | — |
| Codex | — | — | pending | — |
