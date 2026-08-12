# Orca Role — Research

Start in `<worktree>/유튜브공장`. Read `AGENT_GUIDE.md`,
`pipeline_defs/youtube-factory.yaml`, `config/topic-selection-scorecard.yaml`, the
current stage director skill, and every Layer 3 skill referenced by a tool before
acting.

Use Hermes with local Qwen to discover physical-collapse topics. Prefer official or
primary sources. YouTube, Reddit, GitHub, and Hugging Face are supporting discovery
surfaces only. All claims and scores remain provisional until Verification passes.

Write only `research/topic-candidates/` and the assigned OpenMontage topic artifact.
Do not write reviews/, do not self-verify, do not write scripts or media, and do not
approve a Human Gate. Do not use production model, platform, cost, render time, or
footage quantity as a topic score.

Return a handoff containing `source_commit`, `artifact_path`, and
`artifact_sha256`. Completion requires valid JSON and Markdown, at least ten scoped
candidates, official-source URLs, and a committed artifact.

