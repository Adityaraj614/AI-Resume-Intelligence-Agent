from typing import Any, Dict


DEFAULT_GENERATED_AT = "not_provided"

REQUIRED_EXPORT_KEYS = (
    "export_metadata",
    "report_summary",
    "report_data",
)


def normalize_export_payload(
    report_type: str,
    report_data: Any,
    report_summary: str = "",
    generated_at: str = DEFAULT_GENERATED_AT,
) -> Dict[str, Any]:
    """
    Normalize export payloads into a stable recruiter-safe structure.
    """

    normalized_report_type = str(report_type or "generic").strip() or "generic"
    normalized_summary = str(report_summary or "").strip()

    return {
        "export_metadata": {
            "report_type": normalized_report_type,
            "generated_at": str(generated_at or DEFAULT_GENERATED_AT),
            "schema_version": "1.0",
        },
        "report_summary": normalized_summary,
        "report_data": report_data,
    }


def validate_export_payload(payload: Dict[str, Any]) -> bool:
    if not isinstance(payload, dict):
        return False

    for key in REQUIRED_EXPORT_KEYS:
        if key not in payload:
            return False

    metadata = payload["export_metadata"]

    if not isinstance(metadata, dict):
        return False

    if not metadata.get("report_type"):
        return False

    if "generated_at" not in metadata:
        return False

    if not isinstance(payload["report_summary"], str):
        return False

    return True


def infer_candidate_count(report_data: Any) -> int:
    """
    Infer candidate count from common platform report shapes.
    """

    if isinstance(report_data, list):
        return len(report_data)

    if not isinstance(report_data, dict):
        return 0

    for key in (
        "candidate_count",
        "total_candidates",
    ):
        if key in report_data:
            return int(report_data.get(key, 0) or 0)

    for key in (
        "filtered_candidates",
        "candidate_decisions",
        "prioritized_interviews",
        "comparison_table",
    ):
        if isinstance(report_data.get(key), list):
            return len(report_data[key])

    return 0

