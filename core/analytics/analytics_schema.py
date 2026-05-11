from typing import Any, Dict


REQUIRED_ANALYTICS_REPORT_KEYS = (
    "ranking_analytics",
    "confidence_analytics",
    "hallucination_analytics",
    "evidence_analytics",
    "skill_analytics",
    "missing_skill_analytics",
    "bucket_analytics",
    "candidate_pool_summary",
    "recruiter_insights",
)


def validate_analytics_report(report: Dict[str, Any]) -> bool:
    if not isinstance(report, dict):
        return False

    for key in REQUIRED_ANALYTICS_REPORT_KEYS:
        if key not in report:
            return False

    if not isinstance(report["recruiter_insights"], list):
        return False

    if not isinstance(report["candidate_pool_summary"], dict):
        return False

    summary = report["candidate_pool_summary"]

    if summary.get("total_candidates", 0) < 0:
        return False

    if "average_confidence" in summary and not 0 <= summary["average_confidence"] <= 1:
        return False

    if "average_score" in summary and not 0 <= summary["average_score"] <= 10:
        return False

    return True


def normalize_analytics_report(report: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(report, dict):
        raise TypeError("report must be a dictionary.")

    return {
        "ranking_analytics": report.get("ranking_analytics", {}),
        "confidence_analytics": report.get("confidence_analytics", {}),
        "hallucination_analytics": report.get("hallucination_analytics", {}),
        "evidence_analytics": report.get("evidence_analytics", {}),
        "skill_analytics": report.get("skill_analytics", {}),
        "missing_skill_analytics": report.get("missing_skill_analytics", {}),
        "bucket_analytics": report.get("bucket_analytics", {}),
        "candidate_pool_summary": report.get("candidate_pool_summary", {}),
        "recruiter_insights": [
            str(insight).strip()
            for insight in report.get("recruiter_insights", [])
            if str(insight).strip()
        ],
    }

