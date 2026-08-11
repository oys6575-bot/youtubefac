# Claude ↔ Codex 교차검수 Runbook

## Goal

두 모델의 합의율을 높이는 것이 아니라, 서로 다른 실패 탐지 방식을 이용해 구현 전에 blocker와 불필요한 복잡성을 제거한다.

## Rules

1. 두 독립검수는 서로의 결과를 읽기 전에 완료한다.
2. 각 finding에는 위치, 근거, 실패 방식, 최소 수정안, 검증법이 있어야 한다.
3. 제품 주장은 가능한 한 공식 문서로 재확인한다.
4. 의견 차이는 평균내지 않고 evidence와 Golden Test로 판정한다.
5. 리뷰어는 Human Gate를 승인하지 않는다.
6. 리뷰 단계에서는 구현·유료 API 호출·최종 렌더·공개를 하지 않는다.

## Files

- Claude independent: `reviews/claude-independent-review.md`
- Codex independent: `reviews/codex-independent-review.md`
- Claude on Codex: `reviews/claude-cross-review.md`
- Codex on Claude: `reviews/codex-cross-review.md`
- Final consensus: `reviews/final-consensus.md`

## Stage 1: independent review

Claude는 [`CLAUDE-INDEPENDENT-REVIEW-PROMPT.md`](CLAUDE-INDEPENDENT-REVIEW-PROMPT.md)를 사용한다.

Codex는 같은 소스 파일과 같은 finding 형식을 사용하되 Claude 결과가 생기기 전에 독립검수를 저장한다.

각 독립검수는 최소한 다음 결과를 포함한다.

- blocker/high/medium/low 개수
- JSON과 YAML 구문 검증
- 내부 Markdown 링크 검증
- schema의 positive/negative example 검증
- Hyatt Golden Test dry-run
- Bangjja Acceptance Test dry-run
- provider 결정 평가
- 제거 가능한 복잡성 5개
- 최종 verdict

## Stage 2: cross-review

각 리뷰어는 상대 finding을 다음 중 하나로 판정한다.

- `ACCEPT`: 문제와 수정안에 동의
- `PARTIAL`: 문제는 맞지만 범위 또는 수정안 조정 필요
- `REJECT`: 근거와 함께 반대
- `NEEDS_EVIDENCE`: 판정 전에 추가 근거 필요
- `BLOCKER`: 구현 전 반드시 해결

교차검수에는 새 finding을 추가할 수 있지만, ID 앞에 `CLD-X-` 또는 `CDX-X-`를 붙인다.

## Stage 3: consensus

`reviews/final-consensus.md`에 다음 표를 작성한다.

| Finding | Claude | Codex | Evidence | Final disposition | Owner | Target version |
|---|---|---|---|---|---|---|

합의 규칙:

- BLOCKER는 해결하거나 사용자가 명시적으로 위험을 수락해야 닫힌다.
- 공식 계약과 충돌하면 설계보다 공식 계약을 우선하고 설계를 수정한다.
- 경험적 품질 주장은 pilot 데이터가 없으면 가설로 낮춘다.
- 서로 다른 해법이 모두 가능하면 더 작은 계약을 우선한다.
- 결론이 불분명하면 `NEEDS_EVIDENCE`로 남기고 검증 실험을 정의한다.

## Stage 4: Design v2 candidate

합의된 수정만 새 문서 `docs/MK_VISUAL_DIRECTOR_FINAL_DESIGN_v2.md`에 반영한다. v1은 삭제하거나 덮어쓰지 않는다.

v2 candidate는 다음을 첨부한다.

- 변경 요약
- 해결한 finding ID
- 남은 위험
- schema version 변경 여부
- Golden Test 변경 여부
- 구현 Phase 1의 범위

상태는 `READY_FOR_USER_GATE`까지만 변경할 수 있다.

## Stage 5: user gate

사용자가 명시적으로 승인한 뒤에만 다음을 시작한다.

- 구현 계획
- TopView 월간 pilot 또는 API credit 구매
- 유료 generation
- 최종 렌더
- 외부 공개

승인 문구를 추론하거나 이전 대화의 일반적 동의를 새 gate 승인으로 재사용하지 않는다.

## Completion checklist

- [ ] Claude independent review exists
- [ ] Codex independent review exists
- [ ] Both cross-reviews exist
- [ ] Every BLOCKER has a final disposition
- [ ] `final-consensus.md` exists
- [ ] Design v2 candidate preserves v1
- [ ] schemas validate
- [ ] Golden Test criteria remain measurable
- [ ] Human Gate remains `awaiting_human`
