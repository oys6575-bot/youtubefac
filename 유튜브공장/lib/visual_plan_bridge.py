"""Compile MK Visual Director VisualPlan into OpenMontage scene_plan."""

from __future__ import annotations

import json
from typing import Any


SCENE_TYPE = {
    "REAL": "broll",
    "AI_RECONSTRUCTION": "generated",
    "GRAPHIC": "diagram",
    "HYBRID": "animation",
}
ASSET_SOURCE = {
    "REAL_INGEST": "source",
    "TOPVIEW_HANDOFF": "generate",
    "LOCAL_LTX": "generate",
    "HYPERFRAMES": "generate",
}
NARRATIVE_ROLE = {
    "hook": "introduce_subject",
    "context": "establish_context",
    "evidence": "evidence",
    "reveal": "deliver_payload",
    "explanation": "deliver_payload",
    "tension": "build_tension",
    "consequence": "resolution",
    "reflection": "emotional_beat",
}
SHOT_SIZE = {
    "extreme_wide": "extreme_wide",
    "wide": "wide",
    "medium": "medium",
    "close": "close_up",
    "macro": "extreme_close_up",
    "insert": "insert",
}
CAMERA_MOVEMENT = {
    "locked": "static",
    "slow_push": "dolly_in",
    "slow_pull": "dolly_out",
    "pan": "pan_right",
    "tilt": "tilt_up",
    "track": "steadicam",
    "orbit": "orbital",
    "handheld_subtle": "handheld",
    "rack_focus": "rack_focus",
}


def _shot_language(camera: dict[str, Any] | None) -> dict[str, Any] | None:
    if not camera:
        return None
    return {
        "shot_size": SHOT_SIZE[camera["framing"]],
        "camera_movement": CAMERA_MOVEMENT[camera["movement"]],
    }


def compile_scene_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Flatten ordered sequences while preserving route and overlay authority."""

    scenes: list[dict[str, Any]] = []
    production_routes: dict[str, str] = {}

    for sequence in plan.get("sequences", []):
        cursor = float(sequence["narration_range"]["start_seconds"])
        for shot in sequence.get("shots", []):
            shot_id = shot["shot_id"]
            duration = float(shot["duration_seconds"])
            route = shot["provider_route"]["mode"]
            camera = shot.get("camera")
            overlay_items = shot.get("overlay", {}).get("items", [])
            scene: dict[str, Any] = {
                "id": shot_id,
                "type": SCENE_TYPE[shot["representation"]],
                "description": shot["prompt_intent"],
                "start_seconds": cursor,
                "end_seconds": cursor + duration,
                "script_section_id": sequence["sequence_id"],
                "transition_in": shot["transition_in"]["type"],
                "transition_out": shot["transition_out"]["type"],
                "overlay_notes": json.dumps(
                    overlay_items,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
                "shot_intent": shot["narrative_function"],
                "narrative_role": NARRATIVE_ROLE[shot["narrative_function"]],
                "information_role": shot["prompt_intent"],
                "hero_moment": shot["coverage_role"] == "hero",
                "required_assets": [
                    {
                        "type": "video" if route != "HYPERFRAMES" else "motion_graphic",
                        "description": f"{shot_id} via {route}",
                        "source": ASSET_SOURCE[route],
                    }
                ],
            }
            if camera:
                scene["framing"] = camera["framing"]
                scene["movement"] = camera["movement"]
                scene["shot_language"] = _shot_language(camera)
            scenes.append(scene)
            production_routes[shot_id] = route
            cursor += duration

    grammar_ids = plan.get("global_style", {}).get("grammar_ids", [])
    result: dict[str, Any] = {
        "version": "1.0",
        "scenes": scenes,
        "metadata": {
            "source_artifact": "visual_plan",
            "visual_plan_id": plan["plan_id"],
            "visual_plan_schema_version": plan["schema_version"],
            "production_routes": production_routes,
            "script_ref": plan["script_ref"],
            "script_sha256": plan["script_sha256"],
        },
    }
    if grammar_ids:
        result["style_playbook"] = grammar_ids[0]
    return result

