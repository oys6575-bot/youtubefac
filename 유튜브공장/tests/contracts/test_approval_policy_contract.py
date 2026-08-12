import json
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]


def test_decision_log_accepts_explicit_approval_policy_decision() -> None:
    schema = json.loads(
        (ROOT / "schemas" / "artifacts" / "decision_log.schema.json").read_text(
            encoding="utf-8"
        )
    )
    decision_log = {
        "version": "1.0",
        "project_id": "youtube-factory-demo",
        "decisions": [
            {
                "decision_id": "d-001",
                "stage": "proposal",
                "category": "approval_policy",
                "subject": "Human Gate policy",
                "options_considered": [
                    {
                        "option_id": "per-gate",
                        "label": "Approve each gate separately",
                        "score": 1.0,
                        "reason": "Factory safety default.",
                    }
                ],
                "selected": "per-gate",
                "reason": "Publishing and paid work remain human-controlled.",
                "user_visible": True,
                "user_approved": False,
                "confidence": 1.0,
            }
        ],
    }

    jsonschema.validate(decision_log, schema)

