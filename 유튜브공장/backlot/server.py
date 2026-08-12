"""Backlot server — FastAPI app: board state API, SSE change feed, media.

The watcher observes ``projects/`` with watchfiles; on any change it bumps a
per-project version and wakes SSE subscribers, who tell the browser to
refetch state. The server never writes to project directories.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import time
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backlot.state import PROJECTS_DIR, REPO_ROOT, list_projects, load_board_state, summarize_project

UI_DIR = Path(__file__).resolve().parent / "ui"
THUMB_CACHE_DIR = REPO_ROOT / ".backlot" / "thumbs"
THUMB_WIDTHS = (320, 640, 960)
FFMPEG_CANDIDATES = (
    Path("/opt/homebrew/bin/ffmpeg"),
    Path("/usr/local/bin/ffmpeg"),
)

# Paths inside a project whose changes are pure noise for the board.
_IGNORE_PARTS = {"node_modules", ".git", "__pycache__", ".cache"}

SSE_HEARTBEAT_SECONDS = 15


def _ui_html(name: str, assets: tuple[str, ...]) -> HTMLResponse:
    html = (UI_DIR / name).read_text(encoding="utf-8")
    for asset in assets:
        path = UI_DIR / asset
        if path.is_file():
            version = str(int(path.stat().st_mtime))
            html = html.replace(f"/ui/{asset}", f"/ui/{asset}?v={version}")
    return HTMLResponse(html)


class ChangeHub:
    """Fan-out of project-change notifications to SSE subscribers.

    Subscriptions are filtered: a board subscribed to one project only ever
    receives that project's ids, so unrelated-project bursts can't flood its
    queue and starve out the one notification it actually needs.
    """

    def __init__(self) -> None:
        self._subscribers: dict[asyncio.Queue, Optional[str]] = {}

    def subscribe(self, project_id: Optional[str] = None) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=64)
        self._subscribers[q] = project_id
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        self._subscribers.pop(q, None)

    def publish(self, project_id: str) -> None:
        for q, only in list(self._subscribers.items()):
            if only is not None and only != project_id:
                continue
            try:
                q.put_nowait(project_id)
            except asyncio.QueueFull:
                # Queue holds only THIS subscriber's relevant ids, so a full
                # queue already guarantees a pending wake-up → safe to drop.
                pass


hub = ChangeHub()

# Library summaries are expensive to derive (full state parse per project);
# cache per project and invalidate from the watcher.
_summary_cache: dict[str, dict] = {}


def _invalidate_summary(project_id: str) -> None:
    _summary_cache.pop(project_id, None)


def _cached_summaries() -> list[dict]:
    if not PROJECTS_DIR.is_dir():
        return []
    summaries = []
    for entry in sorted(PROJECTS_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith(("_", ".")):
            continue
        cached = _summary_cache.get(entry.name)
        if cached is None:
            try:
                cached = summarize_project(entry)
            except Exception:
                cached = {
                    "project_id": entry.name, "title": entry.name,
                    "pipeline_type": "unknown", "has_pipeline_state": False,
                    "poster": None, "live": False, "last_activity": 0,
                    "active_stage": None, "awaiting_human": False,
                    "stage_states": [], "completed_count": 0,
                    "render_count": 0, "scene_count": 0, "error": "unreadable",
                }
            _summary_cache[entry.name] = cached
        summaries.append(cached)
    summaries.sort(key=lambda s: (not s["live"], -(s["last_activity"] or 0)))
    return summaries


# Watch-loop hot path: pure string comparison, no per-path filesystem calls
# (change batches can be thousands of paths during a render).
import os as _os

_PROJECTS_ROOT_STR = _os.path.normcase(str(PROJECTS_DIR.resolve()))


def _project_of_change(path_str: str) -> Optional[str]:
    """Map a changed filesystem path to a project id (None = irrelevant)."""
    norm = _os.path.normcase(_os.path.normpath(path_str))
    if not norm.startswith(_PROJECTS_ROOT_STR):
        return None
    rel = norm[len(_PROJECTS_ROOT_STR):].lstrip("\\/")
    if not rel:
        return None
    parts = rel.replace("\\", "/").split("/")
    if _IGNORE_PARTS.intersection(parts):
        return None
    return parts[0]


async def _watch_projects() -> None:
    """Background task: watch projects/ and publish debounced changes."""
    try:
        from watchfiles import awatch
    except ImportError:
        return  # watcher unavailable → board still works via manual refresh
    if not PROJECTS_DIR.is_dir():
        return
    async for changes in awatch(PROJECTS_DIR, recursive=True, step=400):
        touched: set[str] = set()
        for _change, path_str in changes:
            pid = _project_of_change(path_str)
            if pid:
                touched.add(pid)
        for pid in touched:
            _invalidate_summary(pid)
            hub.publish(pid)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Own and cleanly stop the project watcher with FastAPI's lifespan API."""

    task = asyncio.create_task(_watch_projects())
    app.state.watch_task = task
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


def create_app(*, mobile_config: Optional[dict] = None) -> FastAPI:
    app = FastAPI(title="Backlot", docs_url=None, redoc_url=None, lifespan=_lifespan)
    from backlot.mobile_security import MobileAuthError, MobileSecurity, load_mobile_config

    mobile_security = MobileSecurity(mobile_config if mobile_config is not None else load_mobile_config())
    app.state.mobile_security = mobile_security

    def _mobile_actor(request: Request):
        client_host = request.client.host if request.client else None
        return mobile_security.authenticate(
            client_host, request.headers.get("Tailscale-User-Login")
        )

    def _auth_error(exc: MobileAuthError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"ok": False, "code": exc.code},
            headers={"Cache-Control": "no-store"},
        )

    # ---- API ----------------------------------------------------------

    @app.get("/api/health")
    async def health() -> dict:
        return {"ok": True, "app": "backlot"}

    # ---- Mobile Human Gate API ---------------------------------------

    @app.get("/api/mobile/session")
    async def mobile_session(request: Request):
        try:
            actor = _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        cookie, csrf_token = mobile_security.issue_session()
        response = JSONResponse(
            {
                "ok": True,
                "csrf_token": csrf_token,
                "actor": {"tailscale_login": actor.tailscale_login},
            },
            headers={"Cache-Control": "no-store"},
        )
        response.set_cookie(
            "mobile_session",
            cookie,
            secure=True,
            httponly=True,
            samesite="strict",
            path="/",
        )
        return response

    @app.get("/api/mobile/projects")
    async def mobile_projects(request: Request):
        try:
            _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        summaries = await asyncio.to_thread(_cached_summaries)
        return JSONResponse(summaries, headers={"Cache-Control": "no-store"})

    @app.get("/api/mobile/project/{project_id}/dashboard")
    async def mobile_dashboard_state(project_id: str, request: Request):
        from backlot.mobile_state import build_mobile_state

        try:
            _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        try:
            project_dir = _safe_project_dir(project_id)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"ok": False, "code": "project_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        state = await asyncio.to_thread(build_mobile_state, project_dir)
        return JSONResponse(state, headers={"Cache-Control": "no-store"})

    @app.get("/api/mobile/project/{project_id}/media/{asset_id}")
    async def mobile_media(project_id: str, asset_id: str, request: Request):
        from backlot.media_library import resolve_mobile_media

        try:
            _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        try:
            project_dir = _safe_project_dir(project_id)
        except HTTPException:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "code": "project_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        media = await asyncio.to_thread(resolve_mobile_media, project_dir, asset_id)
        if media is None:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "code": "asset_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        return FileResponse(
            media.path,
            media_type=media.content_type,
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/api/mobile/project/{project_id}/preview/{asset_id}")
    async def mobile_media_preview(project_id: str, asset_id: str, request: Request):
        from backlot.media_library import resolve_mobile_media

        try:
            _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        try:
            project_dir = _safe_project_dir(project_id)
        except HTTPException:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "code": "project_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        media = await asyncio.to_thread(resolve_mobile_media, project_dir, asset_id)
        if media is None:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "code": "asset_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        preview = await asyncio.to_thread(_thumbnail_for, media.path, 640)
        if preview is None:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "code": "preview_not_available"},
                headers={"Cache-Control": "no-store"},
            )
        return FileResponse(
            preview,
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/api/mobile/project/{project_id}/render/{render_kind}")
    async def mobile_render(
        project_id: str,
        render_kind: str,
        request: Request,
        download: int = 0,
    ):
        from backlot.media_library import resolve_mobile_render

        try:
            _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        if render_kind not in {"latest", "final"}:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "code": "render_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        try:
            project_dir = _safe_project_dir(project_id)
        except HTTPException:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "code": "project_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        render = await asyncio.to_thread(
            resolve_mobile_render,
            project_dir,
            require_pass=render_kind == "final",
        )
        if render is None:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "code": "render_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        return FileResponse(
            render.path,
            media_type=render.content_type,
            filename=render.path.name if download else None,
            content_disposition_type="attachment" if download else "inline",
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/api/mobile/project/{project_id}/events")
    async def mobile_project_events(project_id: str, request: Request):
        try:
            _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        try:
            _safe_project_dir(project_id)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"ok": False, "code": "project_not_found"},
                headers={"Cache-Control": "no-store"},
            )

        async def mobile_stream():
            q = hub.subscribe(project_id)
            try:
                yield _sse({"type": "hello", "project_id": project_id})
                while True:
                    if await request.is_disconnected():
                        return
                    try:
                        await asyncio.wait_for(q.get(), timeout=SSE_HEARTBEAT_SECONDS)
                    except asyncio.TimeoutError:
                        yield _sse({"type": "heartbeat", "ts": time.time()})
                        continue
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            break
                    yield _sse({"type": "change", "project_id": project_id})
            finally:
                hub.unsubscribe(q)

        return StreamingResponse(
            mobile_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
        )

    @app.post("/api/mobile/project/{project_id}/actions")
    async def mobile_action(project_id: str, request: Request):
        from backlot.mobile_actions import (
            ActionConflict,
            ActionValidationError,
            execute_action,
        )

        try:
            actor = _mobile_actor(request)
            mobile_security.verify_post(
                request.cookies.get("mobile_session"),
                request.headers.get("X-CSRF-Token"),
                request.headers.get("Origin"),
            )
            mobile_security.enforce_rate_limit(actor)
        except MobileAuthError as exc:
            return _auth_error(exc)

        content_length = request.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > mobile_security.max_payload_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={"ok": False, "code": "payload_too_large"},
                        headers={"Cache-Control": "no-store"},
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"ok": False, "code": "invalid_content_length"},
                    headers={"Cache-Control": "no-store"},
                )
        body = await request.body()
        if len(body) > mobile_security.max_payload_bytes:
            return JSONResponse(
                status_code=413,
                content={"ok": False, "code": "payload_too_large"},
                headers={"Cache-Control": "no-store"},
            )
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JSONResponse(
                status_code=400,
                content={"ok": False, "code": "invalid_json"},
                headers={"Cache-Control": "no-store"},
            )
        if not isinstance(payload, dict) or payload.get("project_id") != project_id:
            return JSONResponse(
                status_code=422,
                content={"ok": False, "code": "project_id_mismatch"},
                headers={"Cache-Control": "no-store"},
            )
        try:
            result = await asyncio.to_thread(
                execute_action, PROJECTS_DIR, payload, actor
            )
        except ActionConflict as exc:
            return JSONResponse(
                status_code=409,
                content={"ok": False, "code": str(exc)},
                headers={"Cache-Control": "no-store"},
            )
        except ActionValidationError as exc:
            return JSONResponse(
                status_code=422,
                content={"ok": False, "code": str(exc)},
                headers={"Cache-Control": "no-store"},
            )
        hub.publish(project_id)
        return JSONResponse(
            {"ok": True, "receipt": result.receipt, "replayed": result.replayed},
            headers={"Cache-Control": "no-store"},
        )

    @app.get("/api/projects")
    async def projects() -> list:
        return await asyncio.to_thread(_cached_summaries)

    @app.get("/api/project/{project_id}/state")
    async def project_state(project_id: str) -> dict:
        project_dir = _safe_project_dir(project_id)
        return await asyncio.to_thread(load_board_state, project_dir)

    @app.get("/api/project/{project_id}/events")
    async def project_events(project_id: str, request: Request) -> StreamingResponse:
        _safe_project_dir(project_id)  # 404 early for unknown projects

        async def stream():
            q = hub.subscribe(project_id)
            try:
                yield _sse({"type": "hello", "project_id": project_id})
                while True:
                    if await request.is_disconnected():
                        return
                    try:
                        await asyncio.wait_for(q.get(), timeout=SSE_HEARTBEAT_SECONDS)
                    except asyncio.TimeoutError:
                        yield _sse({"type": "heartbeat", "ts": time.time()})
                        continue
                    # Coalesce bursts: drain anything else queued.
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            break
                    yield _sse({"type": "change", "project_id": project_id})
            finally:
                hub.unsubscribe(q)

        return StreamingResponse(stream(), media_type="text/event-stream", headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        })

    @app.get("/api/library/events")
    async def library_events(request: Request) -> StreamingResponse:
        async def stream():
            q = hub.subscribe()
            try:
                yield _sse({"type": "hello"})
                while True:
                    if await request.is_disconnected():
                        return
                    try:
                        changed = await asyncio.wait_for(q.get(), timeout=SSE_HEARTBEAT_SECONDS)
                    except asyncio.TimeoutError:
                        yield _sse({"type": "heartbeat", "ts": time.time()})
                        continue
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except asyncio.QueueEmpty:
                            break
                    yield _sse({"type": "change", "project_id": changed})
            finally:
                hub.unsubscribe(q)

        return StreamingResponse(stream(), media_type="text/event-stream", headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        })

    # ---- Thumbnails (downscaled, cached on disk) ------------------------

    @app.get("/thumb/{project_id}/{file_path:path}")
    async def thumb(project_id: str, file_path: str, w: int = 640) -> FileResponse:
        project_dir = _safe_project_dir(project_id)
        target = (project_dir / file_path).resolve()
        try:
            target.relative_to(project_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="path escapes project")
        if not target.is_file():
            raise HTTPException(status_code=404, detail="media not found")
        width = min(THUMB_WIDTHS, key=lambda x: abs(x - w))
        cached = await asyncio.to_thread(_thumbnail_for, target, width)
        if cached is None:
            # Never fall back to raw video bytes for an <img> consumer (F-03);
            # non-thumbable images are safe to serve as-is.
            if target.suffix.lower() in {".mp4", ".webm", ".mov"}:
                raise HTTPException(status_code=404, detail="no poster frame available")
            return FileResponse(target)
        return FileResponse(cached, media_type="image/jpeg")

    # ---- Media (range requests handled by FileResponse) ---------------

    @app.get("/media/{project_id}/{file_path:path}")
    async def media(project_id: str, file_path: str) -> FileResponse:
        project_dir = _safe_project_dir(project_id)
        target = (project_dir / file_path).resolve()
        try:
            target.relative_to(project_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="path escapes project")
        if not target.is_file():
            raise HTTPException(status_code=404, detail="media not found")
        return FileResponse(target)

    # ---- UI ------------------------------------------------------------

    @app.get("/manifest.webmanifest")
    async def mobile_manifest() -> FileResponse:
        return FileResponse(
            UI_DIR / "manifest.webmanifest",
            media_type="application/manifest+json",
            headers={"Cache-Control": "no-cache"},
        )

    @app.get("/sw.js")
    async def mobile_service_worker() -> FileResponse:
        return FileResponse(
            UI_DIR / "sw.js",
            media_type="application/javascript",
            headers={"Cache-Control": "no-cache", "Service-Worker-Allowed": "/"},
        )

    @app.get("/mobile")
    async def mobile_page(request: Request):
        try:
            _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        return _ui_html("mobile.html", ("mobile.css", "mobile.js"))

    @app.get("/mobile/{project_id}")
    async def mobile_project_page(project_id: str, request: Request):
        try:
            _mobile_actor(request)
        except MobileAuthError as exc:
            return _auth_error(exc)
        try:
            _safe_project_dir(project_id)
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"ok": False, "code": "project_not_found"},
                headers={"Cache-Control": "no-store"},
            )
        return _ui_html("mobile.html", ("mobile.css", "mobile.js"))

    @app.get("/p/{project_id}")
    async def board_page(project_id: str) -> HTMLResponse:
        return _ui_html("board.html", ("board.css", "board.js"))

    @app.get("/p/{project_path:path}")
    async def board_page_path(project_path: str) -> HTMLResponse:
        return _ui_html("board.html", ("board.css", "board.js"))

    @app.get("/")
    async def library_page() -> HTMLResponse:
        return _ui_html("index.html", ("board.css", "library.js"))

    if UI_DIR.is_dir():
        app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")

    # The board is a long-lived SPA: a tab keeps running whatever board.js it
    # loaded, and browsers heuristically cache /ui assets. no-cache forces a
    # conditional revalidation (cheap 304 via ETag) on every load so UI fixes
    # show up on a plain refresh. Media/thumb responses keep normal caching.
    @app.middleware("http")
    async def ui_no_cache(request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path == "/" or path.startswith("/ui") or path.startswith("/p/") or path.startswith("/mobile"):
            response.headers["Cache-Control"] = "no-cache"
        if path.startswith("/mobile") or path.startswith("/api/mobile"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; connect-src 'self'; img-src 'self' data:; "
                "style-src 'self'; script-src 'self'; manifest-src 'self'; "
                "worker-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
            )
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
        return response

    return app


def _safe_project_dir(project_id: str) -> Path:
    # ':' rejects Windows drive-relative ids like "C:" (PROJECTS_DIR / "C:"
    # collapses back to PROJECTS_DIR itself).
    if any(c in project_id for c in "/\\:") or project_id in (".", ".."):
        raise HTTPException(status_code=400, detail="invalid project id")
    project_dir = PROJECTS_DIR / project_id
    if not project_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"unknown project: {project_id}")
    return project_dir


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _ffmpeg_binary() -> str | None:
    discovered = shutil.which("ffmpeg")
    if discovered:
        return discovered
    for candidate in FFMPEG_CANDIDATES:
        if candidate.is_file() and candidate.stat().st_mode & 0o111:
            return str(candidate)
    return None


def _thumbnail_for(source: Path, width: int) -> Optional[Path]:
    """Downscale an image (or extract a video poster frame) to a cached JPEG."""
    suffix = source.suffix.lower()
    is_image = suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    is_video = suffix in {".mp4", ".webm", ".mov"}
    if not (is_image or is_video):
        return None
    try:
        import hashlib
        stat = source.stat()
        key = hashlib.sha1(
            f"{source}|{stat.st_mtime_ns}|{stat.st_size}|{width}".encode()
        ).hexdigest()[:20]
        cached = THUMB_CACHE_DIR / f"{key}.jpg"
        if cached.is_file():
            return cached
        THUMB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # Unique temp per request — concurrent misses for the same source
        # must not write (and replace from) the same temp file.
        import uuid
        tmp = THUMB_CACHE_DIR / f"{key}.{uuid.uuid4().hex[:8]}.tmp.jpg"
        if is_video:
            import subprocess
            ffmpeg = _ffmpeg_binary()
            if ffmpeg is None:
                return None
            result = subprocess.run(
                [ffmpeg, "-y", "-loglevel", "error", "-ss", "1.5",
                 "-i", str(source), "-frames:v", "1",
                 "-vf", f"scale={width}:-2", str(tmp)],
                capture_output=True, timeout=30,
            )
            if result.returncode != 0 or not tmp.is_file():
                return None
        else:
            from PIL import Image
            with Image.open(source) as img:
                img = img.convert("RGB")
                img.thumbnail((width, width * 3))
                img.save(tmp, "JPEG", quality=82)
        tmp.replace(cached)
        return cached
    except Exception:
        return None


app = create_app()
