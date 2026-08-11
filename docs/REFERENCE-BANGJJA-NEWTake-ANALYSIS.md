# 방짜유기 레퍼런스와 Newtake 분석

- 분석 대상: [YouTube 영상](https://www.youtube.com/watch?v=APJcwbxWtfY)
- 집중 구간: 약 00:05–01:31
- 검토 기준일: 2026-08-11
- 용도: 결과물 복제가 아니라 재사용 가능한 촬영·편집 문법 추출

## 1. 관찰 범위와 한계

초반 방짜유기 구간은 약 86초, 약 21개 장면으로 구성된 짧은 브랜드 필름에 가깝다. 공개 영상으로 확인되는 최종 결과와 공개된 제작 설명을 분석했으며, 각 숏의 원본 프롬프트·모델·시드·생성 횟수는 공개되지 않았다.

따라서 다음을 구분한다.

- 직접 관찰: 화면, 컷 순서, 색, 카메라 인상, 제목, 음향 배치
- 제작자 공개 설명: Newtake 활용, Premiere 최종 편집, Photoshop 제목 제작
- 추론: 특정 컷을 어느 모델이 생성했는지, 정확한 후보 수와 실패율

추론은 제품 성능의 확정 근거로 사용하지 않는다.

## 2. 영상 문법

### 반복 모티프

원형의 유기, 금속 표면, 망치 자국, 불꽃과 반사광을 반복한다. 서로 다른 크기의 숏 사이에서도 동일한 형상과 물성이 이어져 짧은 시간 안에 하나의 세계로 인식된다.

### 촬영 coverage

- 작업 공간을 읽게 하는 wide
- 장인과 공정 관계를 보여주는 medium
- 손, 망치, 표면을 강조하는 close-up
- 금속 질감과 불꽃을 추상화하는 macro
- 완성품의 형태와 광택을 보여주는 hero shot

한 생성 클립에 전체 공정을 맡기지 않고 짧은 coverage를 조립하는 방식이 핵심이다.

### 조명과 색

- 불과 금속은 amber/gold 계열 practical light
- 주변은 teal/blue-black 계열 shadow
- rim/back light로 손과 금속 가장자리를 분리
- 얕은 심도와 국부 하이라이트로 생성 영상의 배경 오류를 덜 드러냄

### 카메라와 편집

숏 내부 움직임은 느리고 제한적이지만 컷 전환은 빠르다. 다음 규칙이 반복된다.

- 망치 타격과 컷을 맞추는 cut-on-impact
- 원형 유기와 다른 원형 디테일을 잇는 shape match
- 손이나 도구의 방향을 다음 숏으로 잇는 motion match
- 타격음이나 불 소리를 다음 숏까지 이어 붙이는 sound bridge
- wide → medium → close → macro → hero의 크기 변화
- 시작의 제목 또는 모티프를 끝에서 회수하는 title recall

### 타이포

제목은 생성 영상 안에 포함된 것으로 보지 않는다. 제작자 설명상 Photoshop과 Premiere를 사용했으므로, 정확한 타이포는 별도 합성 단계로 취급하는 것이 안전하다.

## 3. Newtake가 기여한 것으로 공개된 범위

Newtake 공개 페이지에서 확인되는 제작 개념은 다음과 같다.

- 대본에서 스토리보드로 이어지는 노드형 흐름
- 캐릭터·장소·소품 시트
- 디렉터 콘솔과 3D blocking
- 멀티앵글 또는 9분할 후보 탐색
- 조명 프리셋과 파노라마형 공간 탐색
- 이미지에서 영상으로 이어지는 제작 흐름

이 UX는 수동으로 연출 후보를 빠르게 비교하는 데 강점이 있다. 다만 최종 영상 전체가 Newtake 안에서 자동 완성되었다는 근거는 없으며, 공개 설명상 최종 편집과 제목은 외부 도구에서 마무리됐다.

## 4. MK Visual Director에 채택할 요소

| 레퍼런스 요소 | 시스템 규칙 | 담당 |
|---|---|---|
| 반복되는 원형·금속 모티프 | `motif_bindings`로 Sequence 전체에 고정 | Visual Director |
| wide–macro 교차 | coverage 누락 검사 | VisualPlan validator |
| warm/cool 대비 | 조명 family와 색 family 분리 기록 | Visual Grammar |
| 짧은 생성 숏 | 한 클립보다 coverage 조립 우선 | Production Router |
| impact cut | 오디오 transient ±2 frames 검사 | OpenMontage |
| 정확한 제목 | clean plate와 overlay 분리 | HyperFrames |
| 3D blocking | 공간이 복잡한 숏에만 선택 사용 | TopView Canvas/3D |
| 후보 비교 | 승인 전 contact sheet와 animatic 생성 | Producer |
| 최종 hero reveal | Sequence exit 조건으로 정의 | Visual Director |

## 5. 채택하지 않을 해석

- 모든 숏을 AI 영상으로 생성하지 않는다.
- 금속 공예 스타일을 모든 주제의 채널 스타일로 일반화하지 않는다.
- 느린 카메라 움직임만으로 영화적이라고 판정하지 않는다.
- 생성 결과 안의 글자나 수치를 최종 정보로 사용하지 않는다.
- 단일 레퍼런스를 provider의 품질·속도·비용 보증으로 사용하지 않는다.
- Newtake UI 자동화를 공식 API 대체물로 사용하지 않는다.

## 6. 최종 반영

방짜유기 영상에서 추출한 재사용 문법은 [`HERITAGE_FORGE.yaml`](../config/visual-grammars/HERITAGE_FORGE.yaml)로 구조화한다. 재현 여부는 [`BANGJJA-STYLE-ACCEPTANCE-TEST.md`](../golden-tests/BANGJJA-STYLE-ACCEPTANCE-TEST.md)로 판정한다.

Newtake는 연출 UX와 레퍼런스 학습 대상으로 남기고, 자동화 가능한 주력 생성 provider는 [ADR-001](ADR-001-TOPVIEW-PRIMARY-PROVIDER.md)에 따라 TopView로 둔다.

## 7. Sources

- https://www.youtube.com/watch?v=APJcwbxWtfY
- https://www.newtake.com/ko
- https://www.newtake.com/ko/statement/terms-of-service
- https://www.newtake.com/ko/statement/privacy-policy
