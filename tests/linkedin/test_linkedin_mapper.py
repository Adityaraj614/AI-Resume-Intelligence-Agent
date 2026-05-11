from core.linkedin.linkedin_mapper import map_linkedin_to_candidate_profile
from core.linkedin.linkedin_parser import parse_linkedin_json


def _payload():
    return {
        "name": "Asha Rao",
        "headline": "Senior ML Engineer",
        "summary": "Builds retrieval-first GenAI systems.",
        "skills": ["Python", "ML", "SQL"],
        "experience": [
            {
                "title": "ML Engineer",
                "company": "Contoso",
                "description": "Built FAISS retrieval and ranking services.",
                "start_date": "2020",
                "end_date": "Present",
            }
        ],
        "education": [
            {
                "school": "IIT Delhi",
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
            }
        ],
        "projects": ["AI Resume Intelligence Agent"],
        "linkedin_url": "https://linkedin.com/in/asha-rao",
    }


def test_map_linkedin_to_candidate_profile_successful_mapping():
    candidate = map_linkedin_to_candidate_profile(parse_linkedin_json(_payload()))

    assert candidate["candidate_id"].startswith("linkedin_")
    assert candidate["candidate_name"] == "Asha Rao"
    assert candidate["skills"] == ["Machine Learning", "Python", "SQL"]
    assert candidate["experience"][0]["company"] == "Contoso"
    assert "FAISS retrieval" in candidate["profile_text"]


def test_map_linkedin_to_candidate_profile_adds_source_attribution():
    candidate = map_linkedin_to_candidate_profile(_payload())

    assert candidate["source"] == "linkedin"
    assert candidate["source_metadata"] == {
        "source": "linkedin",
        "ingestion_type": "structured_json",
        "linkedin_url": "https://linkedin.com/in/asha-rao",
    }


def test_map_linkedin_to_candidate_profile_is_schema_compatible():
    candidate = map_linkedin_to_candidate_profile(_payload())

    for key in (
        "candidate_id",
        "candidate_name",
        "extracted_skills",
        "skills",
        "experience",
        "education",
        "projects",
        "source",
    ):
        assert key in candidate

    assert candidate["extracted_skills"] == candidate["skills"]


def test_map_linkedin_to_candidate_profile_is_deterministic():
    first = map_linkedin_to_candidate_profile(_payload())
    second = map_linkedin_to_candidate_profile(_payload())

    assert first == second
