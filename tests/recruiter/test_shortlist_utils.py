import pytest

from core.recruiter.shortlist_utils import (
    get_confidence_score,
    get_ranking_position,
    normalize_score_to_10,
    sort_ranked_candidates,
    truncate_shortlist,
)


def test_normalize_score_to_10_accepts_100_point_scores():
    assert normalize_score_to_10(91.2) == pytest.approx(9.12)
    assert normalize_score_to_10(8.4) == 8.4


def test_get_confidence_score_accepts_confidence_score_or_confidence():
    assert get_confidence_score({"confidence_score": 0.91}) == 0.91
    assert get_confidence_score({"confidence": 0.82}) == 0.82


def test_get_ranking_position_accepts_rank_or_ranking_position():
    assert get_ranking_position({"ranking_position": 3}) == 3
    assert get_ranking_position({"rank": 2}) == 2


def test_sort_ranked_candidates_preserves_upstream_ranking_first():
    candidates = [
        {"candidate_id": "resume_002", "rank": 2, "final_score": 9.5},
        {"candidate_id": "resume_001", "rank": 1, "final_score": 7.5},
    ]

    sorted_candidates = sort_ranked_candidates(candidates)

    assert [item["candidate_id"] for item in sorted_candidates] == [
        "resume_001",
        "resume_002",
    ]


def test_truncate_shortlist_rejects_negative_top_k():
    with pytest.raises(ValueError):
        truncate_shortlist([], -1)

