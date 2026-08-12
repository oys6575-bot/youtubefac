# Rights-Cleared Media Collection Stage Design

## Objective

Insert a dedicated, observable `media_collection` stage into the YouTube Factory so
that an approved documentary topic automatically gathers as much actually usable real
media as practical before proposal and script work. Collection verifies legal and
technical usability, but makes no creative decision about which item enters the film.
OpenMontage makes that creative selection later, against the completed script and
VisualPlan, as one shot-by-shot batch.

Gemini and all generative search APIs are outside this design. No paid call is allowed.

## Binding User Decisions

1. Real photos, videos, and useful documents are first-class production inputs.
2. Collection should maximize breadth across configured and public sources.
3. Restricted, permission-required, purchase-required, unknown-rights, watermarked, or
   inaccessible-original items are not downloaded and are not preserved as candidates.
4. Collection-time filtering answers only whether an item is usable. It must not decide
   whether the item is aesthetically or narratively appropriate for the final film.
5. OpenMontage selects the final source assets later, after script and visual planning,
   and presents one consolidated shot-level selection review before editing.
6. AI reconstruction or motion graphics fill only gaps that remain after real-media
   selection. They are never a silent fallback.

## Pipeline Position

The automatic post-topic-approval path becomes:

```text
topic_approval
  -> research
  -> media_collection
  -> evidence_lock
  -> proposal (Human Gate)
```

The later production path becomes:

```text
script
  -> visual_plan
  -> animatic
  -> budget
  -> assets (generation and manual TopView candidates only)
  -> asset_selection (real + generated candidates, one consolidated Human Gate)
  -> edit
  -> compose
```

`media_collection` is deliberately separate from `research`. Research establishes what
is true and which claims matter. Media collection retrieves usable real-world files that
could illustrate those claims. Separating them keeps progress visible and makes either
stage independently retryable.

## Source Policy

### Eligible source families

- Configured stock providers: Pexels, Pixabay, and Unsplash.
- Public collections with per-item rights metadata: Wikimedia Commons and Archive.org.
- Government and institutional archives supported by the local source adapters, only
  where the individual item has an explicit reuse basis.
- User-owned local files whose ownership and intended-use declaration are recorded.

The source family is not sufficient approval by itself. Every item must pass the
per-item acceptance rules below.

### Per-item acceptance rules

An item is accepted only when all of the following are true:

- A downloadable original or sufficiently high-quality production file is available.
- Its license or public-domain basis is explicit and compatible with edited YouTube use.
- Its source page is stable enough to record.
- Required author, institution, and attribution text can be captured.
- The item is not watermarked.
- The retrieved bytes pass file-type and corruption checks.
- The item has a content checksum.

### Immediate rejection rules

The collector must not download or retain a candidate when any of these apply:

- rights status is unknown or ambiguous;
- permission, registration approval, purchase, or a separate contract is required;
- editorial-only or no-derivatives terms conflict with the intended edited documentary;
- only a thumbnail, preview, or watermarked copy is available;
- the source blocks retrieval of the usable original;
- the license metadata cannot be bound to the exact item;
- the file is corrupt or unsupported.

Rejected media URLs and thumbnails do not enter downstream artifacts. The stage may keep
aggregate rejection counts by source and reason so the dashboard can explain progress
without turning unusable material into a production candidate.

## Storage Contract

Accepted files are frozen under the canonical project directory:

```text
projects/<project-id>/
  assets/source/
    images/
    video/
    documents/
  artifacts/
    media_collection_manifest.json
  checkpoint_media_collection.json
```

The manifest contains accepted items only. Each entry includes:

- stable item ID;
- media type;
- local relative path;
- SHA-256 checksum;
- source provider and source page URL;
- direct retrieval URL when redistribution of that URL is permitted;
- creator or institution;
- license name and license URL or public-domain basis;
- attribution requirement and frozen attribution text;
- allowed use summary;
- access timestamp;
- claim IDs or research themes the item may support;
- duration or image dimensions and basic technical validation;
- duplicate relationship when the same content was encountered more than once.

The manifest does not contain a `selected_for_edit` decision. Collection and creative
selection remain separate contracts.

## Collection Behavior

1. Derive bounded multilingual search queries from verified topic names, locations,
   dates, structure names, responsible institutions, and research themes.
2. Search all currently configured eligible adapters without switching providers
   silently.
3. Inspect per-item rights metadata before downloading.
4. Reject disallowed items before any media bytes are persisted.
5. Download accepted originals into a staging path, validate them, compute SHA-256, then
   atomically move them into `assets/source/`.
6. Deduplicate exact bytes by SHA-256. Preserve one canonical file and merge legitimate
   provenance records when multiple eligible sources expose the same content.
7. Write the manifest atomically and validate it against a dedicated JSON Schema.
8. Write a canonical `media_collection` checkpoint only after manifest and file checks
   pass.

The collector is idempotent. Retrying the same project must reuse checksum-identical
files, avoid duplicate downloads, and resume unfinished source adapters without
overwriting verified files.

## Progress and Mobile Dashboard

The mobile dashboard must expose useful work activity rather than a generic spinner:

- current source being searched;
- current query or a safe human-readable summary;
- sources completed versus total;
- items discovered;
- items rights-cleared;
- files downloaded and validated;
- exact duplicates removed;
- aggregate rejection counts by reason;
- elapsed time and last successful activity;
- retry or blocker reason when progress stops.

The stage card must distinguish `searching`, `rights_check`, `downloading`, `validating`,
`deduplicating`, `completed`, and `failed`. No Human Gate is required during collection.

## Later OpenMontage Selection

After script and VisualPlan exist, OpenMontage reads the complete source manifest and
scores usable items per shot using claim relevance, temporal and geographic fidelity,
visual quality, continuity, crop tolerance, and pacing fit. It then prepares one
`asset_selection` packet containing:

- the proposed real-media choice for every shot;
- alternates where meaningful;
- a timeline or contact-sheet preview;
- provenance and attribution summaries;
- clearly marked gaps that require AI reconstruction, diagrams, maps, or typography.

The user reviews this packet once at `GATE_ASSET_SELECTION`. Only approved selections
enter the final edit. The gate does not retroactively approve rights; every presented
item is already rights-cleared by collection.

## Failure Handling

- One source failure does not discard successful results from other sources.
- Authentication failures are reported as source-specific blockers and never trigger a
  provider substitution.
- Rate limits use bounded retry and resume metadata.
- An empty result is valid only when all configured sources were attempted and the
  manifest records zero accepted files plus aggregate reasons.
- A file without complete rights metadata or a matching checksum cannot appear in the
  completed manifest.
- No AI generation, TopView operation, publishing, or paid request is permitted as a
  collection fallback.

## Existing Pilot Migration

For a project already past topic approval, deployment inserts `media_collection` after
its completed research checkpoint. If research is still running, collection waits. If
research already completed, collection is enqueued once. Existing research and evidence
artifacts are preserved. The migration is idempotent and cannot fabricate completion or
Human Gate approval.

## Acceptance Criteria

1. Pipeline and auto-dispatch contracts include `media_collection` between research and
   evidence lock.
2. A schema-valid accepted manifest references only real files that exist beneath
   `assets/source/` and whose SHA-256 values match.
3. Unknown-rights and permission-required fixtures are rejected before download and do
   not appear in the manifest.
4. A retry produces no duplicate files or duplicate manifest entries.
5. Pexels and Pixabay configured-provider fixtures produce accepted image and video
   entries without any generative or paid API call.
6. Source-adapter failure leaves prior accepted files intact and reports visible partial
   progress.
7. The mobile dashboard shows source, discovery, acceptance, download, duplicate, and
   rejection counters for the current stage.
8. The completed collection stage does not set creative selection fields or approve
   `GATE_ASSET_SELECTION`.
9. Later asset selection can consume the manifest and produce a single shot-level review
   packet without modifying source files.
10. The current pilot can resume into this stage without deleting or rewriting existing
    verified artifacts.

