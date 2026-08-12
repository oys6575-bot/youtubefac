# Visual Technique Catalog and Micro-Reel Verification

**Date:** 2026-08-12  
**Scope:** MK Visual Director technique selection, route isolation, and one local
HyperFrames proof reel.  
**External generation:** none  
**Paid calls:** none  
**Human Gate changes:** none

## Verdict

The new technique layer is usable for production planning. OpenMontage remains the
control plane, MK Visual Director selects a small technique set, and provider-specific
instructions remain isolated. The local reel proves that three requested visual ideas
can become an authored timeline rather than a generic generation prompt.

| Check | Result | Evidence |
|---|---|---|
| Registry/schema/VisualPlan/TopView contracts | PASS | 31 tests passed |
| Registry audit | PASS | 0 findings |
| Route isolation | PASS | TopView techniques selected only with explicit `TOPVIEW_MANUAL` + on-demand opt-in |
| HyperFrames static/runtime/motion/layout | PASS | 0 errors, 0 warnings; 3 layout samples |
| Typography contrast | PASS | 21/21 text checks |
| Local MP4 render | PASS | H.264, 1920x1080, 30 fps, 9.000 s |
| Representative-frame visual review | PASS | still-to-motion, velocity display, and exact Korean typography all visible |
| Full factory test suite | PARTIAL | 1,014 passed, 10 skipped, 1 pre-existing ComfyUI inventory-count failure |

## Test 1 — Selective Technique Routing

The catalog contains 43 records:

- 25 `ACTIVE`
- 8 `ON_DEMAND`
- 5 `REFERENCE_ONLY`
- 5 `BLOCKED`

For the test sequence, the route-safe selector returned:

1. `camera.variable_velocity_push`
2. `typography.exact_fact_overlay`
3. `transition.semantic_match_cut`
4. `camera.material_macro_parallax`
5. `camera.static_evidence_hold`

For a provider-specific first/last-frame request, explicit
`TOPVIEW_MANUAL + include_on_demand` selected the two TopView techniques. The same
query under `LOCAL_LTX` selected none and recorded TopView, Higgsfield, and Seedance
records as provider-scope exclusions. A blocked scraped-prompt source remained blocked
under both routes.

## Test 2 — HyperFrames Composition QA

Command:

```bash
cd videos/visual-technique-tests
npm run check -- --snapshots --at 1.4,3.7,7.5
```

Result:

- lint: 0 errors, 0 warnings
- runtime: 0 errors, 0 warnings
- layout: 0 issues across 3 sampled frames
- motion: 0 errors, 0 warnings
- contrast: 21/21 checks passed
- snapshots: 3 PNG files written to `videos/visual-technique-tests/snapshots/`

The only informational note is deterministic substitution of Georgia/Times New Roman
with the renderer's bundled EB Garamond family. Korean sans text uses an explicit local
font declaration.

## Test 3 — Actual Render and Motion Cadence

Local artifact:

```text
.runtime/visual-tests/technique-reel.mp4
```

Media verification:

- codec: H.264
- pixel format: yuv420p
- size: 1920x1080
- frame rate: 30/1
- duration: 9.000000 seconds
- file size: 3,323,998 bytes
- SHA-256: `68737d7ffb74b78883ff907742a5191811c92bf12f959b1c59e7007f238daf6d`

Motion was also measured from two consecutive rendered frames in a background-only
320x240 crop. Mean absolute pixel delta was:

| Phase | Mean delta | Pixels changing by more than 4 |
|---|---:|---:|
| slow observation | 2.7168 | 24.90% |
| fast crossing | 14.5136 | 85.11% |
| soft landing | 5.1058 | 40.31% |

The fast phase therefore changes approximately 5.3 times more than the slow phase,
and the landing falls approximately 65% from the fast peak. This supports the intended
slow-fast-slow camera rhythm in the encoded video, not only in source code.

## Visual Review

- **Still to motion:** PASS. A controlled crop, shallow push, micro-drift, grid
  parallax, and focal ring give the still a directed point of view.
- **Velocity composition:** PASS. The camera crosses low-information space quickly
  and then settles; the lower-third curve makes the editorial intention readable in
  this test reel.
- **Photo to exact typography:** PASS. The circular image anchor expands into an
  authored field, then reveals exact Korean copy. It does not ask a video model to
  render factual text.
- **Continuity:** PASS for this nine-second proof. The brass ring becomes the visual
  anchor of the final brass rule and accent text.

This is a grammar test, not a reproduction of the referenced bangjja-yugi footage.
The source is a local city still, so material tactility, workshop lighting, hammer
rhythm, and documentary sound design still need a real craft-footage pilot.

## Full-Suite Note

The complete factory test run finished with `1014 passed, 10 skipped, 1 failed`.
The one failure is the pre-existing vendored ComfyUI inventory contract: the lock says
1,006 files while the repository currently contains and tracks 958. No file under
`vendor/comfyui/` or its contract test changed in this work. It is an inventory repair
item, not a failure of the visual-technique selector, TopView boundary, VisualPlan
wiring, or rendered proof reel.

