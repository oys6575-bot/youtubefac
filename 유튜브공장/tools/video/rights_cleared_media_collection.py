"""Rights-first real-media collection for the YouTube Factory.

Unlike ``direct_clip_search``, this tool evaluates item-level rights before it calls a
source adapter's download method. Only accepted bytes enter the canonical project source
library. Creative selection is intentionally outside this tool.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from tools.base_tool import (
    BaseTool,
    Determinism,
    ExecutionMode,
    ResourceProfile,
    RetryPolicy,
    ToolResult,
    ToolRuntime,
    ToolStability,
    ToolStatus,
    ToolTier,
)
from tools.video.stock_sources.base import Candidate, SearchFilters


_SUPPORTED_EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".tif", ".tiff"},
    "video": {".mp4", ".mov", ".mkv", ".webm", ".ogv", ".m4v"},
    "document": {".pdf"},
}
_DIRECTORY_BY_KIND = {
    "image": "images",
    "video": "video",
    "document": "documents",
}
_LICENSE_URLS = {
    "pexels": "https://www.pexels.com/license/",
    "pixabay": "https://pixabay.com/service/license-summary/",
    "unsplash": "https://unsplash.com/license",
    "cc0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "cc-by-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "cc-by-2.5": "https://creativecommons.org/licenses/by/2.5/",
    "cc-by-sa-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "cc-by-sa-2.5": "https://creativecommons.org/licenses/by-sa/2.5/",
    "cc-by-3.0": "https://creativecommons.org/licenses/by/3.0/",
    "cc-by-sa-3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
}


@dataclass(frozen=True)
class RightsDecision:
    accepted: bool
    reason: str
    license_url: str | None = None
    public_domain_basis: str | None = None
    attribution_required: bool = False
    attribution_text: str = ""


def evaluate_rights(candidate: Candidate) -> RightsDecision:
    """Return a conservative pre-download decision for one normalized candidate."""

    license_text = (candidate.license or "").strip()
    normalized = re.sub(r"\s+", " ", license_text.lower())
    searchable = " ".join(
        [
            normalized,
            (candidate.source_tags or "").lower(),
            str((candidate.extra or {}).get("rights_notes") or "").lower(),
        ]
    )

    if "watermark" in searchable or "preview only" in searchable:
        return RightsDecision(False, "preview_or_watermark")
    if not candidate.source_url:
        return RightsDecision(False, "missing_provenance")
    if not candidate.download_url:
        return RightsDecision(False, "no_original")
    if not normalized or "verify per-file" in normalized or "check individual" in normalized:
        return RightsDecision(False, "unknown_rights")
    if "permission" in normalized or "separate contract" in normalized:
        return RightsDecision(False, "permission_required")
    if "purchase" in normalized or "paid license" in normalized:
        return RightsDecision(False, "purchase_required")
    if "editorial" in normalized or "restricted" in normalized:
        return RightsDecision(False, "restricted_use")
    if re.search(r"(?:^|[- /])nc(?:[- /]|$)", normalized) or "noncommercial" in normalized:
        return RightsDecision(False, "noncommercial")
    if re.search(r"(?:^|[- /])nd(?:[- /]|$)", normalized) or "no derivatives" in normalized:
        return RightsDecision(False, "no_derivatives")

    source = (candidate.source or "").lower()
    if "pexels license" in normalized:
        return RightsDecision(True, "accepted", license_url=_LICENSE_URLS["pexels"])
    if "pixabay" in normalized and "license" in normalized:
        return RightsDecision(True, "accepted", license_url=_LICENSE_URLS["pixabay"])
    if "unsplash license" in normalized:
        return RightsDecision(True, "accepted", license_url=_LICENSE_URLS["unsplash"])
    if "public domain" in normalized:
        return RightsDecision(
            True,
            "accepted",
            public_domain_basis=license_text,
        )
    if "cc0" in normalized or "creative commons zero" in normalized:
        return RightsDecision(True, "accepted", license_url=_LICENSE_URLS["cc0"])

    cc_key: str | None = None
    if "cc by-sa" in normalized or "creative commons attribution-sharealike" in normalized:
        cc_key = (
            "cc-by-sa-2.5" if "2.5" in normalized
            else "cc-by-sa-3.0" if "3.0" in normalized
            else "cc-by-sa-4.0"
        )
    elif "cc by" in normalized or "creative commons attribution" in normalized:
        cc_key = (
            "cc-by-2.5" if "2.5" in normalized
            else "cc-by-3.0" if "3.0" in normalized
            else "cc-by-4.0"
        )
    if cc_key:
        attribution = _attribution(candidate)
        return RightsDecision(
            True,
            "accepted",
            license_url=_LICENSE_URLS[cc_key],
            attribution_required=True,
            attribution_text=attribution,
        )

    # A source name alone never grants rights. This intentionally rejects institutional
    # adapters that supplied only a generic collection label.
    del source
    return RightsDecision(False, "unknown_rights")


class RightsClearedMediaCollection(BaseTool):
    name = "rights_cleared_media_collection"
    version = "0.1.0"
    tier = ToolTier.SOURCE
    capability = "clip_acquisition"
    provider = "openmontage"
    stability = ToolStability.BETA
    execution_mode = ExecutionMode.SYNC
    determinism = Determinism.DETERMINISTIC
    runtime = ToolRuntime.HYBRID

    dependencies = ["python:requests"]
    install_instructions = (
        "Configure at least one existing OpenMontage stock-source adapter. "
        "Pexels, Pixabay, and Unsplash use the keys documented by provider_menu()."
    )
    agent_skills: list[str] = []
    capabilities = [
        "pre_download_rights_filter",
        "multi_source_search",
        "atomic_media_freeze",
        "sha256_deduplication",
    ]
    supports = {
        "video_and_image": True,
        "unknown_rights_rejected": True,
        "creative_selection": False,
        "paid_calls": False,
    }
    best_for = ["building a reusable real-media pool before documentary scripting"]
    not_good_for = ["creative shot selection", "generated media", "rights investigation"]
    fallback_tools: list[str] = []
    input_schema = {
        "type": "object",
        "required": ["project_id", "output_dir", "queries"],
        "properties": {
            "project_id": {"type": "string"},
            "output_dir": {"type": "string"},
            "queries": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string"},
                        "kind": {"enum": ["image", "video", "document", "any"]},
                        "claim_ids": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "sources": {"type": "array", "items": {"type": "string"}},
            "max_items_per_query": {"type": "integer", "minimum": 1, "maximum": 80},
            "filters": {"type": "object"},
            "progress_path": {"type": "string"},
            "required_identity_phrases": {
                "type": "array",
                "items": {"type": "string", "minLength": 2},
                "uniqueItems": True,
            },
        },
    }
    resource_profile = ResourceProfile(
        cpu_cores=1, ram_mb=512, vram_mb=0, disk_mb=8000, network_required=True
    )
    retry_policy = RetryPolicy(max_retries=1, retryable_errors=["timeout", "rate_limit"])
    side_effects = ["downloads accepted source files beneath assets/source"]
    user_visible_verification = [
        "Validate media_collection_manifest and recompute every recorded SHA-256"
    ]

    def get_status(self) -> ToolStatus:
        try:
            from tools.video.stock_sources import available_sources

            return ToolStatus.AVAILABLE if available_sources() else ToolStatus.UNAVAILABLE
        except Exception:
            return ToolStatus.UNAVAILABLE

    def estimate_cost(self, inputs: dict[str, Any]) -> float:
        del inputs
        return 0.0

    def execute(self, inputs: dict[str, Any]) -> ToolResult:
        started = time.time()
        progress_path: Path | None = None
        project_id = str(inputs.get("project_id") or "")
        try:
            from tools.video.stock_sources import available_sources, get_source

            output_dir = Path(inputs["output_dir"]).resolve()
            if output_dir.name != "source" or output_dir.parent.name != "assets":
                return ToolResult(
                    success=False,
                    error="output_dir must be the canonical project assets/source directory",
                )
            project_root = output_dir.parent.parent
            requested_progress = inputs.get("progress_path")
            progress_path = (
                Path(str(requested_progress)).resolve()
                if requested_progress
                else project_root / "automation/progress/media_collection.json"
            )
            progress_root = (project_root / "automation/progress").resolve()
            try:
                progress_path.relative_to(progress_root)
            except ValueError:
                return ToolResult(success=False, error="progress_path must stay in automation/progress")
            output_dir.mkdir(parents=True, exist_ok=True)
            staging = output_dir / ".staging"
            staging.mkdir(parents=True, exist_ok=True)
            for directory in _DIRECTORY_BY_KIND.values():
                (output_dir / directory).mkdir(parents=True, exist_ok=True)

            requested_sources = list(inputs.get("sources") or [])
            if requested_sources:
                sources = [get_source(name) for name in requested_sources]
                unavailable = [source.name for source in sources if not source.is_available()]
                if unavailable:
                    return ToolResult(
                        success=False,
                        error=f"Requested sources unavailable: {', '.join(unavailable)}",
                    )
            else:
                sources = available_sources()
            if not sources:
                return ToolResult(success=False, error="No rights-eligible media sources available")

            queries = list(inputs["queries"])
            filters_in = dict(inputs.get("filters") or {})
            max_items = int(inputs.get("max_items_per_query", 20))
            required_identity_phrases = [
                _normalise_identity(value)
                for value in inputs.get("required_identity_phrases", [])
                if _normalise_identity(value)
            ]
            attempted = [source.name for source in sources]
            completed_sources: set[str] = set()
            failed_sources: set[str] = set()
            source_errors: list[dict[str, str]] = []
            rejected_counts: dict[str, int] = {}
            items_by_id: dict[str, dict[str, Any]] = {}
            known_hashes = _existing_hashes(output_dir)
            discovered = downloaded = duplicates = 0

            def write_progress(
                state: str,
                current_source: str | None = None,
                current_query: str | None = None,
                error: str | None = None,
            ) -> None:
                rejected = sum(rejected_counts.values())
                _atomic_json_write(
                    progress_path,
                    {
                        "version": "1.0",
                        "project_id": project_id,
                        "state": state,
                        "current_source": current_source,
                        "current_query": _safe_query_summary(current_query),
                        "sources": {
                            "attempted": attempted,
                            "completed": sorted(completed_sources),
                            "failed": sorted(failed_sources),
                        },
                        "counts": {
                            "discovered": discovered,
                            "accepted": len(items_by_id),
                            "downloaded": downloaded,
                            "duplicates": duplicates,
                            "rejected": rejected,
                        },
                        "rejected_counts": dict(sorted(rejected_counts.items())),
                        "elapsed_seconds": round(time.time() - started, 3),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "error": error,
                    },
                )

            query_records = [
                {
                    "query_id": f"Q{index:03d}",
                    "text": str(spec["query"]).strip(),
                    "kind": str(spec.get("kind") or "any"),
                    "claim_ids": list(dict.fromkeys(spec.get("claim_ids") or [])),
                }
                for index, spec in enumerate(queries, start=1)
            ]
            write_progress("searching")

            for source in sources:
                source_failed = False
                for query_record in query_records:
                    write_progress(
                        "searching", source.name, query_record["text"]
                    )
                    filters = SearchFilters(
                        kind=query_record["kind"],
                        per_page=max_items,
                        min_duration=filters_in.get("min_duration"),
                        max_duration=filters_in.get("max_duration"),
                        orientation=filters_in.get("orientation"),
                        min_width=filters_in.get("min_width"),
                    )
                    try:
                        candidates = source.search(query_record["text"], filters)
                    except Exception as exc:
                        source_failed = True
                        failed_sources.add(source.name)
                        source_errors.append(
                            {
                                "source": source.name,
                                "query": query_record["text"],
                                "error": f"{type(exc).__name__}: {exc}",
                            }
                        )
                        write_progress(
                            "searching",
                            source.name,
                            query_record["text"],
                            error=f"{type(exc).__name__}",
                        )
                        continue

                    discovered += len(candidates)
                    for candidate in candidates[:max_items]:
                        if required_identity_phrases and not _candidate_has_identity(
                            candidate, required_identity_phrases
                        ):
                            rejected_counts["identity_mismatch"] = (
                                rejected_counts.get("identity_mismatch", 0) + 1
                            )
                            write_progress("searching", source.name, query_record["text"])
                            continue
                        decision = evaluate_rights(candidate)
                        if not decision.accepted:
                            rejected_counts[decision.reason] = (
                                rejected_counts.get(decision.reason, 0) + 1
                            )
                            write_progress(
                                "searching", source.name, query_record["text"]
                            )
                            continue
                        try:
                            write_progress(
                                "downloading", source.name, query_record["text"]
                            )
                            item, was_downloaded, was_duplicate = _freeze_candidate(
                                source=source,
                                candidate=candidate,
                                decision=decision,
                                output_dir=output_dir,
                                project_root=project_root,
                                staging=staging,
                                known_hashes=known_hashes,
                                claim_ids=query_record["claim_ids"],
                            )
                        except Exception as exc:
                            rejected_counts["download_or_validation_failed"] = (
                                rejected_counts.get("download_or_validation_failed", 0) + 1
                            )
                            source_errors.append(
                                {
                                    "source": source.name,
                                    "query": query_record["text"],
                                    "error": f"{type(exc).__name__}: {exc}",
                                }
                            )
                            write_progress(
                                "searching",
                                source.name,
                                query_record["text"],
                                error=f"{type(exc).__name__}",
                            )
                            continue
                        items_by_id.setdefault(item["id"], item)
                        downloaded += int(was_downloaded)
                        duplicates += int(was_duplicate)
                        write_progress(
                            "searching", source.name, query_record["text"]
                        )
                if not source_failed:
                    completed_sources.add(source.name)
                write_progress("searching", source.name)

            try:
                staging.rmdir()
            except OSError:
                pass
            generated_at = datetime.now(timezone.utc).isoformat()
            manifest = {
                "schema_version": "1.0.0",
                "project_id": str(inputs["project_id"]),
                "collection_status": "partial" if failed_sources else "completed",
                "generated_at": generated_at,
                "queries": query_records,
                "source_summary": {
                    "attempted": attempted,
                    "completed": sorted(completed_sources),
                    "failed": sorted(failed_sources),
                    "discovered": discovered,
                    "accepted": len(items_by_id),
                    "downloaded": downloaded,
                    "duplicates": duplicates,
                    "rejected_counts": dict(sorted(rejected_counts.items())),
                },
                "items": sorted(items_by_id.values(), key=lambda item: item["id"]),
            }
            final_state = "partial" if failed_sources else "completed"
            write_progress(final_state)
            return ToolResult(
                success=True,
                data={
                    "manifest": manifest,
                    "accepted": len(items_by_id),
                    "downloaded": downloaded,
                    "duplicates": duplicates,
                    "rejected_counts": dict(sorted(rejected_counts.items())),
                    "source_errors": source_errors,
                    "progress_path": progress_path.relative_to(project_root).as_posix(),
                },
                cost_usd=0.0,
                duration_seconds=round(time.time() - started, 3),
            )
        except Exception as exc:
            if progress_path is not None:
                try:
                    _atomic_json_write(
                        progress_path,
                        {
                            "version": "1.0",
                            "project_id": project_id,
                            "state": "failed",
                            "current_source": None,
                            "current_query": None,
                            "sources": {"attempted": [], "completed": [], "failed": []},
                            "counts": {
                                "discovered": 0,
                                "accepted": 0,
                                "downloaded": 0,
                                "duplicates": 0,
                                "rejected": 0,
                            },
                            "rejected_counts": {},
                            "elapsed_seconds": round(time.time() - started, 3),
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                            "error": type(exc).__name__,
                        },
                    )
                except OSError:
                    pass
            return ToolResult(
                success=False,
                error=f"{type(exc).__name__}: {exc}",
                duration_seconds=round(time.time() - started, 3),
            )


def _safe_query_summary(value: str | None) -> str | None:
    if value is None:
        return None
    summary = re.sub(r"https?://\S+", "[link]", str(value), flags=re.IGNORECASE)
    summary = re.sub(r"\s+", " ", summary).strip()
    return summary[:160] or None


def _normalise_identity(value: object) -> str:
    text = urllib.parse.unquote(str(value or "")).lower()
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()


def _candidate_has_identity(candidate: Candidate, phrases: list[str]) -> bool:
    metadata = _normalise_identity(
        " ".join(
            [
                candidate.source_url or "",
                candidate.source_tags or "",
                candidate.creator or "",
                json.dumps(candidate.extra or {}, ensure_ascii=False, sort_keys=True),
            ]
        )
    )
    return any(phrase in metadata for phrase in phrases)


def _atomic_json_write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        with open(temporary, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _freeze_candidate(
    *,
    source: Any,
    candidate: Candidate,
    decision: RightsDecision,
    output_dir: Path,
    project_root: Path,
    staging: Path,
    known_hashes: dict[str, Path],
    claim_ids: list[str],
) -> tuple[dict[str, Any], bool, bool]:
    kind = candidate.kind if candidate.kind in _DIRECTORY_BY_KIND else "document"
    extension = _extension(candidate, kind)
    stem = _safe_name(candidate.clip_id)
    target = output_dir / _DIRECTORY_BY_KIND[kind] / f"{stem}{extension}"
    was_downloaded = False
    was_duplicate = False

    if target.is_file() and target.stat().st_size > 0:
        digest = _sha256(target)
        known_hashes.setdefault(digest, target)
        was_duplicate = True
    else:
        temporary = staging / f"{stem}.{os.getpid()}{extension}.part"
        try:
            source.download(candidate, temporary)
            if not temporary.is_file() or temporary.stat().st_size < 1:
                raise ValueError("download produced an empty file")
            digest = _sha256(temporary)
            canonical = known_hashes.get(digest)
            if canonical is not None and canonical.is_file():
                temporary.unlink()
                target = canonical
                was_duplicate = True
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(temporary, target)
                known_hashes[digest] = target
                was_downloaded = True
        finally:
            try:
                temporary.unlink()
            except (FileNotFoundError, UnboundLocalError):
                pass

    stat = target.stat()
    local_path = target.relative_to(project_root).as_posix()
    media_id = "MEDIA_" + re.sub(r"[^A-Z0-9_-]+", "_", candidate.clip_id.upper())[:84]
    return (
        {
            "id": media_id,
            "media_type": kind,
            "local_path": local_path,
            "sha256": digest,
            "source": candidate.source,
            "source_url": candidate.source_url,
            "direct_url": None,
            "creator": candidate.creator or "",
            "source_tags": candidate.source_tags or "",
            "license": candidate.license,
            "license_url": decision.license_url,
            "public_domain_basis": decision.public_domain_basis,
            "attribution_required": decision.attribution_required,
            "attribution_text": decision.attribution_text,
            "allowed_uses": ["display", "transform", "commercial"],
            "accessed_at": datetime.now(timezone.utc).isoformat(),
            "claim_ids": list(dict.fromkeys(claim_ids)),
            "technical": {
                "format": extension.lstrip("."),
                "width": max(0, int(candidate.width or 0)),
                "height": max(0, int(candidate.height or 0)),
                "duration_seconds": max(0.0, float(candidate.duration or 0.0)),
                "size_bytes": stat.st_size,
            },
        },
        was_downloaded,
        was_duplicate,
    )


def _extension(candidate: Candidate, kind: str) -> str:
    extension = Path(urllib.parse.urlparse(candidate.download_url).path).suffix.lower()
    allowed = _SUPPORTED_EXTENSIONS[kind]
    if extension not in allowed:
        extension = {"image": ".jpg", "video": ".mp4", "document": ".pdf"}[kind]
    return extension


def _existing_hashes(output_dir: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for directory in _DIRECTORY_BY_KIND.values():
        for path in (output_dir / directory).iterdir():
            if path.is_file() and path.stat().st_size > 0:
                result.setdefault(_sha256(path), path)
    return result


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return cleaned[:120] or "media"


def _attribution(candidate: Candidate) -> str:
    creator = (candidate.creator or "Unknown creator").strip()
    return f"{creator} — {candidate.source_url} ({candidate.license})"
