from typing import Any, Dict


REQUIRED_WORKFLOW_KEYS = (
    "workflow_metadata",
    "workflow_summary",
    "workflow_outputs",
    "workflow_metrics",
    "diagnostics",
)


REQUIRED_OUTPUT_KEYS = (
    "ranked_candidates",
    "shortlist",
    "filtered_candidates",
    "comparison_report",
    "analytics_report",
    "decision_support",
    "stability_report",
    "recruiter_report",
    "export_metadata",
)


def normalize_workflow_result(
    workflow_metadata: Dict[str, Any],
    workflow_summary: str,
    workflow_outputs: Dict[str, Any],
    workflow_metrics: Dict[str, Any],
    diagnostics: Dict[str, Any],
) -> Dict[str, Any]:
    normalized_outputs = dict(workflow_outputs or {})

    for key in REQUIRED_OUTPUT_KEYS:
        normalized_outputs.setdefault(key, {} if key.endswith("_report") or key == "export_metadata" else [])

    return {
        "workflow_metadata": workflow_metadata or {},
        "workflow_summary": str(workflow_summary or ""),
        "workflow_outputs": normalized_outputs,
        "workflow_metrics": workflow_metrics or {},
        "diagnostics": diagnostics or {},
    }


def validate_workflow_metadata(metadata: Dict[str, Any]) -> bool:
    if not isinstance(metadata, dict):
        return False

    required_keys = (
        "workflow_id",
        "execution_timestamp",
        "candidate_count",
        "export_format",
        "completed_modules",
        "schema_version",
    )

    for key in required_keys:
        if key not in metadata:
            return False

    if not isinstance(metadata["completed_modules"], list):
        return False

    if int(metadata["candidate_count"]) < 0:
        return False

    return True


def validate_workflow_result(result: Dict[str, Any]) -> bool:
    if not isinstance(result, dict):
        return False

    for key in REQUIRED_WORKFLOW_KEYS:
        if key not in result:
            return False

    if not validate_workflow_metadata(result["workflow_metadata"]):
        return False

    if not isinstance(result["workflow_summary"], str):
        return False

    if not isinstance(result["workflow_outputs"], dict):
        return False

    for key in REQUIRED_OUTPUT_KEYS:
        if key not in result["workflow_outputs"]:
            return False

    if not isinstance(result["workflow_metrics"], dict):
        return False

    if not isinstance(result["diagnostics"], dict):
        return False

    return True
