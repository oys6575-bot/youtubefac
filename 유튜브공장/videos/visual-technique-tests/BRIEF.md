---
workflow: motion-graphics
flow: automation
storyboard: no
message: "정지 이미지도 의미, 속도, 전환 설계가 있으면 다큐멘터리 장면처럼 움직일 수 있다"
destination: local-qa
aspect: 1920x1080
language: ko
audience: MK YouTube Factory operator
length: 9s
angle: visual-technique-test
narration: no
---

## Intent

유튜브공장의 MK Visual Director가 선택할 핵심 영상 문법 세 가지를 한 장면
안에서 짧게 검증한다. 정지 이미지의 깊이감, 빠름에서 느림으로 착지하는
가상 카메라, 사진의 원형 앵커가 정확한 합성 타이포로 이어지는 전환을
보여준다. 이것은 최종 채널 영상이 아니라 로컬 기술 검증본이다.

## Assets

- `assets/source.jpg` — OpenMontage 기준 저장소에 포함된 로컬 showcase 이미지의
  프로젝트-local 사본. 테스트의 첫 사진 장면에만 사용한다.

## Customizations

- 1920×1080, 30fps, 9초, 내레이션·음악·외부 생성 없음.
- `camera.variable_velocity_push`, `camera.material_macro_parallax`,
  `transition.semantic_match_cut`, `typography.exact_fact_overlay`의 표현 원리를
  한 장면의 세 단계로 검증한다.

## Notes

- TopView API, 브라우저 자동 조작, 유료 호출, 게시를 사용하지 않는다.
- 사진의 색은 바꾸지 않는다. 프레이밍과 움직임만 적용한다.
- 렌더는 사용자가 요청한 “몇 가지 테스트”의 로컬 검증 산출물이다.
