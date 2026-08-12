"""Manifest-bound lookup for mobile media previews."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


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
    manifest_path = project / "artifacts/media_collection_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    items = manifest.get("items") if isinstance(manifest, dict) else None
    if not isinstance(items, list):
        return None
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

