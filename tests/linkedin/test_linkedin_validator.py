from core.linkedin.linkedin_parser import parse_linkedin_json
from core.linkedin.linkedin_validator import validate_linkedin_profile


def test_validate_linkedin_profile_accepts_valid_profile():
    profile = parse_linkedin_json({
        "name": "Asha Rao",
        "skills": ["Python"],
        "experience": [
            {
                "title": "ML Engineer",
                "company": "Contoso",
                "start_date": "2020",
                "end_date": "2024",
            }
        ],
    })

    report = validate_linkedin_profile(profile)

    assert report["is_valid"] is True
    assert report["errors"] == []


def test_validate_linkedin_profile_reports_duplicate_and_empty_skills():
    report = validate_linkedin_profile({
        "name": "Asha Rao",
        "skills": ["Python", "python", ""],
        "experience": [],
    })

    assert report["is_valid"] is True
    assert "1 duplicate skills detected." in report["warnings"]
    assert "1 empty skills were ignored." in report["warnings"]


def test_validate_linkedin_profile_reports_invalid_date_ranges():
    report = validate_linkedin_profile({
        "name": "Ben Lee",
        "skills": ["SQL"],
        "experience": [
            {
                "title": "Analyst",
                "company": "Fabrikam",
                "start_date": "2024",
                "end_date": "2020",
            }
        ],
    })

    assert report["is_valid"] is False
    assert report["errors"] == ["Experience entry 0 has an invalid date range."]


def test_validate_linkedin_profile_reports_malformed_experience():
    report = validate_linkedin_profile({
        "name": "Chen Wu",
        "skills": ["Python"],
        "experience": ["not a dictionary"],
    })

    assert report["is_valid"] is False
    assert report["errors"] == ["Experience entry 0 is malformed."]


def test_validate_linkedin_profile_reports_missing_required_name():
    report = validate_linkedin_profile({
        "skills": ["Python"],
        "experience": [],
    })

    assert report["is_valid"] is False
    assert "Missing required field: name." in report["errors"]
