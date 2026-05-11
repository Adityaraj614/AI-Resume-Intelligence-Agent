import pytest

from core.scoring.recommendation_mapper import (
    map_score_to_recommendation,
    normalize_score_range,
)


def test_normalize_score_range_converts_zero_to_one_into_ten_point_scale():
    assert normalize_score_range(0.0) == 0.0
    assert normalize_score_range(0.5) == 5.0
    assert normalize_score_range(1.0) == 10.0


def test_normalize_score_range_clips_out_of_bounds_values():
    assert normalize_score_range(-1.0) == 0.0
    assert normalize_score_range(2.0) == 10.0


def test_normalize_score_range_rejects_invalid_source_range():
    with pytest.raises(ValueError):
        normalize_score_range(0.5, source_min=1.0, source_max=1.0)


def test_map_score_to_recommendation_uses_deterministic_thresholds():
    assert map_score_to_recommendation(8.5) == "Strong Match"
    assert map_score_to_recommendation(6.5) == "Moderate Match"
    assert map_score_to_recommendation(4.5) == "Weak Match"
    assert map_score_to_recommendation(3.5) == "Poor Match"
