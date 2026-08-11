# MK Visual Director Final Design v1

## Document status

- Version: 1.0
- Date: 2026-08-11
- Status: DESIGN_READY_FOR_CROSS_REVIEW
- Implementation: NOT AUTHORIZED
- Paid production calls: NOT AUTHORIZED
- Final render or publication: NOT AUTHORIZED

이 문서는 지금까지 논의한 Visual Director, Visual Grammar, 실제 자료+AI 재현 혼합, HyperFrames, OpenMontage, TopView, 방짜유기 레퍼런스 분석을 하나의 구현 가능한 최종 설계로 통합한다.

## 1. Objective

목표는 특정 LLM이나 특정 영상 생성 모델에 종속되지 않는 시네마틱 다큐멘터리 제작 시스템이다.

사용자가 매번 모든 구도와 카메라를 직접 지시하지 않아도 시스템이 다음을 수행해야 한다.

1. 대본의 의미와 내러티브 기능 분석
2. Sequence 단위 연출 설계
3. Shot 단위 촬영·편집·오디오 설계
4. 실제 자료, AI 재현, 그래픽의 적절한 라우팅
5. 생성 전 Animatic과 비용 검토
6. provider별 생성과 결과 수집
7. 정확한 타이포·수치·도면 합성
8. 오디오·자막·편집·출처·QC
9. 사용자 승인 후 최종 렌더와 공개

## 2. Non-negotiable principles

### 2.1 Meaning before camera

~~~text
script
→ narrative function
→ information and emotion
→ sequence grammar
→ shot coverage
→ camera and lighting
→ provider
~~~

대본 한 문장을 바로 한 클립으로 바꾸지 않는다.

### 2.2 Sequence before Shot

Shot은 단독 이미지가 아니라 앞뒤 숏과 함께 의미를 만든다. 먼저 Sequence의 시작·전개·리빌·설명·종료를 설계하고 그 안에서 coverage를 만든다.

### 2.3 Clean plate

생성 영상에는 정확한 글자, 날짜, 수치, 화살표, 로고, 도면 설명을 넣지 않는다.

~~~text
clean_plate.mp4
+ overlay
+ narration
+ SFX
+ BGM
= final_shot.mp4
~~~

### 2.4 Evidence and reconstruction separation

모든 화면은 다음 중 하나 또는 명시적인 혼합형으로 분류한다.

- REAL: 실제 사진·영상·문서·도면
- AI_RECONSTRUCTION: 사실에 근거한 AI 재현
- GRAPHIC: 설명 그래픽·지도·타임라인
- HYBRID: 실제 자료 위 정밀 그래픽 또는 실제 자료에서 AI 재현으로 전환

### 2.5 Local source of truth

TopView, Newtake 또는 다른 원격 Canvas는 탐색·생성 공간이다. 최종 source of truth는 로컬 OpenMontage 프로젝트, asset registry, source registry, Git 기록이다.

### 2.6 Human Gates

다음은 자동 승인하지 않는다.

- 주제 확정
- 최종 대본
- 사실·출처 lock
- Animatic
- 유료 생성 예산
- 주요 생성 asset 선택
- 최종 편집
- 제목·썸네일
- 공개

## 3. Scope and non-goals

### In scope

- 8~20분 정보형 시네마틱 다큐
- 실제 사료가 있는 역사·사건·기술·공예 주제
- REAL/AI/GRAPHIC 혼합
- 다국어 overlay와 자막
- 여러 LLM 및 영상 provider 교체
- 60~90초 Golden Pilot

### Not in initial scope

- 완전 자동 주제 선정과 무승인 공개
- 생성 모델이 만든 글자·숫자를 최종 사실로 사용
- 모든 숏의 Blender 정밀 3D
- 영상 생성만으로 15분 전체 구성
- 실시간 협업 편집기
- 사용자 승인 없는 연간 구독 또는 대량 API 호출

## 4. System architecture

~~~text
TOPIC + RESEARCH SOURCES
          ↓
Evidence Layer
Source Registry + Claim Ledger + Rights
          ↓
SCRIPT
          ↓
MK VISUAL DIRECTOR
Semantic Analysis
Narrative Function
Sequence Plan
Visual Grammar
Shot Plan
Continuity Anchors
          ↓
ANIMATIC
REAL placeholders + storyboard + temp VO + timing
          ↓
HUMAN GATE: creative + factual + budget approval
          ↓
PRODUCTION ROUTER
   ├─ REAL → ingest and normalize
   ├─ IMAGE → TopView / local image provider
   ├─ VIDEO → TopView API / TopView Canvas / local LTX
   └─ GRAPHIC → HyperFrames
          ↓
OPENMONTAGE
Timeline + audio + captions + registry + QC
          ↓
REVIEW BUILD
          ↓
HUMAN GATE: final edit
          ↓
FINAL RENDER
          ↓
HUMAN GATE: publish
~~~

## 5. Canonical project artifacts

모든 LLM과 provider는 다음 artifact를 읽고 쓴다.

| Artifact | Owner | Purpose |
|---|---|---|
| brief / proposal packet | OpenMontage | 주제·시청자·delivery promise·runtime 후보 |
| source-registry.json | Evidence Layer sidecar | 출처·권리·원본 위치 |
| claim-ledger.json | Evidence Layer sidecar | 검증 문장과 근거 연결 |
| script | OpenMontage canonical | 승인된 대본 |
| visual-plan.json | Visual Director IR | Sequence·Shot·routing의 고해상도 계약 |
| scene_plan | OpenMontage canonical | VisualPlan에서 컴파일한 실행 가능한 장면 계획 |
| visual-grammar/*.yaml | Visual Grammar | 재사용 연출 규칙 |
| animatic.mp4 | OpenMontage project media | 생성 전 타이밍·구성 검수 |
| asset_manifest | OpenMontage canonical | 모든 생성·수집 asset과 provenance |
| edit_decisions | OpenMontage canonical | 컷·오디오·transition·overlay·잠긴 runtime |
| render_report / final_review | OpenMontage canonical | 렌더 정보와 실제 미디어 QC |
| checkpoint_<stage>.json | OpenMontage checkpoint | 단계 상태와 Human Gate |

VisualPlan의 기계 검증 계약은 [`visual-plan.schema.json`](../schemas/visual-plan.schema.json)을 기준으로 한다.

### 5.1 OpenMontage compatibility rule

VisualPlan은 OpenMontage `scene_plan`을 대체하지 않는 중간 표현(IR)이다. Phase 1의 deterministic compiler가 VisualPlan을 현재 OpenMontage `scene_plan` schema에 맞는 canonical artifact로 변환한다.

~~~text
visual-plan.json
    ↓ validate + semantic checks
visual_plan_compiler
    ↓
scene_plan.json
metadata.visual_plan_ref
metadata.visual_plan_sha256
metadata.shot_id_map
~~~

OpenMontage `scene_plan`은 `additionalProperties: false`이므로 VisualPlan의 shot-level evidence·continuity·overlay 필드를 임의로 밀어 넣지 않는다. 두 파일 사이의 ID mapping과 checksum을 기록하고, VisualPlan이 바뀌면 `scene_plan`을 다시 생성한다. 수동으로 둘을 따로 수정하지 않는다.

## 6. Evidence Layer

### 6.1 Source Registry

Source Registry는 URL 모음이 아니다. 각 자료에 다음을 기록한다.

- source_id
- canonical URL 또는 원본 파일
- publisher
- title
- publication or capture date
- retrieved_at
- source type
- rights and license
- allowed uses
- local checksum
- credibility tier
- notes

### 6.2 Claim Ledger

대본의 사실 문장은 claim_id를 갖는다.

~~~text
CLAIM_0018
text: 원래 설계는 하나의 연속 행어 로드를 전제로 했다.
citations:
  - source_id: SRC_0042
    pinpoint: p. 18, figure 4
    relationship: supports
  - source_id: SRC_0061
    pinpoint: 00:12:08–00:12:31
    relationship: context_only
confidence: high
status: verified
visualizable: true
~~~

AI 재현 프롬프트는 claim과 source 없이 사실을 추가할 수 없다.

### 6.3 Credibility tiers

1. 원문 보고서·공식 기록·법원·정부·박물관
2. 학술 논문·전문기관
3. 신뢰 가능한 2차 자료
4. 언론·인터뷰
5. 커뮤니티·사용자 경험

Tier 5는 제품 대기열·실사용 경험에는 활용할 수 있지만 역사적 핵심 사실의 단독 근거로 쓰지 않는다.

## 7. MK Visual Director

Visual Director는 하나의 거대한 프롬프트가 아니라 다음 단계의 결정 시스템이다.

### 7.1 Semantic analysis

대본 블록마다 다음을 추출한다.

- narrative_function: hook, context, evidence, reveal, explanation, tension, consequence, reflection
- emotion
- information target
- required factual precision
- available materials
- subject and object identities
- continuity requirements
- expected viewer question

### 7.2 Sequence planning

Sequence는 15~60초 범위의 의미 단위다.

필수 필드:

- sequence_id
- purpose
- narration range
- evidence ids
- visual grammar candidates
- selected grammar
- pacing profile
- entry and exit transitions
- shot list
- target duration

### 7.3 Shot planning

Shot은 다음을 명시한다.

- shot_id and sequence_id
- narrative function
- representation type
- coverage role
- source or provider
- prompt intent
- camera framing, angle, height, lens intent, movement
- lighting
- composition and negative space
- continuity bindings
- edit trigger
- transition in/out
- audio layers
- overlay contract
- duration
- fallback
- evidence ids
- cost tier

### 7.4 Coverage rules

하나의 생성 클립이 전체 Sequence를 담당하지 않는다.

기본 coverage:

- establishing wide
- spatial medium
- action medium
- hand or object close-up
- material macro
- face detail when needed
- evidence insert
- hero or consequence shot

인물·공간 연속성이 약한 AI의 특성을 짧은 coverage 편집으로 보완한다.

## 8. Visual Grammar

Visual Grammar는 효과 목록이 아니라 사용 조건과 금지 조건을 가진다.

초기 필수 grammar:

1. archive_to_reality
2. evidence_to_reconstruction
3. freeze_to_explain
4. photo_to_video
5. document_zoom
6. object_isolation
7. diagram_to_reality
8. map_to_location
9. before_after
10. timeline_travel
11. wide_medium_close
12. cause_effect
13. graphic_match
14. shape_match
15. sound_bridge
16. foreground_reveal
17. rack_focus
18. heritage_forge

각 grammar는 다음을 가져야 한다.

- purpose
- use_when
- avoid_when
- required inputs
- sequence pattern
- timing range
- continuity requirements
- compatible providers
- overlay rules
- audio rules
- failure patterns
- acceptance examples

### 8.1 HERITAGE_FORGE

방짜유기 레퍼런스에서 추출한 grammar다.

- 반복 물성 모티프
- warm practical + cool shadow
- rim/backlight separation
- wide–macro 교차
- 느린 숏 내부 움직임 + 빠른 컷
- cut on impact
- shape match
- 제목의 opening/end recall
- 결과물 또는 증거의 hero reveal

정의 파일: [`HERITAGE_FORGE.yaml`](../config/visual-grammars/HERITAGE_FORGE.yaml)

## 9. Director Memory

Director Memory는 모델 채팅 기록이 아니다. 승인·거절된 선택을 구조화한다.

### Store

- 선호 pacing
- 과도하다고 판정한 transition
- 승인된 color and lighting families
- 반복을 피할 camera patterns
- title and typography rules
- actual user corrections
- Golden Test scores

### Do not store

- 검증되지 않은 사실
- provider 홍보 문구
- 모델이 스스로 내린 품질 주장
- 특정 주제의 우연한 스타일을 전체 채널 규칙으로 일반화한 값

## 10. LLM independence

공용 연출 규칙은 모델 adapter 안에 넣지 않는다.

~~~text
adapters/
  claude.md
  gpt.md
  gemini.md

visual-director/
  grammar/
  continuity/
  qc/
  schemas/
~~~

Adapter는 모델별 출력 안정화만 담당한다.

- JSON only enforcement
- reasoning order
- token budgeting
- retry and repair behavior

Claude와 GPT는 동일한 VisualPlan schema로 출력해야 한다. 결과 품질은 Golden Test로 비교한다.

## 11. Production Router

### 11.1 Routing decision

~~~text
exact historical evidence exists
→ REAL or REAL+GRAPHIC

precise numbers, text, diagram, map
→ HyperFrames

cinematic reconstruction required
→ image master + TopView video

layout or camera blocking uncertain
→ TopView Canvas or 3D Shot Composer

low-cost draft
→ local image + local LTX

sensitive or unpublished source
→ local provider only
~~~

### 11.2 Provider interface

모든 영상 provider는 개념적으로 다음 계약을 구현한다.

~~~text
submit(shot_request) → task_id
status(task_id) → queued | running | succeeded | failed
result(task_id) → files + metadata + cost
cancel(task_id) → best effort
~~~

필수 metadata:

- provider
- provider model
- request id
- prompt and negative prompt
- input asset checksums
- submitted_at, completed_at
- billed credits or cost
- output URL
- local file
- local checksum
- retry parent id
- failure reason

### 11.3 Normalized state mapping

provider 원본 상태를 OpenMontage 내부 상태와 같은 문자열로 오인하지 않는다.

| Normalized | TopView 예시 raw status | 의미 |
|---|---|---|
| queued | init | 제출되었고 처리 대기 |
| running | running | 처리 중 |
| succeeded | success | 결과와 실제 비용 수집 가능 |
| failed | fail 또는 오류 code | 실패 사유와 차감 여부 확인 |
| canceled | provider 지원 시 raw value | best-effort 취소, 실제 종료 재조회 |

`raw_status`, `raw_response`, `error_code`, `costCredit`을 보존한다. 문서상 일반화보다 실제 endpoint의 task query 응답을 우선한다.

## 12. TopView integration

### 12.1 Two paths

#### Canvas path

용도:

- 스타일 탐색
- 3D blocking
- 멀티앵글 후보
- reference 비교
- 인물·소품·카메라 위치 검토

Canvas에서 승인된 결과는 즉시 로컬로 내려받고 shot_id로 이름을 바꾼다.

#### API path

용도:

- 승인된 ShotPlan batch 생성
- task polling
- retry
- 비용 추적
- provider model 교체

### 12.2 Billing boundary

- 웹 계정의 표준 크레딧은 API와 공유되지만 기능별 과금 방식은 같다고 가정하지 않는다.
- Ultra 크레딧과 Unlimited·프로모션 혜택은 API 자동화 가용량으로 계산하지 않는다.
- 모든 유료 호출 전에 estimated cost를 기록한다.
- 월간 pilot에서 실제 숏당 비용과 실패율을 측정한다.

### 12.3 Storage boundary

API 결과 URL은 영구 저장소가 아니다. 성공 즉시 다운로드하고 ffprobe, checksum, frame review를 수행한다.

### 12.4 Model routing

모델명은 Visual Director가 직접 결정하지 않는다. requirements를 보고 Router가 선택한다.

예:

- reference fidelity high → reference 강점 모델
- complex human motion → motion 강점 모델
- native audio needed → audio-video model
- strong camera effect → camera-control 모델
- cheap draft → local LTX

모델별 강점은 provider 공식 설명이 아니라 pilot 결과로 보정한다.

## 13. Image master stage

영상 생성 전에 keyframe image에서 다음을 확정한다.

- 시대와 장소
- 인물과 의상
- 피사체 위치
- 카메라 앵글
- 조명
- 색감
- negative space
- overlay safe area
- 시작 프레임
- 가능하면 종료 프레임

텍스트 overlay가 필요하면 먼저 최종 레이아웃을 설계하고 이미지를 그 레이아웃에 맞춰 생성한다.

## 14. HyperFrames

초기 필수 모듈:

1. TYPOGRAPHY
2. NUMBER
3. UNDERLINE
4. CALLOUT
5. DIAGRAM
6. DOCUMENT
7. ARCHIVE_FRAME
8. RECONSTRUCTION_LABEL

HyperFrames는 매 숏을 장식하지 않는다. 정확성이 필요한 구간에서만 개입한다.

이 목록은 시각 기능 contract다. OpenMontage에서 실제 합성 engine은 proposal 단계에서 선택한다.

- `render_runtime=hyperframes`: HyperFrames가 clean plate와 overlay를 한 runtime 안에서 합성
- `render_runtime=remotion`: 같은 정보 정확성·safe-area·재현 라벨 계약을 Remotion 구성으로 구현하거나, 승인된 투명 overlay asset을 입력으로 사용
- `render_runtime=ffmpeg`: 단순 컷·자막 외 복잡한 도식이 필요한 brief에는 권고하지 않음

두 runtime이 모두 사용 가능하면 각각의 장단점을 사용자에게 제시하고 명시적 승인을 받은 뒤 하나를 잠근다. 무단 교체는 금지한다. 이 시스템의 정밀 모션그래픽 중심 Golden Pilot에는 HyperFrames를 우선 권고하지만 자동 선택하지 않는다.

### Required behavior

- seek-safe deterministic render
- fixed layout at target resolution
- safe-area validation
- source and reconstruction labels
- multilingual text substitution
- transparent or composited output
- frame-accurate timing

## 15. OpenMontage

OpenMontage는 전체 제작의 source of truth와 delivery layer다.

### Responsibilities

- pipeline manifest
- asset and source registry
- render runtime selection
- timeline
- captions
- narration, SFX, BGM
- task state and checkpoints
- QC
- review builds
- final delivery

### 15.1 Canonical compatibility

기준 OpenMontage 계약은 다음과 같다.

- 파이프라인: 실제 자료와 생성 보조 영상이 섞인 경우 `hybrid` 우선 검토
- canonical stages: `idea → script → scene_plan → assets → edit → compose → publish`
- checkpoint status: `in_progress | awaiting_human | completed | failed`
- canonical artifacts: `brief`, `script`, `scene_plan`, `asset_manifest`, `edit_decisions`, `render_report`, `final_review`, `publish_log`
- `render_runtime`: proposal/idea 결정에서 잠그고 `edit_decisions`까지 변경 없이 전달
- runtime 변경: 사용자 승인과 append-only `decision_log` 기록 필요

Visual Director의 세부 gate는 위 canonical stage의 checkpoint와 mapping한다. 별도의 경쟁 checkpoint 엔진을 만들지 않는다.

### 15.2 Runtime selection

한 프로젝트에서 HyperFrames와 Remotion을 동시에 주력 runtime으로 가정하지 않는다. OpenMontage의 실제 registry로 사용 가능 여부를 확인한 뒤 proposal에서 두 경로와 FFmpeg 적용 가능성을 제시한다. 사용자가 선택한 `render_runtime`과 `composition_mode`를 decision log에 기록한다.

## 16. Audio and edit grammar

방짜유기 영상 분석에서 다음 규칙을 채택한다.

### 16.1 End anchor edit

엔딩 음악 히트, 마지막 문장, 최종 title recall을 먼저 고정하고 앞부분을 편집한다.

### 16.2 Beat map

다음을 하나의 timeline event로 통합한다.

- narration clause boundaries
- music beat and section
- SFX transients
- action impacts
- title reveal
- silence and breath

### 16.3 Cut policies

- cut_on_impact
- cut_on_narration_clause
- shape_match
- motion_match
- sound_bridge
- evidence_insert

오디오 이벤트 기반 컷은 목표 이벤트의 ±2 frames 안에 있는지 검사한다.

## 17. REAL + AI + GRAPHIC mixing

권장 sequence:

~~~text
actual archive
→ source/date label
→ slow push and object callout
→ locked match frame
→ AI reconstruction label
→ short clean plate motion
→ freeze and dim
→ structural explanation
→ actual drawing or report
→ return to reconstruction
~~~

비율은 고정하지 않는다. 자료가 풍부할수록 REAL+GRAPHIC 비중을 높인다.

초기 가설:

- AI video: 35–45%
- REAL: 25–30%
- GRAPHIC: 20–25%
- map/timeline/other: 5–10%

이 값은 목표가 아니라 pilot 관측 기준이다.

## 18. Project folder structure

~~~text
projects/<project-id>/
  project.json
  checkpoint_idea.json
  checkpoint_script.json
  checkpoint_scene_plan.json
  checkpoint_assets.json
  checkpoint_edit.json
  checkpoint_compose.json
  checkpoint_publish.json
  artifacts/
    brief.json
    decision_log.json
    source-registry.json
    claim-ledger.json
    script.json
    visual-plan.json
    scene-plan.json
    asset-manifest.json
    edit-decisions.json
    render-report.json
    final-review.json
  assets/
    images/
    video/
    audio/
    music/
    graphics/
  renders/
    animatic.mp4
    review-build.mp4
    final.mp4
  history/
~~~

각 shot의 생성 중간물은 OpenMontage `assets/` 아래에 두고 asset manifest에서 묶는다.

~~~text
assets/video/SEQ03_SH07/
  reference/
  keyframe.png
  clean_plate.mp4
  overlay.mov
  final.mp4
  generation.json
  qc.json
~~~

Backlot이 읽는 canonical checkpoint와 artifact 경로를 임의 구조로 바꾸지 않는다. sidecar 파일도 `artifacts/`에 두고 canonical artifact의 `metadata`에서 ref와 checksum을 남긴다.

## 19. Human Gate mapping

### OpenMontage checkpoint states

- in_progress
- awaiting_human
- completed
- failed

`completed`가 승인 gate를 의미하는 stage에서는 `human_approved=true`가 실제 사용자 승인과 함께 있어야 한다. 검토 중의 `drafting`, `rejected`, `needs_revision`, `superseded`는 설계 artifact의 review status 또는 history로 표현하고 checkpoint status enum을 확장하지 않는다.

### Gates

1. GATE_TOPIC
2. GATE_SCRIPT
3. GATE_EVIDENCE_LOCK
4. GATE_ANIMATIC
5. GATE_BUDGET
6. GATE_ASSET_SELECTION
7. GATE_FINAL_EDIT
8. GATE_TITLE_THUMBNAIL
9. GATE_PUBLISH

어떤 에이전트도 approved 상태를 추정하거나 생성해서는 안 된다.

### Gate-to-stage mapping

| Visual Director gate | OpenMontage checkpoint 또는 artifact |
|---|---|
| GATE_TOPIC | `checkpoint_idea.json` |
| GATE_SCRIPT | `checkpoint_script.json` |
| GATE_EVIDENCE_LOCK | script 또는 scene_plan gate의 evidence sidecar + approval record |
| GATE_ANIMATIC | `checkpoint_scene_plan.json`과 animatic ref |
| GATE_BUDGET | idea/asset checkpoint의 cost snapshot + decision log |
| GATE_ASSET_SELECTION | `checkpoint_assets.json` |
| GATE_FINAL_EDIT | review-build에 대한 별도 사용자 approval record; pipeline 확장 필요 |
| GATE_TITLE_THUMBNAIL | publish 준비 artifact; pipeline 확장 필요 |
| GATE_PUBLISH | `checkpoint_publish.json` |

현재 `hybrid` pipeline의 edit/compose는 기본적으로 자동 진행될 수 있으므로, GATE_FINAL_EDIT을 강제하려면 Phase 1에서 custom pipeline manifest 또는 승인 artifact를 추가한다. 문서상의 gate만으로 보호된다고 간주하지 않는다.

## 20. QC

### 20.1 Data QC

- schema validation
- required evidence ids
- claim citation의 page·section·figure·timestamp pinpoint
- VisualPlan evidence id와 Source Registry의 referential integrity
- valid shot and sequence ids
- narration start < end, shot duration 합계와 sequence target의 허용 오차
- top-level plan status와 approval status의 일관성
- VisualPlan checksum과 compiled scene plan checksum의 freshness
- allowed representation values
- no orphan assets
- no unapproved provider calls

### 20.2 Media QC

- file exists and decodes
- expected duration, resolution, frame rate
- audio stream presence
- representative frame inspection
- motion continuity
- face, wardrobe, prop continuity
- incorrect text or watermark detection
- black frames and frozen frames
- clipping and loudness

### 20.3 Factual QC

- every displayed number maps to claim_id
- AI reconstruction label exists when needed
- source license conditions met
- actual archive not misrepresented
- uncertain claim is not written as fact

### 20.4 Editorial QC

- repeated camera pattern
- transition overuse
- AI texture fatigue
- pacing monotony
- evidence-to-reconstruction clarity
- title and subtitle readability

## 21. Failure and fallback

| Failure | Fallback |
|---|---|
| TopView queue too slow | paid priority within budget, alternate model, local LTX, still+2.5D |
| identity drift | stronger reference, shorter clip, cutaway coverage |
| tool geometry drift | actual archive or macro insert, regenerate only affected shot |
| text generated in plate | reject, regenerate clean, crop only if composition survives |
| factual visual uncertain | replace with REAL+GRAPHIC |
| API result expired | restore local checksum copy; never rely on remote URL |
| budget exceeded | stop at budget gate, reduce candidate count or AI ratio |
| HyperFrames too complex | simplify graphic, use static labeled evidence |

## 22. Golden Tests

### 22.1 Hyatt 60–90s

검증 대상:

- actual archive
- date typography
- walkway callout
- locked push-in
- AI match reconstruction
- clean plate motion
- freeze to explain
- hanger rod diagram
- actual engineering drawing
- return to reconstruction
- narration, SFX, BGM

상세: [`HYATT-60-90S-GOLDEN-SEQUENCE.md`](../golden-tests/HYATT-60-90S-GOLDEN-SEQUENCE.md)

### 22.2 Bangjja style

검증 대상:

- repeated material motif
- wide–macro coverage
- warm/cool lighting
- impact cuts
- same artisan continuity
- title recall
- product/evidence hero reveal

상세: [`BANGJJA-STYLE-ACCEPTANCE-TEST.md`](../golden-tests/BANGJJA-STYLE-ACCEPTANCE-TEST.md)

## 23. Implementation phases

### Phase 0: design cross-review

- Claude independent review
- Codex independent review
- cross-review
- final consensus
- Final Design v2
- User Human Gate

### Phase 1: contracts and local dry run

- schemas
- Source Registry
- Claim Ledger
- Visual Grammar loader
- VisualPlan validator
- VisualPlan → OpenMontage scene_plan compiler
- canonical artifact ref/checksum mapping
- final-edit gate를 강제하는 custom hybrid manifest 검토
- placeholder animatic
- no paid generation

### Phase 2: HyperFrames core

- 8 initial modules
- archive motion
- source labels
- multilingual overlay
- deterministic frame QA

### Phase 3: TopView pilot adapter

- auth through local secret handling
- submit/status/result
- download and checksum
- cost ledger
- retry and failure capture

### Phase 4: Golden Pilot

- Hyatt or approved alternative
- 720p review build
- no final 1080p before approval
- cross-model VisualPlan benchmark

### Phase 5: production hardening

- queue strategy
- concurrency
- caching
- provider fallback
- regression tests
- per-episode metrics

## 24. Acceptance criteria

설계가 구현 준비 완료로 바뀌려면 다음이 모두 충족되어야 한다.

1. Claude와 Codex가 schema로 Hyatt Golden Sequence를 표현 가능하다고 판정
2. REAL/AI/GRAPHIC 경계와 화면 표기 규칙 합의
3. TopView subscription/API billing 경계가 구현 계획에 반영
4. Human Gate를 우회하는 상태 전이가 없음
5. provider 결과의 즉시 로컬 보존과 checksum 규칙 존재
6. clean plate와 overlay의 독립 재렌더 가능
7. 실제 자료의 license와 source provenance 기록 가능
8. model adapter와 공용 Visual Grammar가 분리
9. Golden Test의 pass/fail 기준이 측정 가능
10. OpenMontage canonical stage·artifact·checkpoint enum과 충돌하지 않음
11. render runtime과 composition mode가 사용자 승인 및 decision log로 잠김
12. 사용자가 Final Design v2를 명시적으로 승인

## 25. Open questions for Claude and Codex

1. VisualPlan schema가 지나치게 크거나 중복되는가?
2. Sequence와 Shot의 책임이 명확한가?
3. VisualPlan→scene_plan compiler가 정보 손실을 허용 가능한 수준으로 제한하는가?
4. HyperFrames 우선 권고와 OpenMontage의 사용자 runtime 선택 gate가 함께 작동하는가?
5. TopView API를 provider로 감쌀 때 누락된 상태나 비용 정보가 있는가?
6. Director Memory가 취향을 학습하면서 획일화를 피할 수 있는가?
7. REAL→AI 전환 표기가 시청 몰입과 윤리를 동시에 만족하는가?
8. Hyatt와 Bangjja 두 Golden Test가 전체 시스템을 충분히 압박하는가?
9. 구현 Phase가 너무 크거나 순서가 잘못되었는가?
10. 어떤 부분을 삭제해야 더 단순하면서 같은 품질을 낼 수 있는가?

## 26. Review outcome labels

각 지적은 다음 중 하나로만 분류한다.

- ACCEPT
- PARTIAL
- REJECT
- NEEDS_EVIDENCE
- BLOCKER

최종 상태:

- DESIGN_NOT_READY
- READY_FOR_IMPLEMENTATION_REVIEW

READY_FOR_IMPLEMENTATION_REVIEW는 구현 승인과 다르다. 사용자 Human Gate를 통과해야 구현을 시작한다.

## 27. Sources and evidence date

제품 기능·가격·약관은 2026-08-11 확인 기준이며 바뀔 수 있다.

- https://www.youtube.com/watch?v=APJcwbxWtfY
- https://www.newtake.com/ko
- https://www.newtake.com/ko/statement/terms-of-service
- https://www.newtake.com/ko/statement/privacy-policy
- https://www.topview.ai/
- https://www.topview.ai/canvas
- https://www.topview.ai/3d-shot-composer
- https://www.topview.ai/openapi
- https://docs.topview.ai/docs/getting-started
- https://docs.topview.ai/docs/billing-rules
- https://docs.topview.ai/docs/concurrency-and-storage
- https://www.topview.ai/pricing
- https://www.topview.ai/mcp
- https://encykorea.aks.ac.kr/Article/E0021796
- https://www.nfm.go.kr/home/subIndex/103.do
