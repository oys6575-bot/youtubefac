"""Manifest-bound lookup for mobile media previews."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from lib.reviewed_media_inventory import all_reviewed_items


ALLOWED_SUFFIXES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".m4a": "audio/mp4",
}


@dataclass(frozen=True)
class MobileMedia:
    asset_id: str
    media_type: str
    path: Path
    content_type: str


def resolve_mobile_media(project: Path, asset_id: str) -> MobileMedia | None:
    """Resolve one exact manifest id to a file inside assets/source."""
    items = all_reviewed_items(project)
    match = next(
        (
            item
            for item in items
            if isinstance(item, dict) and item.get("id") == asset_id
        ),
        None,
    )
    if match is None:
        return None
    local_path = match.get("local_path")
    media_type = match.get("media_type")
    if not isinstance(local_path, str) or media_type not in {"image", "video", "audio"}:
        return None
    target = (project / local_path).resolve()
    source_root = (project / "assets/source").resolve()
    try:
        target.relative_to(source_root)
    except (ValueError, OSError):
        return None
    content_type = ALLOWED_SUFFIXES.get(target.suffix.lower())
    if content_type is None or not target.is_file():
        return None
    return MobileMedia(
        asset_id=asset_id,
        media_type=media_type,
        path=target,
        content_type=content_type,
    )


def resolve_mobile_render(project: Path, *, require_pass: bool) -> MobileMedia | None:
    """Resolve the latest render, optionally requiring a passed final review."""
    try:
        report = json.loads(
            (project / "artifacts/render_report.json").read_text(encoding="utf-8")
        )
        review = json.loads(
            (project / "artifacts/final_review.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if require_pass and review.get("status") != "pass":
        return None
    outputs = report.get("outputs") if isinstance(report, dict) else None
    if not isinstance(outputs, list) or not outputs or not isinstance(outputs[0], dict):
        return None
    raw_path = outputs[0].get("path")
    if not isinstance(raw_path, str) or not raw_path:
        return None
    candidate = Path(raw_path)
    target = candidate.resolve() if candidate.is_absolute() else (project / candidate).resolve()
    try:
        target.relative_to(project.resolve())
    except (ValueError, OSError):
        return None
    content_type = ALLOWED_SUFFIXES.get(target.suffix.lower())
    if content_type not in {"video/mp4", "video/quicktime", "video/webm"} or not target.is_file():
        return None
    return MobileMedia(
        asset_id="final" if require_pass else "latest",
        media_type="video",
        path=target,
        content_type=content_type,
    )
