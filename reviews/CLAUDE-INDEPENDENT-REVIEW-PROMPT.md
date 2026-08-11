# Claude 독립검수 프롬프트

아래 내용을 Claude Code의 새 세션에 그대로 전달한다. Codex의 해설이나 결론을 먼저 추가하지 않는다.

---

당신은 MK Visual Director 최종 설계의 독립 아키텍처 리뷰어입니다.

저장소 전체를 읽되, 다음 순서를 지키십시오.

1. `docs/MK_VISUAL_DIRECTOR_FINAL_DESIGN_v1.md`
2. `schemas/visual-plan.schema.json`
3. `schemas/source-registry.schema.json`
4. `config/visual-grammars/HERITAGE_FORGE.yaml`
5. `golden-tests/HYATT-60-90S-GOLDEN-SEQUENCE.md`
6. `golden-tests/BANGJJA-STYLE-ACCEPTANCE-TEST.md`
7. `docs/ADR-001-TOPVIEW-PRIMARY-PROVIDER.md`
8. `docs/ADR-002-OPENMONTAGE-INTEGRATION.md`
9. `docs/REFERENCE-BANGJJA-NEWTake-ANALYSIS.md`

목표는 동의가 아니라 반증입니다. 구현하거나 provider API를 호출하지 마십시오. 제품 기능·가격·API처럼 변할 수 있는 주장을 검토할 때는 공식 출처를 우선해 현재 상태를 재확인하고, 확인하지 못한 것은 `NEEDS_EVIDENCE`로 표시하십시오.

다음을 집중 검수하십시오.

- 요구사항에서 아키텍처로의 추적 가능성
- Sequence, Shot, Visual Grammar의 책임 중복 또는 공백
- JSON Schema의 모순, 과잉 제약, 누락, 실제 검증 가능성
- REAL, AI_RECONSTRUCTION, GRAPHIC, HYBRID 경계와 공개 원칙
- Source Registry, Claim Ledger, rights 기록의 충분성
- LLM adapter와 공용 연출 규칙의 분리
- TopView Canvas/API, HyperFrames, OpenMontage, local LTX의 책임 경계
- 비동기 task, 비용, 실패, 재시도, 다운로드, checksum 계약
- Human Gate를 우회할 수 있는 상태 전이
- Golden Test가 실제 pass/fail을 재현 가능하게 만드는지
- 불필요한 복잡성과 먼저 삭제해야 할 구성
- 60–90초 pilot 전에 반드시 해결할 blocker

모든 지적은 아래 형식을 사용하십시오.

~~~text
ID: CLD-001
Severity: BLOCKER | HIGH | MEDIUM | LOW
Disposition: ACCEPT | PARTIAL | REJECT | NEEDS_EVIDENCE | BLOCKER
Location: file:line or section
Claim: 무엇이 문제인가
Evidence: 문서 또는 공식 외부 근거
Failure mode: 방치할 때 실제로 어떻게 실패하는가
Minimal change: 가장 작은 수정안
Verification: 수정 후 무엇으로 확인하는가
~~~

결과 문서는 `reviews/claude-independent-review.md`에 저장하십시오. 마지막에 반드시 포함할 것:

1. Strengths worth preserving
2. Findings ordered by severity
3. Schema validation findings
4. Golden Test dry-run table
5. TopView decision: keep, revise, or reverse
6. Five simplifications
7. Open questions for Codex
8. Final verdict: `DESIGN_NOT_READY` 또는 `READY_FOR_IMPLEMENTATION_REVIEW`

`READY_FOR_IMPLEMENTATION_REVIEW`는 구현 승인이나 유료 호출 승인이 아닙니다. 사용자의 Human Gate를 변경하거나 승인된 것으로 기록하지 마십시오.

검수가 끝나면 수정한 파일 목록과 검증 명령 결과를 함께 보고하십시오. 설계 자체는 수정하지 말고 리뷰 파일만 추가하십시오.

---
