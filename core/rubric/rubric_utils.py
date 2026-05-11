from typing import Any, Dict, Iterable, List, Tuple


RUBRIC_DIMENSIONS: Tuple[Dict[str, Any], ...] = (
    {
        "dimension_id": "skills_match",
        "dimension_name": "Skills Match",
        "weight": 0.30,
        "description": "Alignment between required skills and candidate skill evidence.",
    },
    {
        "dimension_id": "experience_relevance",
        "dimension_name": "Experience Relevance",
        "weight": 0.25,
        "description": "Relevance of professional experience and semantic role alignment.",
    },
    {
        "dimension_id": "education_certifications",
        "dimension_name": "Education & Certifications",
        "weight": 0.15,
        "description": "Structured education and certification evidence.",
    },
    {
        "dimension_id": "projects_portfolio",
        "dimension_name": "Projects / Portfolio",
        "weight": 0.20,
        "description": "Project, portfolio, and production evidence.",
    },
    {
        "dimension_id": "communication_quality",
        "dimension_name": "Communication Quality",
        "weight": 0.10,
        "description": "Profile clarity, completeness, and recruiter-readable structure.",
    },
)


def clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def bounded_float(value: Any, minimum: float = 0.0, maximum: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = minimum

    return float(min(max(number, minimum), maximum))


def normalize_score_to_100(value: Any) -> float:
    number = bounded_float(value, 0.0, 100.0)

    if number <= 1.0:
        number *= 100.0
    elif number <= 10.0:
        number *= 10.0

    return round(bounded_float(number, 0.0, 100.0), 4)


def normalize_score_to_1(value: Any) -> float:
    return round(normalize_score_to_100(value) / 100.0, 4)


def weighted_score(raw_score: Any, weight: Any) -> float:
    return round(normalize_score_to_100(raw_score) * bounded_float(weight, 0.0, 1.0), 4)


def safe_average(values: Iterable[float]) -> float:
    normalized = [float(value) for value in values]

    if not normalized:
        return 0.0

    return round(sum(normalized) / len(normalized), 4)


def as_list(value: Any) -> List[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


def non_empty_count(value: Any) -> int:
    count = 0

    for item in as_list(value):
        if isinstance(item, dict):
            if any(clean_text(entry) for entry in item.values()):
                count += 1
        elif clean_text(item):
            count += 1

    return count


def normalize_list_text(value: Any) -> List[str]:
    normalized = {
        clean_text(item).lower()
        for item in as_list(value)
        if clean_text(item)
    }

    return sorted(normalized)


def field_present(candidate: Dict[str, Any], *field_names: str) -> bool:
    return any(_has_value(candidate.get(field_name)) for field_name in field_names)


def collect_source_fields(candidate: Dict[str, Any], field_names: Iterable[str]) -> List[str]:
    return [
        field_name
        for field_name in field_names
        if _has_value(candidate.get(field_name))
    ]


def dimension_definitions() -> List[Dict[str, Any]]:
    return [dict(dimension) for dimension in RUBRIC_DIMENSIONS]


def _has_value(value: Any) -> bool:
    if value is None:
        return False

    if isinstance(value, dict):
        return bool(value)

    if isinstance(value, (list, tuple, set)):
        return any(_has_value(item) for item in value)

    return bool(clean_text(value))
