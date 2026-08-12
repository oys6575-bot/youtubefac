from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backlot import server as server_mod
from backlot import state as state_mod
from tests.backlot.mobile_fixtures import build_topic_gate
from tests.backlot.test_mobile_actions import payload


CONFIG = {
    "enabled": True,
    "canonical_origin": "https://factory.tail.test",
    "allowed_users": [{"login": "owner@example.com", "user_id": "123"}],
    "rate_limit_per_minute": 30,
    "max_payload_bytes": 8192,
}
IDENTITY = {"Tailscale-User-Login": "owner@example.com", "Tailscale-User-Name": "MK"}


@pytest.fixture
def mobile_client(tmp_path: Path, monkeypatch):
    root = tmp_path / "projects"
    root.mkdir()
    project, candidate_id, checkpoint_hash = build_topic_gate(root)
    monkeypatch.setattr(state_mod, "PROJECTS_DIR", root)
    monkeypatch.setattr(server_mod, "PROJECTS_DIR", root)
    monkeypatch.setattr(server_mod, "_summary_cache", {})
    monkeypatch.setattr(server_mod, "_PROJECTS_ROOT_STR", __import__("os").path.normcase(str(root.resolve())))

    async def no_watch():
        return None

    monkeypatch.setattr(server_mod, "_watch_projects", no_watch)
    with TestClient(
        server_mod.create_app(mobile_config=CONFIG),
        base_url="https://factory.tail.test",
        client=("127.0.0.1", 50000),
    ) as client:
        yield client, project, candidate_id, checkpoint_hash


def test_mobile_routes_require_allowed_tailscale_identity(mobile_client) -> None:
    client, _project, _candidate, _hash = mobile_client
    assert client.get("/api/mobile/session").status_code == 401
    assert client.get(
        "/api/mobile/session", headers={"Tailscale-User-Login": "other@example.com"}
    ).status_code == 403
    assert client.get("/api/mobile/session", headers=IDENTITY).status_code == 200


def test_dashboard_projection_is_authenticated_and_never_cached(mobile_client) -> None:
    client, _project, _candidate, checkpoint_hash = mobile_client
    response = client.get("/api/mobile/project/MOBILE_TEST/dashboard", headers=IDENTITY)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["current_gate"]["checkpoint_sha256"] == checkpoint_hash


def test_mobile_page_and_project_list_require_identity(mobile_client) -> None:
    client, _project, _candidate, _hash = mobile_client
    assert client.get("/mobile").status_code == 401
    page = client.get("/mobile/MOBILE_TEST", headers=IDENTITY)
    projects = client.get("/api/mobile/projects", headers=IDENTITY)
    assert page.status_code == 200
    assert "유튜브공장" in page.text
    assert "default-src 'self'" in page.headers["content-security-policy"]
    assert projects.status_code == 200
    assert projects.json()[0]["project_id"] == "MOBILE_TEST"


def test_manifest_and_worker_are_available_without_project_data(mobile_client) -> None:
    client, _project, _candidate, _hash = mobile_client
    manifest = client.get("/manifest.webmanifest")
    worker = client.get("/sw.js")
    assert manifest.status_code == 200
    assert manifest.json()["display"] == "standalone"
    assert worker.status_code == 200
    assert worker.headers["service-worker-allowed"] == "/"


def test_action_requires_csrf_and_exact_origin(mobile_client) -> None:
    client, _project, candidate, checkpoint_hash = mobile_client
    session = client.get("/api/mobile/session", headers=IDENTITY)
    token = session.json()["csrf_token"]
    action = payload(candidate, checkpoint_hash)

    no_csrf = client.post(
        "/api/mobile/project/MOBILE_TEST/actions", json=action, headers=IDENTITY
    )
    wrong_origin = client.post(
        "/api/mobile/project/MOBILE_TEST/actions",
        json=action,
        headers={**IDENTITY, "X-CSRF-Token": token, "Origin": "https://evil.example"},
    )
    assert no_csrf.status_code == 403
    assert wrong_origin.status_code == 403


def test_action_api_approves_once_and_stale_request_returns_409(mobile_client) -> None:
    client, project, candidate, checkpoint_hash = mobile_client
    session = client.get("/api/mobile/session", headers=IDENTITY)
    token = session.json()["csrf_token"]
    headers = {
        **IDENTITY,
        "X-CSRF-Token": token,
        "Origin": "https://factory.tail.test",
    }

    stale_action = payload(candidate, "0" * 64, idempotency_key="stale-019ff4c20001")
    stale = client.post(
        "/api/mobile/project/MOBILE_TEST/actions", json=stale_action, headers=headers
    )
    ok = client.post(
        "/api/mobile/project/MOBILE_TEST/actions",
        json=payload(candidate, checkpoint_hash),
        headers=headers,
    )

    assert stale.status_code == 409
    assert stale.json()["code"] == "stale_checkpoint"
    assert ok.status_code == 200
    assert ok.json()["receipt"]["action"] == "approve_topic"
    assert len(list((project / "approvals/receipts").glob("*.json"))) == 1


def test_project_id_mismatch_and_oversize_payload_are_rejected(mobile_client) -> None:
    client, _project, candidate, checkpoint_hash = mobile_client
    session = client.get("/api/mobile/session", headers=IDENTITY)
    token = session.json()["csrf_token"]
    headers = {**IDENTITY, "X-CSRF-Token": token, "Origin": "https://factory.tail.test"}

    mismatch = client.post(
        "/api/mobile/project/OTHER/actions",
        json=payload(candidate, checkpoint_hash),
        headers=headers,
    )
    oversize = client.post(
        "/api/mobile/project/MOBILE_TEST/actions",
        content=b"x" * 9000,
        headers={**headers, "Content-Type": "application/json"},
    )
    assert mismatch.status_code == 422
    assert oversize.status_code == 413
