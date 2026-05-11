from core.analytics.ranking_analytics import (
    analyze_bucket_distribution,
    analyze_confidence,
    analyze_evidence_quality,
    analyze_hallucination_risk,
    analyze_missing_skills,
    analyze_ranking_distribution,
    analyze_skill_coverage,
    build_candidate_pool_summary,
    build_full_ranking_analytics,
)


def _candidates():
    return [
        {
            "candidate_id": "resume_001",
            "ranking_position": 1,
            "final_score": 9.0,
            "confidence_score": 0.90,
            "hallucination_risk": 0.05,
            "evidence_quality": 0.85,
            "bucket": "STRONG_MATCH",
            "extracted_skills": ["Python", "SQL"],
            "missing_skills": ["Docker"],
        },
        {
            "candidate_id": "resume_002",
            "ranking_position": 2,
            "final_score": 7.0,
            "confidence_score": 0.75,
            "hallucination_risk": 0.20,
            "evidence_quality": 0.65,
            "bucket": "GOOD_MATCH",
            "extracted_skills": ["Python", "ML"],
            "missing_skills": ["Docker", "Kubernetes"],
        },
        {
            "candidate_id": "resume_003",
            "ranking_position": 3,
            "final_score": 4.0,
            "confidence_score": 0.40,
            "hallucination_risk": 0.45,
            "evidence_quality": 0.30,
            "bucket": "WEAK_MATCH",
            "extracted_skills": ["Java"],
            "missing_skills": ["Python"],
        },
    ]


def test_analyze_ranking_distribution_calculates_scores():
    analytics = analyze_ranking_distribution(_candidates())

    assert analytics["average_score"] == 6.6667
    assert analytics["median_score"] == 7.0
    assert analytics["top_score"] == 9.0
    assert analytics["lowest_score"] == 4.0
    assert analytics["score_spread"] == 5.0
    assert analytics["score_distribution"]["excellent"] == 1


def test_analyze_confidence_calculates_trustworthiness():
    analytics = analyze_confidence(_candidates())

    assert analytics["average_confidence"] == 0.6833
    assert analytics["low_confidence_count"] == 1
    assert analytics["high_confidence_count"] == 1
    assert analytics["high_confidence_ratio"] == 0.3333


def test_analyze_hallucination_risk_counts_risk_levels():
    analytics = analyze_hallucination_risk(_candidates())

    assert analytics["low_risk_count"] == 1
    assert analytics["high_risk_count"] == 1
    assert analytics["unsafe_candidate_ratio"] == 0.3333
    assert analytics["hallucination_distribution"]["high"] == 1


def test_analyze_evidence_quality_counts_evidence_levels():
    analytics = analyze_evidence_quality(_candidates())

    assert analytics["strong_evidence_count"] == 1
    assert analytics["weak_evidence_count"] == 1
    assert analytics["evidence_quality_distribution"]["usable"] == 1


def test_analyze_skill_and_missing_skill_coverage():
    skills = analyze_skill_coverage(_candidates())
    missing = analyze_missing_skills(_candidates())

    assert skills["top_skills"][0] == {"skill": "python", "count": 2}
    assert missing["top_missing_skills"][0] == {"skill": "docker", "count": 2}


def test_analyze_bucket_distribution_counts_shortlist_buckets():
    analytics = analyze_bucket_distribution(_candidates())

    assert analytics["strong_match_count"] == 1
    assert analytics["good_match_count"] == 1
    assert analytics["potential_match_count"] == 0
    assert analytics["weak_match_count"] == 1


def test_build_candidate_pool_summary_and_full_report():
    summary = build_candidate_pool_summary(_candidates())
    full_report = build_full_ranking_analytics(_candidates())

    assert summary["total_candidates"] == 3
    assert summary["top_skill"] == "python"
    assert "skill_analytics" in full_report
    assert "candidate_pool_summary" in full_report


def test_analytics_handle_empty_candidates():
    analytics = analyze_ranking_distribution([])

    assert analytics["candidate_count"] == 0
    assert analytics["average_score"] == 0.0

