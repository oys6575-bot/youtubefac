# Visual Technique Micro-Reel

Nine-second local HyperFrames proof for three direction decisions:

1. still image to restrained camera motion;
2. slow-fast-slow velocity with a readable landing;
3. a circular photo anchor morphing into exact authored typography.

Run from this directory:

```bash
npm run check -- --snapshots --at 1.4,3.7,7.5
npm run render -- --quality draft --fps 30 --workers 4 --output ../../.runtime/visual-tests/technique-reel.mp4
```

The MP4 is intentionally kept under the ignored `.runtime/` tree. Source,
motion assertions, provenance, and repeatable commands stay in Git.

Recorded results and the known full-suite baseline issue are documented in
`../../docs/verification/2026-08-12-visual-technique-tests.md`.
