# Rights-Cleared Media Collection Verification

Date: 2026-08-12 (Asia/Seoul)

## Verdict

PASS for the new pipeline contract and future approved-topic runs.

The automatic pre-proposal sequence is now:

`research -> media_collection -> evidence_lock -> proposal -> awaiting_human`

`media_collection` downloads only candidates that pass the explicit reusable-rights
policy. It does not perform creative selection. Shot-level selection remains one later
OpenMontage asset-selection gate after the script and VisualPlan exist.

## Verified safety properties

- Gemini, paid calls, TopView API dispatch, generated assets, render, upload, and publish
  remain outside this automatic chain.
- Permission-required, purchase-required, restricted/editorial-only, unknown-rights,
  watermarked, preview-only, and inaccessible-original candidates are rejected before
  download.
- Accepted bytes are written only below `assets/source/` and are bound by SHA-256 and
  size in `media_collection_manifest.json`.
- Retry is checksum-idempotent. Identical bytes are frozen once and may be referenced by
  more than one accepted source record.
- A missing, changed, escaped, or hash-mismatched source file fails the Coordinator
  integrity check.
- The checkpoint embeds the exact manifest object. It cannot mark a Human Gate approved.
- The live progress projection validates a bounded schema and omits API keys, signed
  URLs, and raw exception payloads.
- The Obsidian vault contains the new tool card and audits without drift.

## Test evidence

1. Focused pipeline and dashboard verification:

   `PYTHONPATH=. .venv/bin/pytest tests/contracts/test_media_collection_contract.py tests/contracts/test_youtube_factory_pipeline.py tests/contracts/test_orca_model_routing.py tests/backlot -q`

   Result: `140 passed, 1 skipped`.

2. Full contract suite:

   `PYTHONPATH=. .venv/bin/pytest tests/contracts -q`

   Result: `759 passed, 7 skipped`.

3. Full repository regression suite:

   `PYTHONPATH=. .venv/bin/pytest -p no:terminal`

   Result: exit code `0`.

4. UI and generated knowledge verification:

   - `node --check backlot/ui/mobile.js` -> PASS
   - `PYTHONPATH=. .venv/bin/python scripts/knowledge-vault.py audit` ->
     `{"ok": true, "findings": []}`
   - `git diff --check` -> PASS

5. Integration fixture:

   `test_collection_integration_freezes_only_usable_media_and_embeds_manifest`
   proves accepted, rejected, duplicate, and failed-source behavior in one run, including
   checkpoint embedding and recomputed source-file hashes.

## Existing pilot decision

The current `collapse-topic-pilot-2026-08-12` job completed the old three-stage sequence
before this feature existed and is already at `proposal / awaiting_human`. Its newest job
remains readable and unchanged. It is not silently rewritten or reactivated, because
doing so would alter historical receipts and make the already-produced proposal appear
to have used media it never saw.

Verified live projection:

- job: `52a86cd7-8a57-46b2-a6e7-34b59f2e2f7e`
- state: `awaiting_human`
- current stage: `proposal`
- label: `기획안 승인 대기`
- collection progress: absent, as expected for a pre-feature job

Legacy three-stage jobs are accepted only as terminal history. They cannot be claimed by
the new Coordinator. A failed legacy job may be retried into the four-stage contract only
when its settled results are a valid new-order prefix; otherwise migration fails closed.
New topic approvals always create the four-stage job.

## Known boundary

This verification used deterministic fake-source fixtures and did not make a live stock
provider call. Provider availability and search yield depend on the configured Pexels,
Pixabay, and Unsplash keys at runtime. A provider failure produces a partial manifest and
preserves successful sources; it does not admit unknown-rights media.
