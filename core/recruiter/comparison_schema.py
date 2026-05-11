from typing import Any, Dict, List

from core.recruiter.comparison_utils import build_candidate_summary


REQUIRED_COMPARISON_KEYS = (
    "candidate_a",
    "candidate_b",
    "comparison_summary",
    "skill_overlap",
    "missing_skill_comparison",
    "confidence_and_safety",
    "ranking_analysis",
)

REQUIRED_MULTI_COMPARISON_KEYS = (
    "candidate_count",
    "ranking_overview",
    "comparison_table",
    "skill_distribution",
    "strength_distribution",
    "comparison_summary",
)


def normalize_comparison_output(comparison_output: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(comparison_output, dict):
        raise TypeError("comparison_output must be a dictionary.")

    return {
        "candidate_a": build_candidate_summary(comparison_output.get("candidate_a", {})),
        "candidate_b": build_candidate_summary(comparison_output.get("candidate_b", {})),
        "comparison_summary": str(comparison_output.get("comparison_summary", "")).strip(),
        "skill_overlap": comparison_output.get("skill_overlap", {}),
        "missing_skill_comparison": comparison_output.get("missing_skill_comparison", {}),
        "confidence_and_safety": comparison_output.get("confidence_and_safety", {}),
        "ranking_analysis": comparison_output.get("ranking_analysis", {}),
    }


def validate_candidate_summary(candidate_summary: Dict[str, Any]) -> bool:
    if not isinstance(candidate_summary, dict):
        return False

    if not candidate_summary.get("candidate_id"):
        return False

    if not 0 <= candidate_summary["final_score"] <= 10:
        return False

    if not 0 <= candidate_summary["semantic_score"] <= 1:
        return False

    if not 0 <= candidate_summary["confidence_score"] <= 1:
        return False

    if not 0 <= candidate_summary["hallucination_risk"] <= 1:
        return False

    if not 0 <= candidate_summary["evidence_quality"] <= 1:
        return False

    for list_key in ("skills", "missing_skills", "strengths", "weaknesses"):
        if not isinstance(candidate_summary.get(list_key), list):
            return False

    return True


def validate_comparison_output(comparison_output: Dict[str, Any]) -> bool:
    if not isinstance(comparison_output, dict):
        return False

    for key in REQUIRED_COMPARISON_KEYS:
        if key not in comparison_output:
            return False

    if not validate_candidate_summary(comparison_output["candidate_a"]):
        return False

    if not validate_candidate_summary(comparison_output["candidate_b"]):
        return False

    if not comparison_output["comparison_summary"]:
        return False

    if not isinstance(comparison_output["skill_overlap"], dict):
        return False

    if not isinstance(comparison_output["missing_skill_comparison"], dict):
        return False

    if not isinstance(comparison_output["confidence_and_safety"], dict):
        return False

    if not isinstance(comparison_output["ranking_analysis"], dict):
        return False

    return True


def normalize_multi_comparison_output(multi_comparison: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(multi_comparison, dict):
        raise TypeError("multi_comparison must be a dictionary.")

    return {
        "candidate_count": int(multi_comparison.get("candidate_count", 0)),
        "ranking_overview": multi_comparison.get("ranking_overview", []),
        "comparison_table": multi_comparison.get("comparison_table", []),
        "skill_distribution": multi_comparison.get("skill_distribution", {}),
        "strength_distribution": multi_comparison.get("strength_distribution", {}),
        "comparison_summary": str(multi_comparison.get("comparison_summary", "")).strip(),
    }


def validate_multi_comparison_output(multi_comparison: Dict[str, Any]) -> bool:
    if not isinstance(multi_comparison, dict):
        return False

    for key in REQUIRED_MULTI_COMPARISON_KEYS:
        if key not in multi_comparison:
            return False

    if multi_comparison["candidate_count"] != len(multi_comparison["comparison_table"]):
        return False

    if not isinstance(multi_comparison["ranking_overview"], list):
        return False

    if not isinstance(multi_comparison["comparison_table"], list):
        return False

    if not isinstance(multi_comparison["skill_distribution"], dict):
        return False

    if not isinstance(multi_comparison["strength_distribution"], dict):
        return False

    if not isinstance(multi_comparison["comparison_summary"], str):
        return False

    previous_rank = 0

    for row in multi_comparison["comparison_table"]:
        if not validate_candidate_summary(row):
            return False

        if row["ranking_position"] < previous_rank:
            return False

        previous_rank = row["ranking_position"]

    return True

