from core.linkedin.linkedin_normalizer import (
    canonical_skill,
    normalize_profile_dict,
    normalize_skills,
    normalize_whitespace,
)
from core.linkedin.linkedin_utils import normalize_date


def test_normalize_skills_canonicalizes_aliases_and_duplicates():
    skills = normalize_skills([
        "Machine learning",
        "machine-learning",
        "ML",
        " python ",
    ])

    assert skills == ["Machine Learning", "Python"]


def test_normalize_whitespace_cleans_text():
    assert normalize_whitespace("  Senior\n\n ML   Engineer  ") == "Senior ML Engineer"


def test_normalize_skills_uses_deterministic_ordering():
    first = normalize_skills(["SQL", "Python", "AI"])
    second = normalize_skills(["AI", "SQL", "Python"])

    assert first == second
    assert first == ["Artificial Intelligence", "Python", "SQL"]


def test_normalize_profile_dict_cleans_top_level_fields():
    normalized = normalize_profile_dict({
        "name": " Asha   Rao ",
        "headline": " ML\nEngineer ",
        "linkedin_url": "www.linkedin.com/in/asha-rao/",
        "skills": ["py"],
    })

    assert normalized["name"] == "Asha Rao"
    assert normalized["headline"] == "ML Engineer"
    assert normalized["linkedin_url"] == "https://linkedin.com/in/asha-rao"
    assert normalized["skills"] == ["Python"]


def test_normalize_date_is_rule_based():
    assert normalize_date("Jan 2021") == "2021"
    assert normalize_date("2021-7") == "2021-07"
    assert normalize_date("Current") == "Present"
    assert normalize_date("not a date") == ""


def test_canonical_skill_preserves_short_acronyms():
    assert canonical_skill("API") == "API"
