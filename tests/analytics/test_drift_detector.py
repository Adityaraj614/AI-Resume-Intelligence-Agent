from core.analytics.drift_detector import (
    analyze_candidate_movement,
    detect_ranking_drift,
)


def test_detect_ranking_drift_reports_rank_shift_and_direction():
    previous = [
        {"candidate_id": "a", "ranking_position": 1},
        {"candidate_id": "b", "ranking_position": 2},
        {"candidate_id": "c", "ranking_position": 3},
    ]
    current = [
        {"candidate_id": "b", "ranking_position": 1},
        {"candidate_id": "a", "ranking_position": 3},
        {"candidate_id": "d", "ranking_position": 2},
    ]

    drift = detect_ranking_drift(previous, current, significant_shift=2)
    drift_by_id = {record["candidate_id"]: record for record in drift}

    assert drift_by_id["a"]["movement"] == "down"
    assert drift_by_id["a"]["rank_shift"] == -2
    assert drift_by_id["a"]["is_significant"] is True
    assert drift_by_id["b"]["movement"] == "up"
    assert drift_by_id["c"]["movement"] == "removed_candidate"
    assert drift_by_id["d"]["movement"] == "new_candidate"


def test_analyze_candidate_movement_groups_records():
    drift = [
        {"candidate_id": "a", "movement": "up", "is_significant": False},
        {"candidate_id": "b", "movement": "down", "is_significant": True},
        {"candidate_id": "c", "movement": "stable", "is_significant": False},
    ]

    movement = analyze_candidate_movement(drift)

    assert movement["upward_count"] == 1
    assert movement["downward_count"] == 1
    assert movement["stable_count"] == 1
    assert movement["volatile_count"] == 1

