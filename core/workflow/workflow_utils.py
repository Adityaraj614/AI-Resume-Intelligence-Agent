import hashlib
import json
from typing import Any, Dict, Iterable, List, Optional

from core.export.export_schema import DEFAULT_GENERATED_AT


WORKFLOW_SCHEMA_VERSION = "1.0"


def safe_list(value: Optional[Iterable[Any]]) -> List[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return list(value)


def candidate_identifier(candidate: Dict[str, Any]) -> str:
    return str(
        candidate.get(
            "candidate_id",
            candidate.get("id", candidate.get("candidate_name", "")),
        )
    )


def preserve_candidate_order(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    return list(candidates)


def build_workflow_id(
    ranked_candidates: List[Dict[str, Any]],
    export_format: str = "json",
    recruiter_filters: Optional[Dict[str, Any]] = None,
    execution_timestamp: str = DEFAULT_GENERATED_AT,
) -> str:
    identity_payload = {
        "candidate_ids": [
            candidate_identifier(candidate)
            for candidate in preserve_candidate_order(ranked_candidates)
        ],
        "export_format": str(export_format or "json").strip().lower(),
        "recruiter_filters": recruiter_filters or {},
        "execution_timestamp": str(execution_timestamp or DEFAULT_GENERATED_AT),
    }
    serialized = json.dumps(identity_payload, sort_keys=True, ensure_ascii=True)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:12]

    return f"workflow_{digest}"


def build_workflow_metadata(
    ranked_candidates: List[Dict[str, Any]],
    export_format: str = "json",
    recruiter_filters: Optional[Dict[str, Any]] = None,
    execution_timestamp: str = DEFAULT_GENERATED_AT,
    completed_modules: Optional[List[str]] = None,
    workflow_id: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_timestamp = str(execution_timestamp or DEFAULT_GENERATED_AT)
    normalized_format = str(export_format or "json").strip().lower()

    return {
        "workflow_id": workflow_id or build_workflow_id(
            ranked_candidates,
            export_format=normalized_format,
            recruiter_filters=recruiter_filters,
            execution_timestamp=normalized_timestamp,
        ),
        "execution_timestamp": normalized_timestamp,
        "candidate_count": len(ranked_candidates),
        "export_format": normalized_format,
        "completed_modules": completed_modules or [],
        "schema_version": WORKFLOW_SCHEMA_VERSION,
    }


def build_workflow_summary(
    candidate_count: int,
    shortlist_count: int,
    priority_interview_count: int,
    status: str = "completed",
) -> str:
    normalized_status = str(status or "completed").strip().lower()

    if candidate_count == 0:
        return "Workflow completed with no candidates available for recruiter review."

    if normalized_status == "completed":
        return (
            f"Workflow completed successfully with {shortlist_count} shortlisted "
            f"candidates and {priority_interview_count} priority interviews identified."
        )

    if normalized_status == "partial":
        return (
            f"Workflow completed partially with {shortlist_count} shortlisted "
            f"candidates and {priority_interview_count} priority interviews identified."
        )

    return (
        f"Workflow failed with {shortlist_count} shortlisted candidates and "
        f"{priority_interview_count} priority interviews identified."
    )


def build_diagnostics(
    modules_executed: List[str],
    completed_modules: List[str],
    failed_modules: Optional[Dict[str, str]] = None,
    warnings: Optional[List[str]] = None,
    export_success: bool = False,
) -> Dict[str, Any]:
    failures = failed_modules or {}

    if failures and completed_modules:
        status = "partial"
    elif failures:
        status = "failed"
    else:
        status = "completed"

    return {
        "workflow_status": status,
        "modules_executed": modules_executed,
        "completed_modules": completed_modules,
        "failed_modules": failures,
        "pipeline_warnings": warnings or [],
        "export_success": bool(export_success),
    }


def build_missing_candidate_warnings(
    ranked_candidates: List[Dict[str, Any]],
    filtered_candidates: List[Dict[str, Any]],
) -> List[str]:
    ranked_ids = [
        candidate_identifier(candidate)
        for candidate in ranked_candidates
    ]
    filtered_ids = {
        candidate_identifier(candidate)
        for candidate in filtered_candidates
    }
    missing_ids = [
        candidate_id
        for candidate_id in ranked_ids
        if candidate_id and candidate_id not in filtered_ids
    ]

    if not missing_ids:
        return []

    return [
        f"{len(missing_ids)} candidates were removed by recruiter filters."
    ]
