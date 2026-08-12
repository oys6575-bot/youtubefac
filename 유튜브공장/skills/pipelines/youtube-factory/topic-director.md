# Topic Director — YouTube Factory

## Role

Run the provider-neutral topic-search, independent-verification, and user-selection
stages before deep evidence research. This skill never approves a Human Gate.

## Mandatory read order

1. `AGENT_GUIDE.md`
2. `pipeline_defs/youtube-factory.yaml`
3. `config/topic-selection-scorecard.yaml`
4. `lib/topic_scorecard.py`
5. the artifact schema for the current stage
6. the role prompt assigned by Orca

If any input is missing, stop with a structured blocker. Do not improvise a new
scorecard or production criterion.

## Topic search

- Include only a physical whole or partial collapse of a human-made building or
  structure.
- Start with official or primary sources. News, YouTube, Reddit, GitHub, and
  Hugging Face may supplement discovery but cannot be the sole scope evidence.
- Mark every candidate and score as provisional.
- Never use generation model, platform, production cost, render time, or archive
  footage quantity as a score input.
- Save the canonical `topic_shortlist` artifact in the OpenMontage project and
  export the approved tracked comparison views under `research/topic-candidates/`.

## Handoff

The research handoff must carry:

- `source_commit`
- repository-relative `artifact_path`
- lowercase SHA-256 `artifact_sha256`

The verifier must work from that exact commit and bytes. A later edit invalidates
the verdict.

## Verification

- Independently reopen the official or primary source for each candidate.
- Check scope, collapse date, cause wording, score rationale, and source class.
- Do not fix the research artifact in place.
- Write `topic_verification` with `verdict`, `source_commit`, `input_sha256`,
  `verified_at`, and the checked source URLs.
- `PASS` requires exact commit and hash agreement and no blocking candidate finding.

## Human Gate

At `topic_approval`, write a schema-valid `topic_selection` artifact with
`selection_status: PENDING`, then checkpoint:

```text
status: awaiting_human
human_approval_required: true
human_approved: false
```

Present the shortlist and stop. Do not begin `research`, write a script, choose a
provider, generate media, or spend credits before the user chooses a topic.

