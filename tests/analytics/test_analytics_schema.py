from core.analytics.analytics_schema import (
    normalize_analytics_report,
    validate_analytics_report,
)
from core.analytics.insight_generator import build_analytics_report


def test_validate_analytics_report_accepts_full_report():
    report = build_analytics_report([
        {
            "candidate_id": "resume_001",
            "final_score": 8.0,
            "confidence_score": 0.8,
            "hallucination_risk": 0.1,
            "evidence_quality": 0.8,
        }
    ])

    assert validate_analytics_report(report) is True


def test_validate_analytics_report_rejects_missing_keys():
    assert validate_analytics_report({"ranking_analytics": {}}) is False


def test_normalize_analytics_report_cleans_insights():
    normalized = normalize_analytics_report({
        "ranking_analytics": {},
        "confidence_analytics": {},
        "hallucination_analytics": {},
        "evidence_analytics": {},
        "skill_analytics": {},
        "missing_skill_analytics": {},
        "bucket_analytics": {},
        "candidate_pool_summary": {},
        "recruiter_insights": [" insight ", ""],
    })

    assert normalized["recruiter_insights"] == ["insight"]


def test_validate_analytics_report_rejects_invalid_summary_ranges():
    report = {
        "ranking_analytics": {},
        "confidence_analytics": {},
        "hallucination_analytics": {},
        "evidence_analytics": {},
        "skill_analytics": {},
        "missing_skill_analytics": {},
        "bucket_analytics": {},
        "candidate_pool_summary": {
            "total_candidates": 1,
            "average_confidence": 2.0,
            "average_score": 8.0,
        },
        "recruiter_insights": [],
    }

    assert validate_analytics_report(report) is False
