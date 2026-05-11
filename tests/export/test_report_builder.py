from core.export.report_builder import (
    build_recruiter_report,
    build_report_summary,
    build_top_candidates_section,
)


def test_build_report_summary_supports_shortlist_decision_analytics_and_stability():
    assert build_report_summary("ranked_candidates", [{}, {}]) == (
        "Ranking export contains 2 candidates."
    )
    assert build_report_summary(
        "shortlist",
        [{"bucket": "STRONG_MATCH"}, {"bucket": "GOOD_MATCH"}],
    ) == "Shortlist export contains 2 candidates, including 1 STRONG_MATCH candidates."
    assert build_report_summary(
        "decision_support",
        {"candidate_count": 2, "prioritized_interviews": [{}]},
    ) == (
        "Decision-support export contains 2 candidates and "
        "1 priority interview recommendations."
    )
    assert build_report_summary(
        "analytics",
        {"candidate_pool_summary": {"total_candidates": 3, "top_skill": "python"}},
    ) == "Analytics export covers 3 candidates; top skill is python."
    assert build_report_summary(
        "stability",
        {"stability_insights": ["Stable.", "No drift."]},
    ) == "Stability export generated 2 recruiter stability insights."


def test_build_top_candidates_section_uses_safe_candidate_fields():
    section = build_top_candidates_section([
        {
            "candidate_name": "Asha Rao",
            "final_score": 8.9,
            "recommendation": "Strong Match",
            "bucket": "STRONG_MATCH",
        }
    ])

    assert section == [
        {
            "candidate_name": "Asha Rao",
            "final_score": 8.9,
            "recommendation": "Strong Match",
            "bucket": "STRONG_MATCH",
        }
    ]


def test_build_recruiter_report_combines_sections_deterministically():
    report = build_recruiter_report(
        ranked_candidates=[
            {"candidate_name": "Asha Rao", "final_score": 8.9, "bucket": "STRONG_MATCH"}
        ],
        shortlist=[{"candidate_name": "Asha Rao", "bucket": "STRONG_MATCH"}],
        analytics_report={"candidate_pool_summary": {"total_candidates": 1, "top_skill": "python"}},
        decision_report={
            "risk_summary": {"LOW_CONFIDENCE": 1},
            "prioritized_interviews": [
                {
                    "candidate_name": "Asha Rao",
                    "interview_priority": "PRIORITY_INTERVIEW",
                    "hiring_readiness": "HIGH",
                }
            ],
        },
        stability_report={"stability_insights": ["Ranking consistency remains high."]},
    )

    assert report["top_candidates"][0]["candidate_name"] == "Asha Rao"
    assert report["hiring_risks"] == {"LOW_CONFIDENCE": 1}
    assert report["recommended_interviews"][0]["interview_priority"] == "PRIORITY_INTERVIEW"
    assert report["report_summary"] == (
        "Recruiter report includes 1 ranked candidates, "
        "1 shortlisted candidates, and 1 priority interview recommendations."
    )

