from core.analytics.analytics_utils import (
    EVIDENCE_BUCKETS,
    SCORE_BUCKETS,
    bucket_numeric_values,
    candidate_ratio,
    count_candidate_skills,
    count_missing_skills,
    count_values,
    normalized_scores,
    safe_average,
    safe_median,
    top_count_items,
)


def _candidates():
    return [
        {
            "candidate_id": "resume_001",
            "final_score": 9.0,
            "extracted_skills": ["Python", "SQL"],
            "missing_skills": ["Docker"],
        },
        {
            "candidate_id": "resume_002",
            "final_score": 72.0,
            "extracted_skills": ["Python", "ML"],
            "missing_skills": ["Docker", "Kubernetes"],
        },
    ]


def test_safe_average_and_median_handle_empty_values():
    assert safe_average([]) == 0.0
    assert safe_median([]) == 0.0


def test_normalized_scores_accepts_10_and_100_point_scores():
    assert normalized_scores(_candidates()) == [9.0, 7.2]


def test_count_values_is_deterministic():
    assert count_values(["Python", "python", " SQL "]) == {
        "python": 2,
        "sql": 1,
    }


def test_top_count_items_sorts_by_count_then_name():
    items = top_count_items({"python": 2, "sql": 2, "docker": 1})

    assert items == [
        {"value": "python", "count": 2},
        {"value": "sql", "count": 2},
        {"value": "docker", "count": 1},
    ]


def test_skill_and_missing_skill_counting():
    assert count_candidate_skills(_candidates()) == {
        "ml": 1,
        "python": 2,
        "sql": 1,
    }
    assert count_missing_skills(_candidates()) == {
        "docker": 2,
        "kubernetes": 1,
    }


def test_bucket_numeric_values_counts_distribution():
    score_distribution = bucket_numeric_values([9.0, 7.5, 6.0, 4.0], SCORE_BUCKETS)
    evidence_distribution = bucket_numeric_values([0.8, 0.5, 0.2], EVIDENCE_BUCKETS)

    assert score_distribution == {
        "excellent": 1,
        "strong": 1,
        "moderate": 1,
        "weak": 1,
    }
    assert evidence_distribution == {
        "strong": 1,
        "usable": 1,
        "weak": 1,
    }


def test_candidate_ratio_handles_zero_total():
    assert candidate_ratio(1, 4) == 0.25
    assert candidate_ratio(1, 0) == 0.0

