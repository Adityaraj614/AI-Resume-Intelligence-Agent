import json
from pathlib import Path
from typing import Any, Dict

import numpy as np

from core.export.export_schema import (
    DEFAULT_GENERATED_AT,
    normalize_export_payload,
    validate_export_payload,
)


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively sanitize objects to make them JSON serializable.
    Handles numpy types explicitly.
    """
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_for_json(v) for v in obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    return obj


def serialize_to_json(data: Any) -> str:
    """
    Serialize data with deterministic key ordering and readable indentation.
    """
    sanitized_data = sanitize_for_json(data)
    return json.dumps(
        sanitized_data,
        indent=2,
        sort_keys=True,
        ensure_ascii=True,
    )


def export_to_json(
    data: Any,
    output_path: str,
    report_type: str = "generic",
    report_summary: str = "",
    generated_at: str = DEFAULT_GENERATED_AT,
) -> Dict[str, Any]:
    """
    Export data to a deterministic JSON payload on disk.
    """

    payload = normalize_export_payload(
        report_type=report_type,
        report_data=data,
        report_summary=report_summary,
        generated_at=generated_at,
    )

    if not validate_export_payload(payload):
        raise ValueError("Export payload failed schema validation.")

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(serialize_to_json(payload), encoding="utf-8")

    return payload

