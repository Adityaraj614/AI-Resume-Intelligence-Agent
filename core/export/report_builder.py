from typing import Any, Dict, List

from core.export.export_schema import infer_candidate_count


def _candidate_name(candidate: Dict[str, Any]) -> str:
    return str(
        candidate.get("candidate_name", candidate.get("candidate_id", "unknown_candidate"))
    )


def build_report_summary(report_type: str,
                         report_data: Any) -> str:
    """
    Build deterministic recruiter-facing report summaries.
    """

    normalized_type = str(report_type or "generic").strip().lower()
    candidate_count = infer_candidate_count(report_data)

    if normalized_type in ("ranked_candidates", "ranking"):
        return f"Ranking export contains {candidate_count} candidates."

    if normalized_type in ("shortlist", "shortlisted_candidates"):
        if isinstance(report_data, list):
            strong_count = len([
                candidate
                for candidate in report_data
                if candidate.get("bucket") == "STRONG_MATCH"
            ])
        else:
            strong_count = 0

        return (
            f"Shortlist export contains {candidate_count} candidates, "
            f"including {strong_count} STRONG_MATCH candidates."
        )

    if normalized_type == "decision_support":
        prioritized_count = 0

        if isinstance(report_data, dict):
            prioritized_count = len(report_data.get("prioritized_interviews", []))

        return (
            f"Decision-support export contains {candidate_count} candidates "
            f"and {prioritized_count} priority interview recommendations."
        )

    if normalized_type == "analytics":
        summary = report_data.get("candidate_pool_summary", {}) if isinstance(report_data, dict) else {}
        total = summary.get("total_candidates", candidate_count)
        top_skill = summary.get("top_skill", "")

        if top_skill:
            return f"Analytics export covers {total} candidates; top skill is {top_skill}."

        return f"Analytics export covers {total} candidates."

    if normalized_type == "stability":
        insights = report_data.get("stability_insights", []) if isinstance(report_data, dict) else []

        if insights:
            return f"Stability export generated {len(insights)} recruiter stability insights."

        return "Stability export generated ranking consistency diagnostics."

    return f"Export contains {candidate_count} candidates."


def build_top_candidates_section(candidates: List[Dict[str, Any]],
                                 limit: int = 5) -> List[Dict[str, Any]]:
    return [
        {
            "candidate_name": _candidate_name(candidate),
            "final_score": candidate.get("final_score", 0.0),
            "recommendation": candidate.get("recommendation", ""),
            "bucket": candidate.get("bucket", ""),
        }
        for candidate in candidates[:limit]
    ]


def build_recruiter_report(
    ranked_candidates: List[Dict[str, Any]] = None,
    shortlist: List[Dict[str, Any]] = None,
    analytics_report: Dict[str, Any] = None,
    decision_report: Dict[str, Any] = None,
    stability_report: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Build a deterministic multi-section recruiter report.
    """

    ranked_candidates = ranked_candidates or []
    shortlist = shortlist or []
    analytics_report = analytics_report or {}
    decision_report = decision_report or {}
    stability_report = stability_report or {}
    prioritized_interviews = decision_report.get("prioritized_interviews", [])

    report = {
        "top_candidates": build_top_candidates_section(ranked_candidates),
        "shortlist_summary": build_report_summary("shortlist", shortlist),
        "analytics_summary": build_report_summary("analytics", analytics_report),
        "hiring_risks": decision_report.get("risk_summary", {}),
        "stability_insights": stability_report.get("stability_insights", []),
        "recommended_interviews": [
            {
                "candidate_name": _candidate_name(candidate),
                "interview_priority": candidate.get("interview_priority", ""),
                "hiring_readiness": candidate.get("hiring_readiness", ""),
            }
            for candidate in prioritized_interviews
        ],
    }
    report["report_summary"] = (
        f"Recruiter report includes {len(ranked_candidates)} ranked candidates, "
        f"{len(shortlist)} shortlisted candidates, and "
        f"{len(prioritized_interviews)} priority interview recommendations."
    )

    return report

