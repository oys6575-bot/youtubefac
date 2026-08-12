# Media Collection Director — YouTube Factory

## Mission

Collect a broad local library of real photos, videos, and useful documents for the
approved topic. Decide legal and technical usability now; defer all creative selection
until OpenMontage can compare the finished script and VisualPlan against the full pool.

## Inputs

- `research_brief`
- `evidence_registry`
- Canonical project directory

## Required Output

- `media_collection_manifest`
- Accepted bytes beneath `assets/source/images`, `assets/source/video`, or
  `assets/source/documents`
- Live bounded progress at `automation/progress/media_collection.json`

## Method

1. Derive bounded multilingual queries from verified names, locations, dates, structure
   names, institutions, and claim themes.
2. Use only configured eligible source adapters through
   `rights_cleared_media_collection`.
3. Require the tool to evaluate item-level rights before download.
4. Reject unknown, restricted, permission-required, purchase-required, editorial-only,
   no-derivatives, watermarked, preview-only, or inaccessible-original material.
5. Freeze accepted bytes, compute SHA-256, validate basic media properties, and write the
   accepted-only manifest.
6. Update progress after each source and final validation. Report aggregate rejection
   counts, never restricted thumbnails or signed URLs.
7. Validate the manifest with `schemas.artifacts.validate_artifact` and verify every
   referenced file and checksum before checkpoint completion.

## Selection Boundary

Do not score aesthetic fit, set `selected_for_edit`, or build an edit timeline. The later
asset-selection stage presents one shot-level batch after script and visual planning.

## Forbidden

- Gemini or another generative search service
- Paid API calls
- Download before rights acceptance
- Persisting an unknown-rights or restricted candidate
- TopView, image generation, video generation, upload, or publish activity
- Fabricating Human Gate approval
