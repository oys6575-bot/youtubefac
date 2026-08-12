# Rana Plaza Media Relevance Review Verification

Date: 2026-08-13 KST  
Project: `collapse-topic-pilot-2026-08-12`

## Result

PASS. The existing collection was migrated to the mandatory automatic relevance-review
contract without rewriting the original manifest or any of its 75 bound source files.
The dashboard/OpenMontage default pool now contains four positively identified direct
event images. No Human Gate was approved and no paid, Gemini, TopView, generation,
publish, or restricted-media call occurred.

## Immutable baseline

- Base manifest SHA-256:
  `c865db8190cdd1fb2e139d92870b4607ab81468000d0ff671c4ff24418daee1f`
- Base items: 75
- Hashes checked after migration: manifest plus all 75 bound files (76 paths)
- Result: all 76 baseline hashes unchanged
- Unbound files remaining in `assets/source`: 0
- Bound files missing: 0

An interrupted first archive experiment downloaded 11 results before the new
pre-download identity filter was added. None were in the final supplement manifest;
all 11 were moved to macOS Trash and remain recoverable there.

## Final review counts

| Measure | Count |
|---|---:|
| Total reviewed | 79 |
| Recommended / eligible | 4 |
| Excluded | 27 |
| Held pending identity | 48 |
| Direct event | 4 |
| Generic B-roll | 18 |
| Unrelated | 9 |
| Unknown | 48 |

Known wrong-event fixtures `MEDIA_PEXELS_12734648`, `15554614`, `15554615`,
`15650838`, `14673884`, and `17386637` are all excluded. Query text and inherited
claim labels did not promote any of them.

## Reusable exact-event supplement

The exact-event pre-download filter searched Archive.org and Wikimedia Commons.
Archive.org yielded no reusable identity-matched result. Wikimedia supplied four
files whose persistent page metadata identifies the 2013 Savar building collapse:

| Media ID | Role | License |
|---|---|---|
| `MEDIA_WIKIMEDIA_25784003` | collapse site | CC BY 2.5 |
| `MEDIA_WIKIMEDIA_25784004` | survivor / aftermath | CC BY 2.5 |
| `MEDIA_WIKIMEDIA_25801152` | site crowd | CC BY-SA 3.0 |
| `MEDIA_WIKIMEDIA_25844966` | aftermath | CC BY-SA 3.0 |

The recorded license URLs preserve the actual 2.5 and 3.0 versions. The supplement
record reports 19 discovered, four accepted unique items, and 13 rejected before
download for event-identity mismatch.

Coverage is `covered` for event site and aftermath/rescue. Warning cracks, factory
context, news/newspaper, official record, and map/structure remain explicitly
`missing`. The system did not fill these lanes with irrelevant or unusable material.

## Dashboard and production inventory

- Default dashboard filter: `recommended`
- Recommended cards: 4
- Total reviewable cards, including held/excluded filters: 79
- Default OpenMontage inventory IDs exactly match the four Wikimedia IDs above
- Normal UI exposes category, usefulness, preview, and playback, not internal rights
  or direct-download fields
- The media-review checkpoint is `completed`, machine-owned, and
  `human_approved=false`

## Verification commands

- Full suite: `1237 passed, 11 skipped, 1 subtests passed`
- JavaScript syntax: `node --check backlot/ui/mobile.js` passed
- Patch hygiene: `git diff --check` passed
- Review and supplement artifacts passed their Draft 2020-12 JSON Schemas
- Dashboard state returned 79 items, four recommended, and zero unbound/missing files
