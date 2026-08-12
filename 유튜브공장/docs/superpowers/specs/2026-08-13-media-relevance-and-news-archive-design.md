# Media Relevance Review and News Archive Design

Date: 2026-08-13  
Status: User-approved direction, written specification pending final review

## 1. Problem

The current Rana Plaza pilot collected 75 reusable files but accepted every discovered
item. The collection tool deliberately checks rights, download integrity, hashes, and
technical validity; it does not perform creative selection or event relevance review.
As a result, generic walls, unrelated earthquakes, war ruins, and generic sewing footage
appear beside potentially useful Rana Plaza material. The run also pinned only Pexels,
Pixabay Video, and Unsplash, so reusable news, archive, newspaper, and official-record
material was not searched.

The pipeline must not advance to a new proposal or script while this unreviewed pool is
presented as production-ready material.

## 2. Chosen Approach

Use a two-layer review system:

1. `media_relevance_review` immediately after collection automatically classifies and
   quarantines irrelevant or uncertain material without deleting source bytes.
2. `asset_selection` remains the later Human Gate where OpenMontage recommends exact
   assets per approved script shot.

This is preferable to manual review of all collected files because relevance can be
reduced automatically before the user sees the pool. It is preferable to metadata-only
filtering because titles and provider search results can be misleading. It is preferable
to CLIP-only filtering because visual similarity cannot establish event identity,
geography, date, or news authenticity.

## 3. Pipeline

```text
topic approval
  -> research
  -> media collection
  -> media relevance review
       - rights and file checks are inherited from collection
       - event identity and mismatch checks
       - image and sampled-video visual relevance
       - category assignment
       - coverage and shortage report
  -> targeted news and archive supplement
       - only when direct/news/official coverage is insufficient
  -> media relevance review (supplement)
  -> evidence lock
  -> proposal
  -> script
  -> visual plan
  -> animatic
  -> budget
  -> generated assets
  -> OpenMontage shot-level asset selection (Human Gate)
  -> edit
```

`media_relevance_review` does not approve creative choices and is not a Human Gate.
It determines whether an item is eligible to be proposed later. The existing
`asset_selection` Human Gate remains the only step that admits a specific item into the
edit.

## 4. Review Categories

Every collected item receives exactly one category:

- `event_direct`: verifiably depicts Rana Plaza, Savar, the collapse, warning cracks,
  rescue, survivors, or the site.
- `news_report`: reusable broadcast, news package, newspaper page, press photograph, or
  contemporaneous report whose metadata identifies the event.
- `official_record`: reusable government, court, ILO, institutional, map, diagram, report,
  hearing, or official statement material.
- `explanatory`: relevant garment work, building construction, structural failure, map,
  or contextual imagery that is not represented as event footage.
- `generic_broll`: visually usable but generic context; never presented as direct evidence.
- `unrelated`: wrong event, country, date, disaster, subject, or visual content.
- `unknown`: insufficient evidence to establish a safe category.

Default dashboard and OpenMontage candidate views show only `event_direct`,
`news_report`, `official_record`, and `explanatory`. `generic_broll`, `unrelated`, and
`unknown` remain accessible in separate filters but are excluded from automatic shot
recommendations.

## 5. Review Decision Model

The review combines independent evidence channels.

### 5.1 Metadata identity

- Event-direct and news classifications require positive event identity in provider
  metadata, archive metadata, title, description, transcript, or an authoritative linked
  record.
- A query or inherited `claim_id` is not evidence that the returned item depicts the
  claim.
- Explicit mismatches such as Ukraine, Syria, Turkey earthquake, demolition, generic
  wall, pavement, or unrelated city footage force `unrelated` unless an approved script
  later requests a clearly labelled comparison.

### 5.2 Visual relevance

- Images are evaluated directly.
- Videos use representative first, middle, last, and scene-change frames.
- Local CLIP or the existing local visual-understanding path may rank visual relevance,
  but cannot promote an item to `event_direct` or `news_report` without metadata identity.
- If an image or video requires visual confirmation and the local visual model is
  unavailable or confidence is below threshold, the item is `unknown`; it must not fail
  open into the eligible pool. A text document with authoritative identity metadata may
  be classified without a visual model, but it cannot be represented as event footage.

### 5.3 Technical quality

- Corrupt, unreadable, extremely low-resolution, watermarked, duplicate, or unusably
  short items remain rejected by collection or review.
- Valid resolution alone never makes an item relevant.

### 5.4 Decision output

Each review record contains:

```json
{
  "media_id": "MEDIA_PEXELS_12734648",
  "category": "unrelated",
  "eligibility": "excluded",
  "relevance_score": 4,
  "identity_evidence": [],
  "mismatch_evidence": ["metadata identifies war ruins in Ukraine"],
  "visual_summary": "damaged urban building",
  "review_method": ["metadata", "sampled_frames"],
  "reviewed_at": "ISO-8601 timestamp"
}
```

The canonical artifact is `artifacts/media_relevance_review.json`; the checkpoint is
`checkpoint_media_relevance_review.json`. Both bind the exact SHA-256 of the input media
manifest so stale reviews cannot be reused after collection changes.

## 6. Targeted News and Archive Collection

The supplement searches reusable material, not merely visually similar stock footage.
Priority lanes are:

1. Wikimedia Commons items with explicit per-file reusable rights.
2. Archive.org items with explicit public-domain or compatible Creative Commons rights.
3. Government and institutional collections through configured adapters, including
   NARA and Library of Congress when topically relevant.
4. Public-domain and compatible CC collections already registered in OpenMontage.
5. Configured stock sources only for explanatory or generic B-roll gaps.

The initial Rana Plaza query pack includes exact-event searches for:

- `Rana Plaza collapse 24 April 2013 Savar`
- `Rana Plaza rescue footage`
- `Rana Plaza news report 2013`
- `Rana Plaza newspaper front page`
- `Savar building collapse Bangladesh archive`
- `Rana Plaza survivors interview`
- `Rana Plaza warning cracks`
- `ILO Rana Plaza report`

Search results that require permission, purchase, subscription, editorial-only use,
unknown rights, or inaccessible originals are not downloaded. A restricted news page may
remain a research citation, but it does not enter the media library.

The supplement stops when either coverage targets are met or all eligible sources have
been exhausted. It must not fill missing news coverage with unrelated disaster footage.

## 7. Coverage Targets

Before proposal generation, the review artifact reports availability for:

- direct event exterior/site;
- warning cracks or pre-collapse condition;
- collapse aftermath and rescue;
- workers and garment-factory context;
- contemporaneous news or newspaper material;
- official investigation or institutional record;
- location map and structural explanation.

Each area is `covered`, `partial`, or `missing`, with eligible media IDs. Missing direct or
news evidence is surfaced as a production limitation, not silently replaced with generic
B-roll.

## 8. Dashboard

The 에셋 section gains the following filters and counts:

- 추천 자료
- 사건 직접
- 뉴스·보도
- 공식 기록
- 설명 자료
- 일반 B-roll
- 보류·제외

The default grid shows only recommended eligible material. Cards show the category and a
short usefulness label; source URLs and license details remain stored internally and are
not required in the normal user view. The 보류·제외 view shows the exclusion reason so
bad automatic decisions can be understood without deleting the file.

현황 gains a visible `수집 자료 검수` stage and coverage summary. Proposal approval is
not shown while review or targeted supplement collection is incomplete.

## 9. OpenMontage Contract

OpenMontage consumes only items whose review eligibility is `eligible`. It may read
`generic_broll` only when an approved VisualPlan explicitly requests generic context and
the item is clearly labelled as non-event imagery. `unrelated` and `unknown` are never
automatic candidates.

At `asset_selection`, OpenMontage presents the proposed item, alternates, category, scene
purpose, and any disclaimer such as `contextual reconstruction` or `generic B-roll`.
The user still approves the final per-shot selection once.

## 10. Existing Pilot Migration

- Preserve all 75 downloaded files and the original manifest unchanged.
- Review the existing pool first; do not redownload it.
- Expect obvious mismatches already identified in metadata, including Ukraine war ruins,
  Syria earthquake footage, unrelated earthquake destruction, generic walls, rocks,
  pavement, and unrelated bazaar imagery, to move to `unrelated` or `generic_broll`.
- Run targeted archive collection only after the first review establishes coverage gaps.
- Regenerate the proposal only after review and supplement collection settle.
- Do not approve any Human Gate during migration.

## 11. Failure and Safety Rules

- No source byte is deleted by review.
- Review failure leaves items `unknown` and blocks automatic eligibility.
- Archive source failure is recorded per source and does not promote stock substitutes.
- No Gemini call, paid call, publish action, or automatic Human Gate approval is allowed.
- Existing project history and collection checkpoints remain immutable; new checkpoints
  archive prior values through the existing transaction pattern.

## 12. Verification

Implementation is complete only when:

1. A regression fixture reproduces `75 accepted / 0 rejected` and the new review excludes
   known mismatches.
2. Query-inherited claim IDs cannot promote unrelated content.
3. Event/news categories require positive identity evidence.
4. Missing local visual analysis fails closed to `unknown`.
5. The existing 75 files remain byte-identical after migration.
6. Archive supplement uses only explicit reusable-rights items.
7. The dashboard defaults to eligible items and exposes all excluded items separately.
8. OpenMontage candidate projection excludes `unrelated` and `unknown`.
9. Proposal state remains blocked until review and supplement stages settle.
10. The full test suite, live dashboard, representative image previews, and representative
    video playback pass without browser errors.
