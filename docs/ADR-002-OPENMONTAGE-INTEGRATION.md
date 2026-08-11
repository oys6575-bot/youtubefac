# ADR-002: VisualPlan을 OpenMontage sidecar IR로 통합

- 상태: Accepted for design review
- 결정일: 2026-08-11
- 검토한 OpenMontage: 로컬 `main` HEAD `a9f1417ab4a9770bb6ebe24f51aa948a98aaa238`, 2026-08-11 working-tree contract
- 구현 승인: 사용자 Human Gate 대기

## Context

MK Visual Director의 shot-level 계약은 evidence, representation, camera, continuity, overlay, provider routing, fallback을 표현해야 한다. 현재 OpenMontage `scene_plan`은 scene 단위 실행 artifact이며 `additionalProperties: false`이므로 이 필드를 그대로 삽입하면 schema validation에 실패한다.

또한 OpenMontage는 다음 계약을 이미 갖는다.

- `projects/<project-id>/` canonical workspace
- `brief → script → scene_plan → asset_manifest → edit_decisions → render_report`
- stage별 `checkpoint_<stage>.json`
- checkpoint status `in_progress | awaiting_human | completed | failed`
- proposal에서 `render_runtime`과 `composition_mode` 잠금
- runtime 변경 시 사용자 승인과 append-only decision log
- post-render `final_review`

이 계약과 별개인 두 번째 orchestrator 또는 checkpoint 시스템을 만들면 Backlot 관찰성, schema 검증, 승인 보호가 깨진다.

검토 당시 로컬 OpenMontage working tree에는 이 작업과 무관한 기존 사용자 변경이 있었다. 본 ADR은 파일을 수정하지 않고 현재 `AGENT_GUIDE.md`, `pipeline_defs/hybrid.yaml`, canonical schemas를 읽어 대조한 결과다. 구현 시점에는 [upstream OpenMontage](https://github.com/calesthio/OpenMontage)의 실제 checkout과 schema를 다시 확인한다.

## Decision

VisualPlan을 OpenMontage 밖의 경쟁 source of truth가 아니라, `artifacts/visual-plan.json`에 저장되는 고해상도 planning IR로 사용한다.

deterministic compiler가 이를 OpenMontage canonical `scene_plan`으로 변환한다.

~~~text
Visual Director
  → visual-plan.json
  → schema + semantic validation
  → compiler
  → scene-plan.json
  → OpenMontage assets/edit/compose
~~~

canonical `scene_plan.metadata`에는 최소한 다음을 남긴다.

- `visual_plan_ref`
- `visual_plan_sha256`
- `visual_plan_schema_version`
- `shot_id_map`

VisualPlan 변경 후 scene plan을 수동 편집해 동기화를 맞추지 않는다. compiler를 다시 실행한다.

## Runtime boundary

HyperFrames는 주력 권고이지 자동 고정값이 아니다.

OpenMontage registry에서 HyperFrames와 Remotion이 모두 사용 가능하면 proposal에서 두 option의 brief-specific 장단점을 제시하고 사용자가 하나를 선택한다. 선택한 `render_runtime`은 `edit_decisions`까지 유지한다.

정확한 타이포·수치·도면 contract는 runtime과 분리해 유지한다.

- HyperFrames runtime: HTML/CSS/GSAP 기반으로 직접 구현
- Remotion runtime: React 구성으로 동등한 contract 구현 또는 승인된 overlay asset 사용
- FFmpeg runtime: 복잡한 모션그래픽이 없는 단순 treatment에 한정

## Human Gate boundary

Visual Director gate 이름은 OpenMontage checkpoint에 mapping한다. checkpoint enum을 확장하지 않는다.

현재 `hybrid` manifest에서 edit/compose가 자동 진행될 수 있으므로, 최종 편집 Human Gate가 필요한 MK 채널용 custom manifest 또는 approval artifact가 Phase 1의 필수 검토 대상이다.

## Consequences

### Positive

- OpenMontage Backlot과 기존 checkpoint 보호를 유지한다.
- Visual Director의 shot-level 표현력을 잃지 않는다.
- compiler 결과가 deterministic이면 LLM 교체에도 canonical scene plan이 안정된다.
- upstream OpenMontage schema를 즉시 fork하지 않아도 된다.

### Negative

- VisualPlan과 scene plan 사이에 compiler 및 mapping test가 필요하다.
- scene plan만 읽는 도구는 shot-level 세부 정보를 직접 보지 못한다.
- OpenMontage schema가 바뀌면 compiler compatibility test가 필요하다.

## Acceptance tests

1. valid VisualPlan이 current OpenMontage `scene_plan` schema를 통과하는 artifact로 변환된다.
2. 모든 source shot_id가 결과 scene_id 또는 metadata map에 존재한다.
3. VisualPlan checksum이 바뀌면 stale scene plan을 검출한다.
4. checkpoint status는 OpenMontage enum 밖의 값을 쓰지 않는다.
5. render runtime 무단 변경을 검출한다.
6. final-edit gate를 강제하지 못하는 기존 manifest는 production-ready로 판정하지 않는다.

## Revisit triggers

- OpenMontage가 shot-level extension schema 또는 first-class VisualPlan artifact를 채택
- compiler의 정보 손실이 Golden Test를 반복적으로 실패시킴
- custom manifest 유지 비용이 upstream 호환성 이익보다 커짐

## Amendments (2026-08-11, cross-review 반영)

`reviews/final-consensus.md` 합의에 따른 수정.

1. **CLD-001 (PARTIAL) — 기준선을 contract lock으로 고정**: 본문이 인용한 로컬 HEAD `a9f1417…`은 upstream에 존재하지 않아 제3자가 재현할 수 없다. 교차검수에서 compiler가 의존하는 세 파일(`scene_plan.schema.json`, `checkpoint.schema.json`, `hybrid.yaml`)이 공개 upstream 커밋 `4eab34c5cfcccaa4f1970554928feccce73ee930`과 blob·SHA-256 동일함을 양측이 검증했다. 기준선은 [`vendor/openmontage/contract-lock.json`](../vendor/openmontage/contract-lock.json)으로 고정한다. "구현 시점에 다시 확인한다"는 절차는 lock 검증 명령 실행으로 대체하며, 불일치 시 변경 파일을 재검토하기 전까지 compiler·gate 작업을 진행하지 않는다. upstream이 AGPL-3.0이므로 전체 사본 vendoring은 오프라인 CI가 실제로 필요해질 때만 한다.
2. **CLD-004 / CDX-003 — compiler 검증은 loss-accounting**: round-trip이 아니라 필드 단위 배정표로 검증한다. 모든 VisualPlan 필드는 `scene field로 컴파일 | metadata로 이관 | QC가 visual-plan 직접 소비 | 정당화된 drop` 중 하나의 소비처를 가져야 하며, disclosure·evidence·overlay는 drop 금지 집합이다. representation→scene type 매핑은 Design v2 §5.1의 표를 따른다.
3. **CLD-007 — 편집 이후 권위 순서**: 컷·타이밍·runtime의 최종 권위는 `edit_decisions`다. VisualPlan의 편집 필드는 GATE_ANIMATIC까지의 계획 가설이며, 이후 차이는 자동 역수정 없이 `{planned, actual, reason, actor, decided_at}` divergence report로 기록한다.
