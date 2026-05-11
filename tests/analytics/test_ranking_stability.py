from core.analytics.ranking_stability import (
    build_ranking_stability_report,
    calculate_stability_metrics,
    check_reproducibility,
    generate_stability_insights,
    validate_ranking_consistency,
)


def _current_rankings():
    return [
        {
            "candidate_id": "a",
            "ranking_position": 1,
            "final_score": 9.0,
            "confidence_score": 0.90,
            "hallucination_risk": 0.05,
            "evidence_quality": 0.90,
            "semantic_score": 0.90,
        },
        {
            "candidate_id": "b",
            "ranking_position": 2,
            "final_score": 8.0,
            "confidence_score": 0.80,
            "hallucination_risk": 0.10,
            "evidence_quality": 0.80,
            "semantic_score": 0.80,
        },
        {
            "candidate_id": "c",
            "ranking_position": 3,
            "final_score": 7.0,
            "confidence_score": 0.70,
            "hallucination_risk": 0.20,
            "evidence_quality": 0.70,
            "semantic_score": 0.70,
        },
    ]


def test_validate_ranking_consistency_accepts_stable_rankings():
    result = validate_ranking_consistency(_current_rankings())

    assert result["is_consistent"] is True
    assert result["consistency_score"] == 1.0


def test_check_reproducibility_compares_candidate_order():
    result = check_reproducibility(_current_rankings(), _current_rankings())
    changed = check_reproducibility(
        _current_rankings(),
        list(reversed(_current_rankings())),
    )

    assert result["is_reproducible"] is True
    assert changed["is_reproducible"] is False


def test_calculate_stability_metrics_handles_drift_records():
    metrics = calculate_stability_metrics([
        {"absolute_rank_shift": 0, "is_significant": False, "movement": "stable"},
        {"absolute_rank_shift": 2, "is_significant": True, "movement": "down"},
    ])

    assert metrics["average_rank_shift"] == 1.0
    assert metrics["stability_ratio"] == 0.5
    assert metrics["volatile_candidate_count"] == 1


def test_generate_stability_insights_is_template_based():
    insights = generate_stability_insights({
        "consistency_metrics": {"consistency_score": 1.0},
        "movement_analysis": {"volatile_count": 0, "stable_count": 2},
        "normalization_validation": {"is_valid": True},
    })

    assert "Ranking consistency remains high." in insights
    assert "No significant ranking drift detected." in insights
    assert "2 candidates remained stable across runs." in insights


def test_build_ranking_stability_report_detects_drift():
    previous = [
        {"candidate_id": "a", "ranking_position": 1},
        {"candidate_id": "b", "ranking_position": 2},
        {"candidate_id": "c", "ranking_position": 3},
    ]
    current = _current_rankings()
    current[0]["ranking_position"] = 3
    current[1]["ranking_position"] = 1
    current[2]["ranking_position"] = 2

    report = build_ranking_stability_report(
        current,
        previous_rankings=previous,
        significant_shift=2,
    )

    assert report["movement_analysis"]["volatile_count"] == 1
    assert report["normalization_validation"]["is_valid"] is True
    assert report["stability_insights"]


def test_build_ranking_stability_report_handles_empty_rankings():
    report = build_ranking_stability_report([])

    assert report["consistency_metrics"]["candidate_count"] == 0
    assert report["movement_analysis"]["stable_count"] == 0
