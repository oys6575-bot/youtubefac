# Corrected collapse topic shortlist verification — 2026-08-12

## Verdict

**PASS**

The corrected tracked shortlist passes exact-byte verification for the
`topic_verification` stage. This verdict does not select a topic, approve
`topic_approval`, or authorize deeper research, script, media, spend, push,
merge, or publish work.

## Exact input binding

- Source commit: `a5b2984184993757ec0d68e976db160caac88a93`
- Input path: `research/topic-candidates/2026-08-12-collapse-topic-shortlist.json`
- Input SHA-256: `b81d12af4557f71305c2dced638a4b0392f1e0112758c40272fd988d4d9bf3e4`
- Verified at: `2026-08-12T07:58:16Z`
- Verifier: `codex` / `gpt-5.6-sol`

The checkout was clean at the corrected source commit, and an independent
SHA-256 calculation over the exact tracked JSON bytes matched the required
digest.

## Correction audit against `7142a2f`

A recursive value comparison of the old and corrected JSON found exactly three
changes and no others:

1. `/generated_at`: `2026-08-12T07:37:20Z` → `2026-08-12T07:55:34Z`
2. `/candidates/6/score_reasons/event_pull` (Tacoma Narrows):
   `실제 붕괴 영상의 움직임이 강한 첫 장면을 만든다.` →
   `거대한 상판이 비틀리다 추락하는 사건 자체가 강렬하다.`
3. `/candidates/11/score_reasons/visual_explainability` (Quebec Bridge):
   `캔틸레버 좌굴은 설명 가능하나 원영상 자료는 제한적이다.` →
   `캔틸레버 압축부 좌굴은 정교한 단계 도식이 필요하다.`

The Tacoma replacement now scores the inherent event rather than availability
of collapse footage. The Quebec replacement now scores the engineering concept
and explanatory work required rather than scarcity of original footage. Both
are provider-neutral and independent of production capability.

All 96 raw score values are byte-for-byte unchanged. Canonical ranking also
remains unchanged:

| Rank | Candidate | Total | Status |
|---:|---|---:|---|
| 1 | Rana Plaza | 93 | PRIORITY |
| 2 | Hyatt Regency walkways | 90 | PRIORITY |
| 2 | I-35W Mississippi bridge | 90 | PRIORITY |
| 4 | FIU pedestrian bridge | 88 | PRIORITY |
| 5 | Champlain Towers South | 86 | PRIORITY |
| 5 | WTC 7 | 86 | PRIORITY |
| 7 | Tacoma Narrows Bridge | 84 | PRIORITY |
| 8 | L'Ambiance Plaza | 83 | PRIORITY |
| 9 | Quebec Bridge first collapse | 83 | PRIORITY |
| 10 | Schoharie Creek Bridge | 77 | STRONG |
| 11 | Sunshine Skyway Bridge | 76 | STRONG |
| 12 | Silver Bridge | 73 | STRONG |

## Semantic forbidden-input review

I reread every one of the 96 score reasons, not only field names. No reason now
uses generation model, production platform, production cost, render time, or
archive-footage quantity/availability as a scoring input.

The remaining Tacoma phrases involving video do not reintroduce the defect:

- `공식 역사 기록과 영상·공학 연구가 풍부하다` is evidence provenance and
  verifiability, not production-footage availability.
- `비틀림과 바람 흐름을 영상으로 직관화하기 쉽다` describes the physical
  mechanism's ability to be explained visually, not the quantity of existing
  archival footage or a provider capability.

The Korean YouTube landscape entries are the expressly approved
`korean_content_scarcity` criterion. They remain visibly provisional for all 12
candidates and do not fail this pilot.

## Reused evidence and candidate results

The completed first verification had already reopened all 12 tracked official
URLs plus four supplementary official/primary records. Per the correction
brief, this pass reused that evidence rather than repeating broad web research.
Scope, event date, official/primary source class, title/question wording, and
the evidence-based non-scarcity rationales remain unchanged and verified for
all candidates:

- PASS: `hyatt-regency-walkways`
- PASS: `champlain-towers-south`
- PASS: `fiu-pedestrian-bridge`
- PASS: `i35w-mississippi-bridge`
- PASS: `wtc-7`
- PASS: `silver-bridge`
- PASS: `tacoma-narrows-bridge`
- PASS: `sunshine-skyway-bridge`
- PASS: `lambiance-plaza`
- PASS: `schoharie-creek-bridge`
- PASS: `rana-plaza`
- PASS: `quebec-bridge-first-collapse`

## Verification commands and results

- Exact input SHA-256: PASS
- Recursive old/new JSON comparison: PASS; exactly three changed values
- `topic_shortlist` schema validation with canonical factory Python 3.11: PASS
- Old/new raw-score, total, status, and rank equality: PASS
- Recursive forbidden field-name scan: PASS
- Semantic review of all score reasons: PASS
- `python -m pytest tests/contracts/test_collapse_topic_shortlist.py -q`:
  PASS (`1 passed`)

## Limitations

- Every Korean YouTube scarcity score remains provisional pending the planned
  quantitative check; this is explicitly labeled and non-blocking.
- The prior evidence review noted that NIST published Champlain Towers South
  technical findings in June 2026. Later deep research must use the latest NIST
  state rather than treating all causal conclusions as indefinitely pending.
- This verifies topic-selection fitness only. It does not approve the Human
  Gate or establish media rights, production feasibility, or script-level
  evidence pinpoints.
