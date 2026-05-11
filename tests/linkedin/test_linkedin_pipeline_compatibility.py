import json
from pathlib import Path

from core.linkedin.linkedin_mapper import map_linkedin_to_candidate_profile
from core.linkedin.linkedin_parser import parse_linkedin_json
from core.linkedin.linkedin_validator import validate_linkedin_profile


MOCK_PROFILE_PATH = Path("data/mock_linkedin/john_doe_profile.json")


def test_linkedin_profile_maps_to_unified_candidate_contract():
    with MOCK_PROFILE_PATH.open(encoding="utf-8") as profile_file:
        payload = json.load(profile_file)

    profile = parse_linkedin_json(payload)
    validation = validate_linkedin_profile(profile)
    candidate = map_linkedin_to_candidate_profile(profile)
    repeated_candidate = map_linkedin_to_candidate_profile(profile)

    assert validation["is_valid"] is True
    assert candidate == repeated_candidate

    for field in (
        "skills",
        "experience",
        "education",
        "projects",
        "profile_text",
        "candidate_id",
        "candidate_name",
        "source",
    ):
        assert field in candidate

    assert candidate["source"] == "linkedin"
    assert candidate["candidate_id"].startswith("linkedin_")
    assert candidate["candidate_name"] == "John Doe"
    assert candidate["skills"] == sorted(candidate["skills"], key=str.lower)
    assert candidate["extracted_skills"] == candidate["skills"]
    assert candidate["profile_text"].startswith("Headline:\nMachine Learning Software Engineer")
    assert "\n\nSkills:\n" in candidate["profile_text"]
    assert "\n\nExperience:\n" in candidate["profile_text"]
    assert "\n\nEducation:\n" in candidate["profile_text"]
    assert candidate["section_chunks"]["skills"] == candidate["skills"]
    assert candidate["text"] == candidate["profile_text"]


def test_linkedin_profile_text_is_labeled_and_duplicate_safe():
    candidate = map_linkedin_to_candidate_profile({
        "name": "John Doe",
        "headline": "ML Engineer",
        "summary": "Builds retrieval systems.",
        "skills": ["Python", "python", "ML"],
        "experience": [
            {
                "title": "Engineer",
                "company": "Example Co",
                "description": "Builds retrieval systems.",
            }
        ],
        "projects": [
            "Search dashboard",
            "Search dashboard",
        ],
    })

    assert candidate["profile_text"].count("Skills:") == 1
    assert candidate["section_chunks"]["skills"] == ["Machine Learning", "Python"]
    assert candidate["section_chunks"]["projects"] == ["Search dashboard"]
