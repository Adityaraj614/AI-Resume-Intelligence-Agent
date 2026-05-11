import re
from typing import Any, Dict, Iterable, List

from core.linkedin.linkedin_utils import clean_text, dedupe_preserve_order, normalize_date, normalize_url


SKILL_ALIASES = {
    "ai": "Artificial Intelligence",
    "artificial intelligence": "Artificial Intelligence",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "machine-learning": "Machine Learning",
    "python": "Python",
    "py": "Python",
    "sql": "SQL",
    "structured query language": "SQL",
    "js": "JavaScript",
    "javascript": "JavaScript",
}


def normalize_whitespace(value: Any) -> str:
    return clean_text(value)


def canonical_skill(value: Any) -> str:
    skill = normalize_whitespace(value)

    if not skill:
        return ""

    alias_key = re.sub(r"\s+", " ", skill.replace("_", " ").strip().lower())
    alias_key = alias_key.replace(" - ", "-")

    if alias_key in SKILL_ALIASES:
        return SKILL_ALIASES[alias_key]

    if skill.isupper() and len(skill) <= 5:
        return skill

    return " ".join(
        token.upper() if token.lower() in ("sql", "api", "aws", "gcp") else token.capitalize()
        for token in re.split(r"\s+", skill.replace("-", " "))
        if token
    )


def normalize_skills(skills: Iterable[Any]) -> List[str]:
    canonical_skills = [
        canonical_skill(skill)
        for skill in skills or []
    ]

    return sorted(dedupe_preserve_order(canonical_skills), key=lambda value: value.lower())


def normalize_text_list(values: Iterable[Any]) -> List[str]:
    return dedupe_preserve_order(normalize_whitespace(value) for value in values or [])


def normalize_profile_dict(profile: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(profile, dict):
        raise TypeError("profile must be a dictionary.")

    normalized = dict(profile)
    normalized["name"] = normalize_whitespace(profile.get("name", ""))
    normalized["headline"] = normalize_whitespace(profile.get("headline", ""))
    normalized["summary"] = normalize_whitespace(profile.get("summary", ""))
    normalized["location"] = normalize_whitespace(profile.get("location", ""))
    normalized["linkedin_url"] = normalize_url(profile.get("linkedin_url", profile.get("url", "")))
    normalized["skills"] = normalize_skills(profile.get("skills", []))

    return normalized


def normalize_date_fields(item: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(item)
    normalized["start_date"] = normalize_date(item.get("start_date", item.get("start", "")))
    normalized["end_date"] = normalize_date(item.get("end_date", item.get("end", "")))

    return normalized
