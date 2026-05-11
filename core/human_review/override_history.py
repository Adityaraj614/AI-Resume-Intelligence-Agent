from typing import Any, Dict, List

from core.human_review.review_schema import OverrideHistory
from core.human_review.review_utils import normalize_timestamp, safe_deepcopy


def append_override_event(
    history: List[Dict[str, Any]],
    audit_entry: Dict[str, Any],
) -> List[Dict[str, Any]]:
    if not isinstance(history, list):
        raise TypeError("history must be a list.")

    if not isinstance(audit_entry, dict):
        raise TypeError("audit_entry must be a dictionary.")

    updated_history = [
        safe_deepcopy(entry)
        for entry in history
    ]
    updated_history.append(safe_deepcopy(audit_entry))

    return _sort_history(updated_history)


def get_override_history(
    history: List[Dict[str, Any]],
    candidate_id: str,
) -> Dict[str, Any]:
    entries = [
        safe_deepcopy(entry)
        for entry in history
        if entry.get("candidate_id") == candidate_id
    ]

    return OverrideHistory(
        candidate_id=candidate_id,
        entries=_sort_history(entries),
    ).to_dict()


def summarize_override_history(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    sorted_history = _sort_history(history)
    override_counts: Dict[str, int] = {}

    for entry in sorted_history:
        override_type = str(entry.get("override_type", "unknown"))
        override_counts[override_type] = override_counts.get(override_type, 0) + 1

    return {
        "total_overrides": len(sorted_history),
        "override_counts": {
            key: override_counts[key]
            for key in sorted(override_counts)
        },
        "candidate_ids": sorted({
            str(entry.get("candidate_id", ""))
            for entry in sorted_history
            if entry.get("candidate_id")
        }),
    }


def _sort_history(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [
            safe_deepcopy(entry)
            for entry in history
        ],
        key=lambda entry: (
            normalize_timestamp(entry.get("timestamp")),
            str(entry.get("candidate_id", "")),
            str(entry.get("audit_id", "")),
        ),
    )
