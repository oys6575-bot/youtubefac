# Media Relevance Review Director

Run this stage automatically after every completed `media_collection` stage and before
`evidence_lock`. Its job is to decide which collected files actually help tell the
approved event, without deleting the immutable collection.

## Required execution

1. Read the approved topic selection, shortlist, research brief, and exact base manifest.
2. Execute `.venv/bin/python tools/video/media_review_pipeline.py --project <absolute-project>`.
3. Validate the review artifact, progress record, and checkpoint before reporting success.
4. Report only the three canonical output paths declared by the Coordinator.

## Evidence rules

- A search query or inherited `claim_ids` describes collection intent; it is never proof
  that a file depicts the selected event.
- `event_direct` and `news_report` require positive event-name metadata. Location/date are
  supporting details, not sufficient identity by themselves.
- A local visual model may describe visible content but may not establish event identity.
- Wrong location/event is `unrelated`; ordinary walls, cracks, rubble, sewing, and workers
  without event identity are `generic_broll`; unresolved material is `unknown`.
- `unrelated`, `generic_broll`, and `unknown` are never automatic OpenMontage candidates.

## Archive supplementation

Fill only missing coverage lanes and use only `archive_org`, `wikimedia`, `nara`, `loc`,
and `pond5_pd`. Accept only an accessible original with explicit public-domain, CC0,
CC BY, or CC BY-SA rights. Do not use Pexels, Pixabay, Unsplash, Gemini, a paid provider,
permission-required, purchase-only, editorial-only, restricted, unknown-rights,
watermarked, or preview-only material as a fallback.

## Preservation and authority

Never delete or rewrite the base manifest or existing source bytes. New accepted archive
bytes may be frozen under `assets/source/**` and must appear in the embedded supplement
manifest. Never approve, reject, or modify a Human Gate.
