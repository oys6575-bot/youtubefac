"""Deterministic, fail-closed relevance review for collected documentary media.

This module deliberately performs no I/O, model loading, or network access.  Search
queries and inherited claim IDs describe an editor's intent and therefore never
count as proof that an asset depicts the selected event.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import re
import unicodedata
from urllib.parse import unquote


CATEGORIES = (
    "event_direct",
    "news_report",
    "official_record",
    "explanatory",
    "generic_broll",
    "unrelated",
    "unknown",
)
COVERAGE_LANES = (
    "event_site",
    "warning_cracks",
    "aftermath_rescue",
    "factory_context",
    "news_newspaper",
    "official_record",
    "map_structure",
)

_MISMATCH_TERMS = {
    "ukraine": "different location: Ukraine",
    "syria": "different location: Syria",
    "turkey": "different location: Turkey",
    "türkiye": "different location: Türkiye",
    "earthquake": "different event type: earthquake",
    "bombed": "different event type: war damage",
    "bombing": "different event type: war damage",
    "war ruins": "different event type: war damage",
    "demolition": "different event type: demolition",
    "demolished": "different event type: demolition",
    "rock on shore": "unrelated scene: shore rocks",
    "rocks on shore": "unrelated scene: shore rocks",
    "bazaar": "unrelated scene: bazaar",
}
_NEWS_TERMS = ("news", "report", "broadcast", "newspaper", "front page", "footage", "interview")
_OFFICIAL_TERMS = (
    "official",
    "government",
    "ministry",
    "court",
    "ilo",
    "international labour organization",
    "investigation report",
    "nara",
    "library of congress",
)
_GENERIC_TERMS = (
    "crack",
    "concrete wall",
    "brick wall",
    "pavement",
    "sewing",
    "clothing",
    "garment",
    "textile",
    "factory worker",
    "building exterior",
    "rubble",
)
_EXPLANATORY_TERMS = (
    "bangladesh garment industry",
    "savar garment factory",
    "structural diagram",
    "building plan",
    "site map",
    "rana plaza map",
)


def _normalise(value: object) -> str:
    text = unicodedata.normalize("NFKC", unquote(str(value or ""))).lower()
    return re.sub(r"[^\w]+", " ", text, flags=re.UNICODE).strip()


def _metadata_text(item: dict) -> str:
    # Deliberately excludes query, query_text and claim_ids.
    fields = ("title", "description", "source_url", "direct_url", "creator", "source")
    return " ".join(part for part in (_normalise(item.get(key)) for key in fields) if part)


def _identity_matches(text: str, topic_identity: dict) -> list[str]:
    phrases = [topic_identity.get("canonical_name", ""), *topic_identity.get("aliases", [])]
    evidence = []
    for phrase in phrases:
        token = _normalise(phrase)
        if token and token in text:
            evidence.append(f"metadata names event: {phrase}")
    # Location/date alone are supporting evidence, never sufficient event identity.
    if evidence:
        for location in topic_identity.get("locations", []):
            if (token := _normalise(location)) and token in text:
                evidence.append(f"metadata location: {location}")
        for date in topic_identity.get("dates", []):
            if (token := _normalise(date)) and token in text:
                evidence.append(f"metadata date: {date}")
    return list(dict.fromkeys(evidence))


def _decision(
    item: dict,
    *,
    category: str,
    eligibility: str,
    score: int,
    identity_evidence: list[str],
    mismatch_evidence: list[str],
    visual_summary: str,
    usefulness: str,
    methods: list[str],
    reviewed_at: str,
) -> dict:
    return {
        "media_id": item["id"],
        "media_sha256": item["sha256"],
        "category": category,
        "eligibility": eligibility,
        "relevance_score": score,
        "identity_evidence": identity_evidence,
        "mismatch_evidence": mismatch_evidence,
        "visual_summary": visual_summary,
        "usefulness": usefulness,
        "review_method": methods,
        "reviewed_at": reviewed_at,
    }


def review_one(
    item: dict,
    topic_identity: dict,
    visual_evidence: dict | None = None,
    *,
    reviewed_at: str | None = None,
) -> dict:
    """Classify one collected item using positive identity and mismatch evidence."""
    reviewed_at = reviewed_at or datetime.now(timezone.utc).isoformat()
    text = _metadata_text(item)
    identity = _identity_matches(text, topic_identity)
    mismatch = [reason for term, reason in _MISMATCH_TERMS.items() if _normalise(term) in text]
    visual = visual_evidence or {}
    visual_status = visual.get("status", "unavailable")
    labels = [str(label) for label in visual.get("labels", [])]
    visual_summary = str(visual.get("summary") or ", ".join(labels))
    methods = ["metadata"]
    if visual_status != "unavailable":
        methods.append("local_visual_evidence")

    if mismatch and not identity:
        return _decision(
            item,
            category="unrelated",
            eligibility="excluded",
            score=0,
            identity_evidence=[],
            mismatch_evidence=mismatch,
            visual_summary=visual_summary,
            usefulness="wrong event or location; excluded from production candidates",
            methods=methods,
            reviewed_at=reviewed_at,
        )

    if identity:
        if any(term in text for term in _NEWS_TERMS):
            category, score, usefulness = "news_report", 95, "direct event reporting candidate"
        elif any(term in text for term in _OFFICIAL_TERMS) or item.get("media_type") == "document":
            category, score, usefulness = "official_record", 92, "official event evidence candidate"
        else:
            category, score, usefulness = "event_direct", 90, "direct event visual candidate"
        return _decision(
            item,
            category=category,
            eligibility="eligible",
            score=score,
            identity_evidence=identity,
            mismatch_evidence=mismatch,
            visual_summary=visual_summary,
            usefulness=usefulness,
            methods=methods,
            reviewed_at=reviewed_at,
        )

    if any(term in text for term in _EXPLANATORY_TERMS):
        return _decision(
            item,
            category="explanatory",
            eligibility="eligible",
            score=65,
            identity_evidence=[],
            mismatch_evidence=[],
            visual_summary=visual_summary,
            usefulness="topic-specific explanatory context candidate",
            methods=methods,
            reviewed_at=reviewed_at,
        )

    if any(term in text for term in _GENERIC_TERMS):
        return _decision(
            item,
            category="generic_broll",
            eligibility="excluded",
            score=25,
            identity_evidence=[],
            mismatch_evidence=[],
            visual_summary=visual_summary,
            usefulness="generic B-roll; excluded unless a later VisualPlan explicitly requests it",
            methods=methods,
            reviewed_at=reviewed_at,
        )

    return _decision(
        item,
        category="unknown",
        eligibility="held",
        score=10 if visual_status != "unavailable" else 0,
        identity_evidence=[],
        mismatch_evidence=[],
        visual_summary=visual_summary,
        usefulness="identity not established; held out of automatic candidates",
        methods=methods,
        reviewed_at=reviewed_at,
    )


def _coverage(decisions: list[dict], items_by_id: dict[str, dict]) -> list[dict]:
    lanes: dict[str, list[str]] = {lane: [] for lane in COVERAGE_LANES}
    for decision in decisions:
        if decision["eligibility"] != "eligible":
            continue
        media_id = decision["media_id"]
        category = decision["category"]
        text = _metadata_text(items_by_id[media_id])
        if category == "news_report":
            lanes["news_newspaper"].append(media_id)
        if category == "official_record":
            lanes["official_record"].append(media_id)
        if category == "event_direct":
            lanes["event_site"].append(media_id)
            if any(term in text for term in ("rescue", "aftermath", "survivor", "rubble")):
                lanes["aftermath_rescue"].append(media_id)
            if "crack" in text:
                lanes["warning_cracks"].append(media_id)
        if category == "explanatory":
            if any(term in text for term in ("garment", "factory", "textile")):
                lanes["factory_context"].append(media_id)
            if any(term in text for term in ("map", "diagram", "plan", "structure")):
                lanes["map_structure"].append(media_id)
    return [
        {
            "lane": lane,
            "status": "covered" if ids else "missing",
            "eligible_media_ids": sorted(set(ids)),
        }
        for lane, ids in lanes.items()
    ]


def review_manifest(
    manifest: dict,
    manifest_sha256: str,
    topic_identity: dict,
    visual_evidence: dict[str, dict] | None = None,
    supplement_manifest: dict | None = None,
    *,
    generated_at: str | None = None,
) -> dict:
    """Review base and optional supplement items and return a canonical result."""
    generated_at = generated_at or datetime.now(timezone.utc).isoformat()
    items = [*manifest.get("items", []), *((supplement_manifest or {}).get("items", []))]
    items_by_id = {row["id"]: row for row in items}
    if len(items_by_id) != len(items):
        raise ValueError("duplicate media id across base and supplement manifests")
    evidence = visual_evidence or {}
    decisions = [
        review_one(items_by_id[media_id], topic_identity, evidence.get(media_id), reviewed_at=generated_at)
        for media_id in sorted(items_by_id)
    ]
    category_counts = Counter(row["category"] for row in decisions)
    eligibility_counts = Counter(row["eligibility"] for row in decisions)
    return {
        "schema_version": "1.0.0",
        "project_id": manifest["project_id"],
        "review_status": "completed",
        "generated_at": generated_at,
        "base_manifest_sha256": manifest_sha256,
        "supplement_manifest": supplement_manifest,
        "topic_identity": topic_identity,
        "decisions": decisions,
        "coverage": _coverage(decisions, items_by_id),
        "counts": {
            "total": len(decisions),
            "eligible": eligibility_counts["eligible"],
            "excluded": eligibility_counts["excluded"],
            "held": eligibility_counts["held"],
            "by_category": dict(sorted(category_counts.items())),
        },
    }
