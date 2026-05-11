import re
from typing import Any, Dict, Iterable, List
from urllib.parse import urlparse


DATE_PATTERN = re.compile(r"^\d{4}(?:-\d{2})?$")


def clean_text(value: Any) -> str:
    """
    Normalize whitespace for recruiter-safe structured fields.
    """

    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def safe_get(data: Dict[str, Any], key: str, default: Any = "") -> Any:
    if not isinstance(data, dict):
        return default

    return data.get(key, default)


def as_list(value: Any) -> List[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


def dedupe_preserve_order(values: Iterable[Any]) -> List[str]:
    seen = set()
    deduped = []

    for value in values:
        normalized = clean_text(value)

        if not normalized:
            continue

        key = normalized.lower()

        if key in seen:
            continue

        seen.add(key)
        deduped.append(normalized)

    return deduped


def normalize_date(value: Any) -> str:
    candidate = clean_text(value)

    if not candidate:
        return ""

    lowered_candidate = candidate.lower()

    if lowered_candidate in ("present", "current", "now"):
        return "Present"

    match = re.search(r"\b(\d{4})(?:[-/](\d{1,2}))?\b", candidate)

    if not match:
        return ""

    year = int(match.group(1))

    if not 1900 <= year <= 2100:
        return ""

    month = match.group(2)

    if not month:
        return str(year)

    month_number = int(month)

    if not 1 <= month_number <= 12:
        return ""

    return f"{year:04d}-{month_number:02d}"


def date_sort_key(value: str) -> tuple:
    normalized = normalize_date(value)

    if normalized == "Present":
        return (9999, 12)

    if not normalized:
        return (0, 0)

    parts = normalized.split("-")
    year = int(parts[0])
    month = int(parts[1]) if len(parts) > 1 else 1

    return (year, month)


def is_valid_date_range(start_date: str, end_date: str) -> bool:
    normalized_start = normalize_date(start_date)
    normalized_end = normalize_date(end_date)

    if not normalized_start or not normalized_end:
        return True

    if normalized_end == "Present":
        return True

    return date_sort_key(normalized_start) <= date_sort_key(normalized_end)


def normalize_url(value: Any) -> str:
    candidate = clean_text(value).lower().rstrip("/")

    if not candidate:
        return ""

    if not candidate.startswith(("http://", "https://")):
        candidate = f"https://{candidate}"

    candidate = re.sub(r"^https?://www\.", "https://", candidate)
    parsed = urlparse(candidate)

    if not parsed.netloc or "." not in parsed.netloc:
        return ""

    return candidate


def stable_sort_dicts(items: List[Dict[str, Any]], keys: Iterable[str]) -> List[Dict[str, Any]]:
    sort_keys = list(keys)

    return sorted(
        items,
        key=lambda item: tuple(clean_text(item.get(key, "")).lower() for key in sort_keys),
    )
