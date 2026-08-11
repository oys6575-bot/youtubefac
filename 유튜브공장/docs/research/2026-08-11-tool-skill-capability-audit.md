# 유튜브공장 도구·스킬·TopView·로컬 모델 전수 검수

**기준일:** 2026-08-11

**범위:** OpenMontage, MK Visual Director, TopView, HyperFrames, Remotion, FFmpeg, yt-dlp, ComfyUI, Hugging Face 로컬 모델, 프로젝트 내 도구 104개와 스킬 107개
**결론:** 구조는 유지한다. OpenMontage를 최상위 총괄 감독과 진실원으로 두고, TopView는 수동 생성실, HyperFrames는 정확한 그래픽실, Remotion은 프로그램식 편집·합성 런타임, ComfyUI는 로컬 파일럿 경로로 쓴다.

## 1. 최종 채택 구조

~~~text
사용자 — 최종 승인권자
  ↓
OpenMontage — 총괄 감독 / 단계·상태·비용·승인·산출물의 진실원
  ├─ Evidence Director — 조사·출처·권리
  ├─ Script Director — 대본·주장 연결
  ├─ MK Visual Director — Visual Grammar·Sequence·Shot·전환·타이포 설계
  ├─ Animatic Director — 저비용 사전 검토본
  ├─ Production Router — 승인된 숏의 제작 경로 계획·실행
  │   ├─ REAL_INGEST — 실제 사진·영상·문서
  │   ├─ TOPVIEW_HANDOFF — 사용자 수동 TopView
  │   ├─ LOCAL_LTX — ComfyUI·로컬 생성
  │   └─ HYPERFRAMES — 정확한 타이포·수치·도표·모션그래픽
  ├─ Asset Director — 후보 반입·비교·선택 Gate
  ├─ Edit/Compose Director — Remotion·HyperFrames·FFmpeg 조립
  └─ QC/Publish Director — 실제 렌더 검수·납품·게시 Gate
~~~

OpenMontage를 최상위에 두는 편이 효율적인 이유는 모든 하위 도구가 서로 다른 상태와 결과 형식을 가지기 때문이다. 총괄 계층이 없으면 TopView 후보, 로컬 생성물, 실제 자료, 그래픽이 승인 여부와 출처를 잃은 채 타임라인에 섞인다. 반대로 OpenMontage가 전체 checkpoint와 manifest를 관리하면, MK Visual Director가 연출에 집중하고 실행 도구는 교체 가능해진다.

## 2. 근거 등급

1. **공식 문서·공식 저장소·고정 커밋:** 기능, 버전, 라이선스, 스키마 판단의 기준
2. **공식 GitHub 이슈:** 현재 재현되거나 보고된 기술 위험
3. **Hugging Face 고정 리비전:** 모델 파일과 라이선스의 재현 기준
4. **Reddit 실사용 글:** 속도, 대기열, 비용 체감, 실패 양상의 보조 신호

Reddit 글은 사실 확정 자료로 쓰지 않았다. 반복 시험의 크기와 중단 기준을 정하는 위험 신호로만 반영했다.

## 3. 핵심 도구 업데이트와 판정

| 구성 | 고정 기준 | 이번 조치 | 공장 역할 | 판정 |
|---|---|---|---|---|
| OpenMontage | 4eab34c5… | 공식 tracked tree를 독립 저장소로 이관 | 최상위 control plane | 필수 |
| HyperFrames | 0.7.106, 896bc336… | 최신 스킬 14종을 프로젝트 안에 고정 | 타이포·수치·도표·모션그래픽 | 필수 |
| Remotion | 4.0.508 | 전체 패키지 버전 정렬, 공식 스킬 12종 갱신 | React 장면·캡션·최종 조립 | 필수 |
| FFmpeg | 8.1.2 | 현재 실행 버전 기록 | probe·변환·mux·단순 편집 | 필수 |
| yt-dlp | 2026.07.04 | 현재 실행 버전 기록 | 참조 영상·허용 소스 반입 | 필수 |
| ComfyUI | stable v0.31.0, 43cb4ffc… | 소스 1,006개 파일을 독립 vendor에 고정 | 로컬 그래프 실행 | 선택 설치·중요 |
| LTX/Wan/FLUX | HF exact revision | 가중치 대신 리비전·라이선스·경로만 고정 | 로컬 파일럿 | 승인 후 다운로드 |
| TopView | live web UI | API 없이 기능 카탈로그와 수동 계약만 추가 | 외부 후보 제작실 | 수동 경로 |

정확한 값은 [config/toolchain-lock.json](../../config/toolchain-lock.json)에 있다. Remotion은 [공식 라이선스](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)상 개인, 비영리, 직원 3명 이하 영리 조직 등에 무료 사용 자격이 있고 그 밖의 영리 조직에는 회사 라이선스가 필요하므로, 운영 주체가 커지면 재확인해야 한다.

### HyperFrames

[v0.7.106 공식 릴리스](https://github.com/heygen-com/hyperframes/releases/tag/v0.7.106)를 고정했다. 검증된 날짜·수치·인용·지도 라벨, 방짜유기 공정 단계도, 키네틱 타이포, AI 재현 공개 라벨처럼 글자와 타이밍이 정확해야 하는 장면에 우선 사용한다.

embedded-captions에 개발자 개인 경로가 포함됐다는 [공식 이슈 #3219](https://github.com/heygen-com/hyperframes/issues/3219)가 열려 있다. 핵심 캡션 지침만 쓰고 PORTING 문서와 test-set 예제는 제외하도록 라우팅 장부에 제한을 걸었다. 과거 snapshot과 실제 render가 달라질 수 있었던 [이슈 #1047](https://github.com/heygen-com/hyperframes/issues/1047)도 있어, 스냅샷만 보지 않고 최종 MP4 프레임을 검사한다.

실제 5초 렌더에서 기본 5 worker가 현재 V8 heap 권장치를 넘을 수 있다는 경고도 확인했다. 공장 adapter의 기본 capture worker를 4로 제한해 안정성을 우선했다. HyperFrames CLI의 core 누락은 0개다. 선택 팩 5개 중 Figma, PR-to-video, product-launch-video는 현재 채널 범위 밖이고, slideshow와 talking-head-recut은 기존 OpenMontage·Remotion 기능과 겹쳐 지금은 복사하지 않았다. 실제 파일럿에서 고유 기능이 필요할 때만 추가한다.

### Remotion과 FFmpeg

Remotion 패키지는 모두 4.0.508로 맞췄고, [공식 Remotion 스킬 저장소](https://github.com/remotion-dev/skills) b12104ef…의 12종을 프로젝트 내부에 복사했다. Remotion은 장면·자막·오디오·React 그래픽을 시간축에 결합하는 데 쓴다.

단순 자르기, 연결, 리사이즈, 코덱 변환, 음성 mux는 FFmpeg fast path를 유지한다. Reddit의 [Remotion·FFmpeg 비교 경험담](https://www.reddit.com/r/SaaS/comments/1s6gjh8/title_why_i_swapped_clientside_rendering_for/)도 참고했지만, 속도 수치는 개인 환경의 일화로만 취급한다.

## 4. TopView 기능 전수 분류

TopView의 [공식 종합 가이드](https://www.topview.ai/guides/topview-official-guide)는 이미지·영상·음성·아바타 기능을, [Board 공식 가이드](https://www.topview.ai/guides/ai-board)는 공유·평가·댓글·필터·배치 작업을 설명한다. [공식 모델 페이지](https://www.topview.ai/models)는 여러 영상·이미지 모델을 하나의 Board에서 쓴다고 안내한다.

### 작업 공간

| 기능 | 공장 채택 | 사용 위치 |
|---|---|---|
| Board | 기본 수동 | 후보 생성, 나란히 비교, 평가·고정·필터 |
| Canvas | 선택 수동 | 긴 다중 장면 탐색; canonical 계획은 아님 |
| 3D Shot Composer | 선택 수동 | 인물·소품·카메라의 공간 연속성이 중요한 숏 |
| Film Studio / Storyboard | 선택 수동 | 승인된 숏 계획 뒤의 대체 보드 탐색 |
| Drama Studio | 기본 제외 | 향후 극화 시리즈에만 검토 |

### 영상 기능

- **우선:** Image to Video, Omni/Multi Reference
- **필요 시:** Text to Video, First/Last Frame, Multi-shot, Motion Control
- **보조:** Video Edit, Repair, Upscale, Inpaint, Relighting
- **조건부:** Native Audio, Expression Control, Character Swap
- **기본 제외:** Subtitle removal
- **권리 확인 필수:** Watermark removal

### 이미지 기능

- Text to Image, Image Edit/Remix, Inpaint, Upscale
- Photo Angle Editor는 공간·시점 후보 제작에 우선 검토
- Background Removal, Image to Prompt, Color Palette는 보조 도구
- Character/Face Swap은 동의와 권리 확인이 있을 때만 사용
- Virtual Try-on과 Product Photography는 현재 다큐 기본 경로에서 제외

### 음성·아바타·3D·마케팅

- Voiceover와 Music은 보조 후보이며 최종 음성·음악 권리를 별도 기록한다.
- Voice Clone은 본인 동의 없이는 사용하지 않는다.
- Avatar와 UGC/광고 자동 생성기는 채널의 사실 기반 다큐 기본 문법과 맞지 않아 기본 제외한다.
- 3D World, Gaussian Splat, Image to 3D는 실험 경로다.
- URL-to-Video와 reference-style recreation은 저작권·표절 위험 때문에 기본 경로가 아니다.

### 모델 계열

TopView Board는 Seedance, Kling, Veo, Sora, Hailuo/MiniMax, Wan, Vidu, Runway와 GPT Image, Nano Banana, Seedream, Kontext 계열을 소개한다. 계열명만으로 버전·가격·길이·해상도·오디오 지원을 확정하지 않는다. 작업자는 매 유료 시도 전에 화면에 표시된 전체 모델명, 실제 설정, 예상 크레딧, 시도 횟수, 설정 캡처, 제출·완료 시각과 큐 표시를 남긴다.

전체 기능과 상태는 [config/topview-capabilities.yaml](../../config/topview-capabilities.yaml)에 기계 판독 가능한 형태로 저장했다.

### API와 공식 스킬을 설치하지 않은 이유

TopView에는 [공식 agent skill 저장소](https://github.com/topviewai/skill/tree/5e0fa64642cd732ad18382e91195171f2957453d)가 있고 API·MCP 기능을 제공한다. 사용자가 반자동 수동 운용을 확정했으므로 공장에는 설치하지 않았다. 공식 skill은 기능 용어를 확인하는 참고 자료일 뿐이며 API 제출·폴링, MCP 호출, Codex 플러그인, 브라우저 자동 클릭, 자동 결제·재시도·다운로드·승인은 금지한다.

대신 프로젝트 전용 topview-manual-handoff 스킬과 job/result 스키마를 만들었다.

## 5. TopView Reddit 검토와 안전장치

Reddit에는 결과에 만족한 제작 사례도 있고, 긴 대기열·크레딧·버전 표시·연속성 실패를 호소한 글도 있다. [TopView 사용자 의견 모음](https://www.reddit.com/r/Seedance_v2/comments/1s9f19u/any_reviews_or_thoughts_on_topview/), [무제한 플랜 토론](https://www.reddit.com/r/Seedance_AI/comments/1sjamnd/unlimited_plans_real_or_a_hoax/), [Seedance 단편 제작 사례](https://www.reddit.com/r/Seedance_AI/comments/1s6xy1i/i_made_a_400_live_action_short_film_using/)를 함께 검토했다.

이 일화들로 서비스 품질을 단정하지 않고 다음 안전장치만 반영했다.

- 첫 결제는 소수 숏의 작은 파일럿으로 제한
- 연간 플랜이나 무제한을 생산량 보장으로 가정하지 않음
- 모델 표시와 제출 전 비용을 캡처
- 숏별 시도 수와 배치별 총 예산 상한
- 긴 큐·반복 실패·연속성 붕괴 시 Router fallback
- 다운로드를 곧바로 selected로 만들지 않음

## 6. GitHub 검토와 기술 위험

안정 릴리스 [ComfyUI v0.31.0](https://github.com/Comfy-Org/ComfyUI/releases/tag/v0.31.0)을 vendor에 고정했다. 이 릴리스의 LTX-2.3과 Wan 2.2 공식 blueprint 사본과 해시도 잠갔다.

Mac에서는 다음 공개 이슈를 반영했다.

- 큰 attention 행렬에서 조용한 MPS 출력 손상이 보고된 [#14837](https://github.com/Comfy-Org/ComfyUI/issues/14837)
- Wan 2.2 TI2V 5B의 세로 줄무늬가 보고된 [#15010](https://github.com/Comfy-Org/ComfyUI/issues/15010)
- MPS가 특정 FP8 dtype을 지원하지 않는 [#12202](https://github.com/Comfy-Org/ComfyUI/issues/12202)

따라서 작업이 오류 없이 끝났다는 로그만으로 성공 처리하지 않는다. 고정 seed의 저해상도 파일럿, FP16 또는 이미 검증된 dtype, ffprobe, 실제 프레임 샘플, 검은 프레임·밴딩·색 손상 검사를 통과해야 한다.

Reddit의 [M5 Max LTX-2.3 속도 경험](https://www.reddit.com/r/comfyui/comments/1tldb1k/mac_experience/)과 [M4 Pro 검은 프레임 사례](https://www.reddit.com/r/comfyui/comments/1suuyvu/ltx_23_i2v_on_m4pro_macmini_64gb_unified_memory/)는 하드웨어·workflow별 편차가 크다는 신호다. LOCAL_LTX는 무료·프라이버시·컨셉 파일럿에 강하지만, 납기 중심 대량 생산의 무조건적 기본값으로 두지 않았다.

## 7. Hugging Face 검토

TopView 자체의 공식 생성 가중치나 공식 Space는 확인되지 않았다. TopView는 로컬 모델이 아니라 여러 모델을 제공하는 hosted workspace로 취급한다.

| 모델 | 고정 리비전 | 라이선스/판정 |
|---|---|---|
| [Lightricks/LTX-2.3](https://huggingface.co/Lightricks/LTX-2.3) | 6f352058… | LTX-2 Community License, 다운로드 전 Human Gate |
| [Wan2.2-I2V-A14B](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B/tree/206a9ee1b7bfaaf8f7e4d81335650533490646a3) | 206a9ee1… | Apache-2.0, 선택 로컬 |
| [Wan2.2-TI2V-5B](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B/tree/921dbaf3f1674a56f47e83fb80a34bac8a8f203e) | 921dbaf3… | Apache-2.0, MPS 별도 파일럿 |
| [FLUX.2-klein-4B](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/tree/e7b7dc27f91deacad38e78976d1f2b499d76a294) | e7b7dc27… | Apache-2.0, 우선 로컬 이미지 후보 |
| FLUX.1-Kontext-dev | 24e9dedc… | gated/기타 라이선스, 조건부 |
| HunyuanVideo-1.5 | 9b49404b… | 기타 라이선스, 기본 제외 |

가중치는 용량보다 라이선스와 실제 workflow 검증이 먼저이므로 Git에 복사하지 않았다. 전체 값은 [config/local-models.lock.json](../../config/local-models.lock.json)에 있다.

## 8. 도구 104개 전수 분류

OpenMontage registry의 모든 도구를 [config/tool-inventory.json](../../config/tool-inventory.json)에 기록했다.

| 상태 | 개수 | 의미 |
|---|---:|---|
| ACTIVE_LOCAL | 33 | 현재 로컬에서 쓸 수 있음 |
| LOCAL_SETUP_REQUIRED | 6 | 로컬 의존성·모델 설치 후 사용 |
| MANUAL_BRIDGE | 2 | TopView 작업지시서 생성과 결과 반입 |
| PLANNING_ONLY | 4 | 실행이 아닌 경로 선택·계획 |
| HUMAN_GATE_ONLY | 1 | 게시 등 사람 승인 전용 |
| EXPLICIT_OPT_IN | 39 | 네트워크나 외부 서비스라 명시 선택 필요 |
| DISABLED_BY_DEFAULT | 6 | 인증·유료 제공자 기본 비활성 |
| OPTIONAL | 13 | 승인된 숏 설계가 필요할 때만 사용 |

레지스트리에 등록돼 있다는 사실은 사용 승인이라는 뜻이 아니다. 네트워크·인증·게시·유료 호출은 각각의 정책 상태를 따른다.

## 9. 스킬 107개 전수 분류

모든 .agents/skills 하위 스킬을 프로젝트 안에 실제 파일로 보관하고 tree SHA-256을 [vendor/skills/manifest.json](../../vendor/skills/manifest.json)에 기록했다. 심볼릭 링크는 쓰지 않는다.

| 출처 | 개수 | 내용 |
|---|---:|---|
| OpenMontage 기준본 | 71 | 조사·생성·편집·음성·메타 작업 지침 |
| 기존 사용자 모션 스킬 선별 이관 | 8 | 숏 구성, 키네틱 타이포, 색·모션 등 |
| HyperFrames 0.7.106 | 14 | 코어·CLI·애니메이션·미디어·장르 지침 |
| Remotion 공식 최신 | 12 | 캡션·마크업·멀티미디어·렌더·업그레이드 등 |
| remotion-bits | 1 | 고급 예제 참고; upstream 라이선스 미확인 |
| 유튜브공장 전용 | 1 | TopView 수동 handoff |

사용 정책은 [config/factory-skill-routing.yaml](../../config/factory-skill-routing.yaml)에 있다.

| 상태 | 개수 | 의미 |
|---|---:|---|
| REQUIRED | 37 | 해당 제작 단계에서 핵심 |
| REQUIRED_WITH_RESTRICTION | 1 | HyperFrames embedded captions 핵심만 사용 |
| OPTIONAL | 47 | 숏 요구가 있을 때만 사용 |
| REFERENCE_ONLY | 7 | 지식 참고, 정상 실행 경로 아님 |
| DISABLED_BY_DEFAULT | 15 | 외부 제공자·키·유료 경로 기본 금지 |

setup-api-key, Seedance, Kling, HeyGen 등 제공자 스킬이 보존돼 있어도 자동 호출되지는 않는다. 향후 사용자가 명시적으로 다른 운영 방식을 승인할 때 재검토할 수 있게 삭제 대신 비활성으로 남겼다.

## 10. 실제로 복사·업데이트한 것

- 깨끗한 OpenMontage 공식 tree와 source lock
- HyperFrames 0.7.106 스킬 14종
- Remotion 4.0.508 런타임과 공식 스킬 12종
- ComfyUI v0.31.0 전체 소스와 LTX/Wan blueprint
- 사용자 모션 지침 8종과 remotion-bits 참고 자료
- TopView 수동 handoff 전용 스킬·스키마·도구
- 모든 스킬의 해시 manifest와 라우팅 정책
- 모든 registry 도구의 상태 inventory
- 로컬 모델 exact revision·license lock
- 독립 ComfyUI bootstrap/start와 프로젝트 전용 모델 경로

## 11. 의도적으로 복사하지 않은 것

- 기존 /Users/mk-macbook/Desktop/openmontage의 Git 정보, 환경파일, 프로젝트, 캐시, 렌더, 모델
- API 키, 로그인 쿠키, TopView 인증정보
- TopView 공식 MCP/API 생성 스킬
- Hugging Face 대형 모델 가중치
- ComfyUI custom node와 사용자 설정
- 검토되지 않은 음성·얼굴 데이터

이 제외 목록이 오염 방지와 비용 통제의 핵심이다. 필요한 모델이나 custom node는 파일럿 요구가 확정된 뒤 이 새 폴더 안에서만 설치한다.

## 12. 운영 결론

- **구조:** 확정해도 된다. OpenMontage 최상위 구조가 가장 효율적이다.
- **TopView:** NewTake 대신 선택을 유지하되, 전체 시스템을 대체시키지 않는다.
- **자동화 수준:** 조사·계획·작업지시서·반입·검사는 자동화하고, TopView 조작·결제·선택은 사람이 한다.
- **로컬 생성:** 작은 파일럿과 대체 경로로 유용하지만 Mac 처리량과 MPS 품질을 실측한다.
- **정확한 정보 표현:** 생성 모델이 아니라 HyperFrames/Remotion에서 증거와 연결한다.
- **다음 제작 단계:** 새 도구를 더 붙이기보다 방짜유기 30~60초 수동 파일럿을 전체 Gate 흐름으로 한 번 완주해 병목을 측정한다.

## 13. 실행 검증 결과

- 공장 전체 Python 테스트: **1,005 passed, 10 skipped, 1 subtest passed**
- 공장·TopView·도구 장부 집중 테스트: **84 passed**
- HyperFrames 실제 렌더: 5.0초, 1920×1080, 30fps, H.264; 프레임 직접 확인
- Remotion 실제 렌더: 5.55초, 960×540, 30fps, H.264/AAC; 프레임 직접 확인
- Remotion 패키지: 전체 4.0.508 정렬 확인
- HyperFrames 스킬: current 14, outdated 0, core missing 0
- TopView 전용 스킬: skill validator 통과
- JSON/YAML, shell syntax, Git whitespace 검사 통과
- 유료 호출, TopView 자동화, 모델 가중치 다운로드, 게시, Human Gate 대리 승인: **수행하지 않음**
