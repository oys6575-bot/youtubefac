from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROMPT_ROOT = ROOT / "orchestration" / "prompts"


def test_all_role_prompts_lock_factory_cwd_and_rule_zero() -> None:
    roles = {
        "control",
        "research",
        "verification",
        "story-visual",
        "production",
        "qa",
    }
    assert {path.stem for path in PROMPT_ROOT.glob("*.md")} == roles

    for role in roles:
        text = (PROMPT_ROOT / f"{role}.md").read_text(encoding="utf-8")
        assert "<worktree>/유튜브공장" in text
        assert "AGENT_GUIDE.md" in text
        assert "pipeline_defs/youtube-factory.yaml" in text
        assert "stage director skill" in text
        assert "Layer 3" in text
        assert "Human Gate" in text
        assert "Do not" in text


def test_research_and_verification_have_disjoint_write_ownership() -> None:
    research = (PROMPT_ROOT / "research.md").read_text(encoding="utf-8")
    verification = (PROMPT_ROOT / "verification.md").read_text(encoding="utf-8")

    assert "research/topic-candidates/" in research
    assert "Do not write reviews/" in research
    assert "reviews/" in verification
    assert "Do not edit research/topic-candidates/" in verification
    for field in ("source_commit", "artifact_path", "artifact_sha256"):
        assert field in research
        assert field in verification


def test_visual_role_owns_direction_but_not_facts() -> None:
    text = (PROMPT_ROOT / "story-visual.md").read_text(encoding="utf-8")
    for phrase in (
        "Visual Grammar",
        "Sequence",
        "Shot",
        "camera",
        "speed curve",
        "photo-to-video",
        "typography",
        "motion graphics",
        "Do not change verified facts",
    ):
        assert phrase in text

