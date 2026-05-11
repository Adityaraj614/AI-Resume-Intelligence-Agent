import pytest

from core.linkedin.linkedin_parser import parse_linkedin_json
from core.linkedin.linkedin_schema import LinkedInProfile


def _profile_payload():
    return {
        "name": " Asha Rao ",
        "headline": " Senior ML Engineer ",
        "summary": " Builds retrieval systems. ",
        "skills": ["Python", "machine-learning", {"name": "SQL"}],
        "experience": [
            {
                "title": "ML Engineer",
                "company": "Contoso",
                "start_date": "2020-01",
                "end_date": "Present",
                "description": "Built ranking services.",
            }
        ],
        "education": [
            {
                "school": "IIT Delhi",
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
            }
        ],
        "certifications": [{"name": "Azure AI", "issuer": "Microsoft"}],
        "projects": ["Resume intelligence platform"],
        "location": "Bengaluru, India",
        "linkedin_url": "linkedin.com/in/asha-rao",
    }


def test_parse_linkedin_json_valid_profile():
    profile = parse_linkedin_json(_profile_payload())

    assert isinstance(profile, LinkedInProfile)
    assert profile.name == "Asha Rao"
    assert [skill.name for skill in profile.skills] == [
        "Machine Learning",
        "Python",
        "SQL",
    ]
    assert profile.experience[0].end_date == "Present"
    assert profile.linkedin_url == "https://linkedin.com/in/asha-rao"


def test_parse_linkedin_json_accepts_partial_profile():
    profile = parse_linkedin_json({
        "name": "Ben Lee",
        "skills": ["python"],
    })

    assert profile.name == "Ben Lee"
    assert profile.headline == ""
    assert profile.experience == []
    assert profile.skills[0].name == "Python"


def test_parse_linkedin_json_rejects_malformed_json():
    with pytest.raises(ValueError, match="malformed"):
        parse_linkedin_json("{not valid json")


def test_parse_linkedin_json_strict_mode_rejects_missing_required_fields():
    with pytest.raises(ValueError, match="Missing required field"):
        parse_linkedin_json({"skills": ["Python"]}, strict=True)


def test_parse_linkedin_json_skips_malformed_optional_entries():
    profile = parse_linkedin_json({
        "name": "Chen Wu",
        "experience": ["bad entry", {"title": "Data Scientist"}],
    })

    assert len(profile.experience) == 1
    assert profile.experience[0].title == "Data Scientist"
