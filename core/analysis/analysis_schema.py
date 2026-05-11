from typing import Any, Dict


REQUIRED_ANALYSIS_KEYS = (
    "candidate_id",
    "summary",
    "strengths",
    "missing_skills",
    "evidence_used",
    "recommendation",
)


def _as_string_list(value: Any) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def normalize_analysis_schema(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize provider output into the recruiter analysis schema.
    """

    if not isinstance(analysis, dict):
        raise TypeError("analysis must be a dictionary.")

    return {
        "candidate_id": str(
            analysis.get("candidate_id", "unknown_candidate")
        ).strip() or "unknown_candidate",
        "summary": str(analysis.get("summary", "")).strip(),
        "strengths": _as_string_list(analysis.get("strengths")),
        "missing_skills": _as_string_list(analysis.get("missing_skills")),
        "evidence_used": _as_string_list(analysis.get("evidence_used")),
        "recommendation": str(analysis.get("recommendation", "")).strip(),
    }


def validate_analysis_output(analysis: Dict[str, Any]) -> bool:
    """
    Validate the structured output expected from candidate analysis.
    """

    if not isinstance(analysis, dict):
        return False

    for key in REQUIRED_ANALYSIS_KEYS:
        if key not in analysis:
            return False

    if not isinstance(analysis["candidate_id"], str) or not analysis["candidate_id"].strip():
        return False

    if not isinstance(analysis["summary"], str) or not analysis["summary"].strip():
        return False

    if not isinstance(analysis["strengths"], list):
        return False

    if not isinstance(analysis["missing_skills"], list):
        return False

    if not isinstance(analysis["evidence_used"], list):
        return False

    if not isinstance(analysis["recommendation"], str) or not analysis["recommendation"].strip():
        return False

    return True
