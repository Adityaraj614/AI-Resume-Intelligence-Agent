from typing import Any, Dict, List


def _rank_map(rankings: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        str(candidate.get("candidate_id", "")): int(
            candidate.get("ranking_position", candidate.get("rank", 0)) or 0
        )
        for candidate in rankings
        if str(candidate.get("candidate_id", ""))
    }


def detect_ranking_drift(previous_rankings: List[Dict[str, Any]],
                         current_rankings: List[Dict[str, Any]],
                         significant_shift: int = 3) -> List[Dict[str, Any]]:
    """
    Detect rank movement between two deterministic ranking runs.
    """

    previous = _rank_map(previous_rankings)
    current = _rank_map(current_rankings)
    candidate_ids = sorted(set(previous).union(current))
    drift_records = []

    for candidate_id in candidate_ids:
        previous_rank = previous.get(candidate_id)
        current_rank = current.get(candidate_id)

        if previous_rank is None:
            movement = "new_candidate"
            rank_shift = 0
        elif current_rank is None:
            movement = "removed_candidate"
            rank_shift = 0
        else:
            rank_shift = previous_rank - current_rank

            if rank_shift > 0:
                movement = "up"
            elif rank_shift < 0:
                movement = "down"
            else:
                movement = "stable"

        drift_records.append({
            "candidate_id": candidate_id,
            "previous_rank": previous_rank,
            "current_rank": current_rank,
            "rank_shift": rank_shift,
            "absolute_rank_shift": abs(rank_shift),
            "movement": movement,
            "is_significant": abs(rank_shift) >= significant_shift,
        })

    return drift_records


def analyze_candidate_movement(drift_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    upward = [
        record
        for record in drift_records
        if record["movement"] == "up"
    ]
    downward = [
        record
        for record in drift_records
        if record["movement"] == "down"
    ]
    stable = [
        record
        for record in drift_records
        if record["movement"] == "stable"
    ]
    volatile = [
        record
        for record in drift_records
        if record["is_significant"]
    ]

    return {
        "upward_movement": upward,
        "downward_movement": downward,
        "stable_candidates": stable,
        "volatile_candidates": volatile,
        "upward_count": len(upward),
        "downward_count": len(downward),
        "stable_count": len(stable),
        "volatile_count": len(volatile),
    }

