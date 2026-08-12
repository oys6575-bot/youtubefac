from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "backlot/ui"


def test_pwa_manifest_is_installable_and_has_required_icons() -> None:
    manifest = json.loads((UI / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert manifest["name"] == "유튜브공장"
    assert manifest["display"] == "standalone"
    assert manifest["start_url"] == "/mobile"
    sizes = {icon["sizes"] for icon in manifest["icons"]}
    assert {"192x192", "512x512"} <= sizes
    for icon in manifest["icons"]:
        assert (UI / icon["src"].removeprefix("/ui/")).is_file()


def test_service_worker_caches_shell_only_and_never_approval_data() -> None:
    worker = (UI / "sw.js").read_text(encoding="utf-8")
    assert "APP_SHELL" in worker
    assert 'startsWith("/api/")' in worker
    assert 'cache: "no-store"' in worker
    assert "approval" not in worker.lower()
    assert "receipt" not in worker.lower()
    assert "checkpoint" not in worker.lower()
    assert "backgroundSync" not in worker


def test_mobile_ui_has_eight_sections_two_step_gates_and_no_offline_queue() -> None:
    html = (UI / "mobile.html").read_text(encoding="utf-8")
    css = (UI / "mobile.css").read_text(encoding="utf-8")
    script = (UI / "mobile.js").read_text(encoding="utf-8")
    for label in (
        "제작 현황", "주제 후보", "자료·출처", "대본·VisualPlan",
        "에셋·TopView", "편집·렌더", "검수 보고서", "모델·도구",
    ):
        assert label in html
    for stage in ("budget", "asset_selection", "final_review", "title_thumbnail", "publish"):
        assert stage in script
    assert "navigator.onLine" in script
    assert "localStorage" not in script
    assert "sessionStorage" not in script
    assert "indexedDB" not in script
    assert "CONFIRM" in script
    assert "min-height: 44px" in css
    assert "@media (max-width: 760px)" in css
    assert ".bottom-nav" in css
    assert ".role-status { color: #6f7d8f; text-align: right; overflow: hidden;" in css


def test_ui_never_contains_publish_or_shell_execution_endpoint() -> None:
    script = (UI / "mobile.js").read_text(encoding="utf-8")
    assert "/publish" not in script
    assert "/shell" not in script
    assert "/orca" not in script
    assert "/actions" in script


def test_mobile_decision_dialog_close_controls_do_not_submit_the_form() -> None:
    html = (UI / "mobile.html").read_text(encoding="utf-8")
    script = (UI / "mobile.js").read_text(encoding="utf-8")

    assert html.count('type="button" data-dialog-close') == 2
    assert "function closeDecision()" in script
    assert 'querySelectorAll("[data-dialog-close]")' in script
    assert 'button.addEventListener("click", closeDecision)' in script


def test_mobile_ui_projects_automation_and_only_exposes_allowlisted_retry() -> None:
    html = (UI / "mobile.html").read_text(encoding="utf-8")
    script = (UI / "mobile.js").read_text(encoding="utf-8")

    assert 'id="automation-card"' in html
    assert 'id="automation-label"' in html
    assert "retry_auto_dispatch" in script
    assert "expected_job_sha256" in script
    assert "자료조사 실행 중" in script
    assert "/shell" not in script
    assert "/orca" not in script
