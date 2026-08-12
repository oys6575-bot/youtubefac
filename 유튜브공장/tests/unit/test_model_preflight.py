from __future__ import annotations

from pathlib import Path

from scripts.orca.model_preflight import build_preflight_report
from lib.orca_model_routing import DEFAULT_ROUTING_PATH


def test_preflight_reports_exact_model_and_never_returns_secret_values(
    tmp_path: Path,
) -> None:
    factory = tmp_path / "유튜브공장"
    factory.mkdir()
    env = factory / ".env"
    env.write_text(
        "YOUTUBE_API_KEY=super-secret-youtube\n"
        "PEXELS_API_KEY=super-secret-pexels\n",
        encoding="utf-8",
    )

    def command_probe(name: str) -> dict[str, object]:
        return {"ok": True, "detail": f"{name}-ready"}

    def model_probe(endpoint: str) -> dict[str, object]:
        assert endpoint == "http://127.0.0.1:1234/v1"
        return {
            "ok": True,
            "available_models": [
                "qwen3.6-35b-a3b-mlx",
                "gemma-4-31b-it-mlx",
            ],
            "primary_available": True,
        }

    report = build_preflight_report(
        factory,
        command_probe=command_probe,
        model_probe=model_probe,
        env_path=env,
        routing_path=DEFAULT_ROUTING_PATH,
    )

    assert report["ok"] is True
    assert report["factory_cwd"] == str(factory)
    assert report["checks"]["lm_studio"]["primary_available"] is True
    assert report["secret_status"] == {
        "YOUTUBE_API_KEY": True,
        "PEXELS_API_KEY": True,
        "PIXABAY_API_KEY": False,
        "UNSPLASH_ACCESS_KEY": False,
    }
    serialized = str(report)
    assert "super-secret-youtube" not in serialized
    assert "super-secret-pexels" not in serialized


def test_preflight_fails_when_exact_primary_model_is_missing(tmp_path: Path) -> None:
    factory = tmp_path / "유튜브공장"
    factory.mkdir()

    report = build_preflight_report(
        factory,
        command_probe=lambda name: {"ok": True, "detail": name},
        model_probe=lambda endpoint: {
            "ok": True,
            "available_models": ["some-other-model"],
            "primary_available": False,
        },
        env_path=factory / ".env",
        routing_path=DEFAULT_ROUTING_PATH,
    )

    assert report["ok"] is False
    assert report["checks"]["lm_studio"]["primary_available"] is False
