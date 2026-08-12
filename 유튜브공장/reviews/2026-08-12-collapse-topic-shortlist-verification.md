# Collapse topic shortlist verification — 2026-08-12

## Verdict

**FAIL**

The exact tracked bytes are not suitable to advance to `topic_approval` because
two score reasons use archive-footage availability, which the approved
scorecard forbids as an input. This verdict does not repair the shortlist,
select a topic, approve the Human Gate, or authorize deeper research, script,
media, spend, publish, merge, or push action.

## Exact input binding

- Source commit: `7142a2f003563308c30acce937ab0b35667d3675`
- Input path: `research/topic-candidates/2026-08-12-collapse-topic-shortlist.json`
- Input SHA-256: `2928f8d1781c8600814549a2419eaac210294ef3cf9da9c342fbb99b4b3ff627`
- Verified at: `2026-08-12T07:49:49Z`
- Verifier: `codex` / `gpt-5.6-sol`

The repository entered verification clean at the bound commit. Independent
SHA-256 calculation over the tracked JSON bytes matched the required digest.
The canonical shared `topic_shortlist.json` also had the same digest.

## Verification method

I reread the pipeline manifest, verification prompt, scorecard, both artifact
schemas, deterministic scoring implementation, and the tracked JSON/Markdown
views. I reopened every listed official source and used supplementary official
records where a landing page was too thin to assess the question or causal
rationale. For every candidate I checked physical-collapse scope, event date,
source class, title/question wording, all eight raw scores and their reasons,
the deterministic total/rank, and forbidden production inputs, including
semantic uses that are not encoded under a forbidden field name.

Score vectors below use this fixed order:
`event_pull / causal_depth / belief_reversal / evidence_verifiability /
narrative_expandability / visual_explainability / meaning_and_lessons /
korean_content_scarcity`.

## Candidate results

| Rank | Candidate | Raw scores | Total | Result | Verification note |
|---:|---|---|---:|---|---|
| 1 | Rana Plaza | `5/5/4/5/5/4/5/3` | 93 | PASS | ILO records the 24 Apr 2013 building collapse and five garment factories; an ILO-hosted research chapter supports the prior-day cracks, evacuation, worker return, and supply-chain/worker-choice framing. Whole physical collapse and wording are supportable. |
| 2 | Hyatt Regency walkways | `4/5/4/5/4/5/5/3` | 90 | PASS | NIST records the 17 Jul 1981 collapse and the second/fourth-floor suspended-walkway load path; the official investigation supports the connection-capacity and design-review narrative. Partial structural collapse is correctly classified. |
| 2 | I-35W Mississippi bridge | `4/5/4/5/4/5/5/3` | 90 | PASS | NTSB records the 1 Aug 2007 main-span collapse, undersized U10 gusset plates, accumulated weight, construction loading, and review/inspection failures. The question and all non-scarcity reasons are evidence-aligned. |
| 4 | FIU pedestrian bridge | `4/5/4/5/3/5/4/4` | 88 | PASS | NTSB records the 15 Mar 2018 span collapse, design-calculation and peer-review errors, severe cracking, continued work, and open traffic lanes. The question and causal-depth rationale are directly supported. |
| 5 | Champlain Towers South | `5/4/4/4/5/4/5/4` | 86 | PASS | NIST records the sudden partial collapse of the 12-floor condominium on 24 Jun 2021. NIST published technical findings in Jun 2026, so the shortlist's caution about an ongoing investigation is conservative rather than a reason to reject the candidate; final-script work must use the latest NIST state. |
| 5 | WTC 7 | `5/4/5/4/5/4/4/2` | 86 | PASS | NIST's final report covers the 11 Sep 2001 whole-building collapse and the fire/debris-driven progressive sequence. The no-aircraft-impact question is accurate, while the score reason correctly warns that unsupported controversy must be separated from NIST evidence. |
| 7 | Tacoma Narrows Bridge | `5/3/4/5/4/5/5/2` | 84 | FAIL | Scope, date, source, and engineering framing are supportable, but `event_pull` is justified with “실제 붕괴 영상의 움직임이 강한 첫 장면을 만든다.” This uses availability/content of archival collapse footage as a scoring input, forbidden by `archive_footage_quantity`. |
| 8 | L'Ambiance Plaza | `4/4/3/5/4/5/4/4` | 83 | PASS | OSHA records the 23 Apr 1987 lift-slab construction collapse and 28 deaths; the supplementary NIST investigation identifies loss of jack support and progressive slab failure. Whole-building scope and the lift-slab question are supportable. |
| 9 | Quebec Bridge first collapse | `4/5/4/4/4/3/5/4` | 83 | FAIL | Scope, date, source, first-collapse title, and warning question are supportable, but `visual_explainability` is justified partly with “원영상 자료는 제한적이다.” This penalizes the candidate for archival-footage availability, forbidden by `archive_footage_quantity`. |
| 10 | Schoharie Creek Bridge | `3/4/3/5/3/4/5/4` | 77 | PASS | NTSB records the 5 Apr 1987 pier and multi-span collapse and attributes it to lost riprap, severe erosion below spread footings, inspection weakness, and low redundancy. The hidden-riverbed question and scour explanation are directly supported. |
| 11 | Sunshine Skyway Bridge | `3/4/3/5/3/4/4/4` | 76 | PASS | NTSB records the 9 May 1980 vessel collision, destroyed pier, and fall of about 1,297 feet of deck/superstructure, with severe weather, navigation loss, missing pier protection, and missing motorist warning as causal/contributing factors. |
| 12 | Silver Bridge | `3/4/3/4/3/4/5/4` | 73 | PASS | NTSB records the 15 Dec 1967 whole-bridge collapse from an inaccessible eyebar flaw produced by stress corrosion and corrosion fatigue, followed by rapid chain/span/tower collapse. The crack, inspection, and redundancy framing is supportable. |

All 12 candidates retain `provisional: true`. Every Korean YouTube scarcity
assessment explicitly says that follow-up quantitative checking is required;
those scarcity scores are therefore treated as provisional and do not fail
this pilot.

## Deterministic scoring and contract checks

- Canonical scoring reproduced totals/ranks exactly: `93, 90, 90, 88, 86,
  86, 84, 83, 83, 77, 76, 73`, with shared ranks only where the configured
  total/evidence/causal/event tie tuple is identical.
- Statuses reproduce as nine `PRIORITY` and three `STRONG`; no candidate is
  `UNASSESSED`, `OUT_OF_SCOPE`, or on the evidence hold.
- No forbidden field name appears, but two score reasons semantically use the
  forbidden `archive_footage_quantity` input. Tacoma's `event_pull` rewards
  actual collapse footage; Quebec's `visual_explainability` penalizes limited
  original footage. Either defect blocks `PASS` for these exact bytes.
- The tracked Markdown is a shortened presentation view; its title/question
  paraphrases preserve the JSON meaning and its displayed totals/ranks match
  the deterministic machine result.
- Schema validation and the focused shortlist contract passed under the
  canonical factory Python 3.11 environment.

## Reopened official and primary URLs

Tracked shortlist URLs:

1. <https://www.nist.gov/el/walkway-collapse-kansas-city-missouri-1981>
2. <https://www.nist.gov/disaster-and-failure-studies/champlain-towers-south-collapse>
3. <https://www.ntsb.gov/investigations/pages/hwy18mh009.aspx>
4. <https://www.ntsb.gov/investigations/Pages/HWY07MH024.aspx>
5. <https://www.nist.gov/publications/final-report-collapse-world-trade-center-building-7-federal-building-and-fire-safety-0>
6. <https://www.ntsb.gov/investigations/Pages/80267.aspx>
7. <https://wsdot.wa.gov/TNBhistory/collapse.htm>
8. <https://www.ntsb.gov/investigations/Pages/DCA80AM050.aspx>
9. <https://www.osha.gov/enforcement/directives/std-03-15-003>
10. <https://www.ntsb.gov/investigations/Pages/DCA87MH005.aspx>
11. <https://www.ilo.org/resource/statement/employment-injury-insurance-bangladesh-bridging-social-security-cases>
12. <https://www.canada.ca/en/housing-infrastructure-communities/news/2019/08/the-history-of-the-quebec-bridge.html>

Supplementary official/primary records used to check causal or question wording:

13. <https://www.nist.gov/publications/investigation-kansas-city-hyatt-regency-walkways-collapse-nbs-bss-143>
14. <https://www.nist.gov/publications/investigation-lambiance-plaza-building-collapse-bridgeport-connecticut-nbs-ir-87-3640>
15. <https://researchrepository.ilo.org/esploro/fulltext/bookChapter/Women-workers-during-global-value-chain/995633407702676?institution=41ILO_INST&mId=13135257220002676&repId=12135257300002676>
16. <https://publications.gc.ca/collections/collection_2016/bcp-pco/Z1-1907-5-1-1-eng.pdf>

## Findings and limitations

1. **Blocking:** Tacoma Narrows `event_pull` uses actual collapse-video
   availability as a scoring reason, violating the forbidden-input rule for
   `archive_footage_quantity`.
2. **Blocking:** Quebec Bridge `visual_explainability` uses limited original
   footage availability as a scoring reason, violating the same rule.
3. Korean YouTube scarcity is not quantitatively verified. The shortlist labels
   every scarcity assessment as provisional, so this is a visible downstream
   task rather than a blocking defect.
4. NIST released Champlain Towers South technical findings in June 2026. Deep
   research must refresh the shortlist's still-cautious wording and must not
   imply that no technical conclusion exists.
5. Several artifact `sources[].title` values are descriptive labels rather than
   byte-for-byte copies of the live page heading. The institutions, URLs,
   source classes, event identity, date, and claimed support remain correct.
6. Some landing pages are intentionally high-level. The supplementary records
   above were needed to assess causal/question wording for Hyatt, L'Ambiance,
   Rana Plaza, and Quebec Bridge. A later evidence registry must still bind
   script-level claims to precise primary pinpoints.
7. This verification audits topic-selection fitness only. It does not establish
   media rights, footage availability, production cost, or final-script factual
   sufficiency. The two forbidden archival-footage influences above are the
   reason for the exact-byte `FAIL`.
