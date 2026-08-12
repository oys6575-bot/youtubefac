---
card_id: research.cinematic.direction_map
type: research-synthesis
title: 시네마틱 연출 연구 지도
status: REFERENCE_ONLY
activation_status: REFERENCE_ONLY
copyright_mode: paraphrase_only
retrieved_at: "2026-08-12"
domain: direction_map
source_ids:
  - source.cinedance_mirror
  - source.acting_mirror
  - source.lira_mirror
coverage_ids: []
keywords:
  - 시네마틱 연출
  - Visual Director
  - 연구 지도
  - 온디맨드 지식
---

# 시네마틱 연출 연구 지도

이 폴더는 외부 스킬을 실행하거나 복제하는 장소가 아니다. 세 자료에서 발견한 유용한 사고 원리를 MK Visual Director, VisualPlan, TopView 수동 전달, OpenMontage 검수에 맞게 다시 작성한 프로젝트 연구층이다.

## 세 개의 연구 축

### 화면이 어디서 어떻게 움직이는가

[[10-RESEARCH/cinematic-direction/Camera-Spatial-Physics-Direction]]

- 현재 숏 문맥 격리
- 첫 프레임과 공간 블로킹
- 시선·몸 방향·랜드마크
- 보이는 광학 결과와 카메라 운용
- 시간 비트와 물리 인과
- 조명 우선순위
- 레퍼런스 역할과 출력 전 점검

### 인물이 왜 그렇게 행동하는가

[[10-RESEARCH/cinematic-direction/Behavioral-Performance-Direction]]

- 목적·장애물·전술·비트·서브텍스트
- 시선, 호흡, 생각 뒤 말하기, 반응
- 신체 작업과 행동 중단
- 거리와 지위 변화
- 반복 인물 프로필과 장면별 적응
- 앙상블과 실패 진단

### 어떤 이미지를 기준 자산으로 만들 것인가

[[10-RESEARCH/cinematic-direction/Image-Reference-Asset-Direction]]

- 이미지 목적과 작업 종류 분해
- 모호성·드리프트·문자 오류 진단
- 조명·재질·팔레트의 관찰 가능한 통제
- 정체성 기준과 역할별 레퍼런스
- 최소 변경·최대 보존 방식의 부분 수정
- 반대 각도와 상태 변형 자산
- 공급자 기능 주장에 대한 검증 경계

## 실제 제작으로 내려가는 경로

```text
연구 노트(REFERENCE_ONLY, 필요할 때만 열람)
  ↓ 원리 추출
Visual Technique Registry(짧은 선택 가능 지시)
  ↓ 숏당 1~4개, 시퀀스당 3~7개 선택
MK Visual Director
  ↓
VisualPlan.cinematic_direction
  ├─ opening_frame
  ├─ spatial_blocking
  ├─ optical_result
  ├─ timed_beats
  ├─ physical_cues
  ├─ performance (인물 연기가 필요할 때만)
  └─ reference_bindings
  ↓
Animatic·사실·예산 Human Gate
  ↓
Production Router
  ├─ 실제 자료 반입
  ├─ TopView 수동 전달
  ├─ 로컬 LTX 생성
  └─ HyperFrames 그래픽·합성
  ↓
Asset Selection Human Gate
  ↓
OpenMontage 편집·합성·QC·납품 상태
```

## 지식 과밀 방지 규칙

1. 검색은 연구 노트를 포함한 전체 지식에서 수행한다.
2. 정상 제작의 `load_order`에는 이 폴더를 자동 포함하지 않는다.
3. 레지스트리의 짧은 기술 카드가 기본 실행 지식이다.
4. 어려운 숏, 실패 분석, 새 원리 등록, 연구 유지보수 때만 관련 연구 절을 연다.
5. 연구 노트에서 가져온 원리는 공급자 중립 언어로 다시 써야 한다.
6. 특정 서비스의 모델명·기능·한도는 현재 공식 화면에서 재검증한다.
7. 연구 노트는 Human Gate를 승인하거나 유료 호출을 시작할 수 없다.

## 여섯 가지 실행 원리 연결

| 레지스트리 기술 | 주 연구 노트 | VisualPlan 위치 |
|---|---|---|
| `direction.opening_frame_intent` | 카메라·공간·물리 | `opening_frame` |
| `continuity.explicit_spatial_blocking` | 카메라·공간·물리 | `spatial_blocking` |
| `direction.behavioral_performance_beats` | 행동 기반 연기 | `performance`, `timed_beats` |
| `camera.observable_optical_result` | 카메라·공간·물리 | `optical_result` |
| `direction.physical_causality` | 카메라·공간·물리 | `physical_cues`, `timed_beats` |
| `continuity.reference_role_binding` | 이미지·레퍼런스·에셋 | `reference_bindings` |

## 저작권·출처·검증 상태

- 세 원자료는 2026-08-12에 제3자 미러에서 연구용으로 확인했고 SHA-256은 `config/cinematic-direction-coverage.yaml`에 기록했다.
- 외부 Markdown 전체를 프로젝트에 저장하지 않는다.
- 원문 문장, 프롬프트 블록, 예시, 페르소나는 복제하지 않는다.
- 이 폴더의 본문은 프로젝트가 새로 작성한 한국어 해설이다.
- 공식 출처가 아니므로 제품 기능과 라이선스의 최종 근거로 사용하지 않는다.
- 향후 공식 자료나 실제 파일럿이 모순을 발견하면 레지스트리 변경 제안을 만들고 검토 후 반영한다.
