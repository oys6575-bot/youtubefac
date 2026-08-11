# Review workspace

이 폴더는 Claude와 Codex의 독립검수 및 교차검수 결과를 저장한다.

현재 저장소에는 검수 방법만 있으며, 아직 어떤 리뷰어도 최종 설계를 승인하지 않았다.

## Expected outputs

1. `claude-independent-review.md`
2. `codex-independent-review.md`
3. `claude-cross-review.md`
4. `codex-cross-review.md`
5. `final-consensus.md`

리뷰 결과는 원본 설계 파일을 직접 덮어쓰지 않는다. 합의가 끝난 뒤 별도의 Design v2 candidate를 만든다.
