import json
from copy import deepcopy
from typing import Any, Dict


DEFAULT_REVIEW_TIMESTAMP = "not_provided"

VALID_OVERRIDE_TYPES = {
    "score_override",
    "recommendation_override",
    "shortlist_override",
    "recruiter_notes",
}


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def normalize_timestamp(timestamp: Any = DEFAULT_REVIEW_TIMESTAMP) -> str:
    normalized = clean_text(timestamp)
    return normalized or DEFAULT_REVIEW_TIMESTAMP


def normalize_override_type(override_type: Any) -> str:
    normalized = clean_text(override_type).lower().replace(" ", "_")

    if normalized not in VALID_OVERRIDE_TYPES:
        raise ValueError(
            "override_type must be one of: "
            f"{', '.join(sorted(VALID_OVERRIDE_TYPES))}."
        )

    return normalized


def normalize_score(value: Any) -> float:
    return float(value)


def safe_deepcopy(value: Any) -> Any:
    return deepcopy(value)


def deterministic_serialize(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )


def values_changed(before: Any, after: Any) -> bool:
    return deterministic_serialize(before) != deterministic_serialize(after)


def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in data.items()
        if value is not None
    }
