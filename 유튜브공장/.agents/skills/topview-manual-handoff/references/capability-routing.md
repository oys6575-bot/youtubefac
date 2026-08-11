# Capability routing

Use the canonical inventory in `config/topview-capabilities.yaml`. Confirm every option in the live UI because model labels, prices, limits, and features can change.

## Workspace

| Need | Workspace | Reason |
|---|---|---|
| One or several ordinary image/video candidates | Board | Compare, rate, pin, group, and review outputs |
| Long or multi-scene exploration | Canvas | Agent-assisted scene and asset flow, while OpenMontage remains canonical |
| Repeatable spatial layout or camera angles | 3D Shot Composer | Stage people, props, and camera before spending generation credits |
| Alternate storyboard candidate | Film Studio / Storyboard | Explore only after the internal shot plan exists |
| Episodic fictional continuity | Drama Studio | Reserve for future dramatized series, not normal evidence documentaries |

## Task mode

| Input and control need | Mode |
|---|---|
| No source image | `TEXT_TO_VIDEO` |
| One approved source or reconstruction frame | `IMAGE_TO_VIDEO` |
| Controlled opening and closing composition | `FIRST_LAST_FRAME` |
| Character, environment, object, or style references | `MULTI_REFERENCE` |
| Existing clip needs a bounded modification | `VIDEO_EDIT` |
| Existing motion reference drives movement | `MOTION_CONTROL` |
| Spatial continuity must be staged first | `COMPOSITE_SCENE` |
| No paid video output is requested | `STORYBOARD_ONLY` |

## Model choice

Choose by required capability first, then compare two candidates when budget permits. Do not promise a family is present.

- Prefer a currently visible Seedance option for general cinematic or mixed-reference candidates.
- Prefer a currently visible Kling option when first/last frames, controlled references, or multi-shot controls are decisive.
- Consider Veo when the visible UI explicitly offers the required resolution or native audio.
- Treat Hailuo/MiniMax, Vidu, Wan, Runway, and Sora as alternatives to test against the shot need.
- Record the full label displayed in the UI; a family name alone is insufficient.

## Evidence and continuity

- Use generated footage for reconstruction, atmosphere, motion, or spatial explanation.
- Keep verified dates, numbers, quotations, maps, labels, and citations out of generated pixels.
- Bind every reference to a role: first frame, last frame, character, environment, object, style, motion, source video, or audio.
- Preserve negative space for later disclosure and typography.
- Fall back to a real still, 2.5D parallax, HyperFrames, or local LTX when continuity or budget fails.
