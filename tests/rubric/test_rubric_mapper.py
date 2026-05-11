from core.rubric.rubric_mapper import map_candidate_to_rubric


def _candidate(**overrides):
    candidate = {
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "final_score": 9.0,
        "semantic_score": 0.90,
        "confidence_score": 0.92,
        "evidence_quality": 0.88,
        "recommendation": "Strong Match",
        "extracted_skills": ["Python", "Machine Learning", "FAISS"],
        "missing_skills": ["Kubernetes"],
        "years_experience": 5,
        "experience": [{"title": "ML Engineer", "company": "Example AI"}],
        "education": [{"school": "State University", "degree": "MS"}],
        "certifications": [{"name": "Azure AI Engineer"}],
        "projects": ["Resume retrieval platform"],
        "profile_text": "Asha builds retrieval systems and recruiter-facing ML platforms. " * 3,
    }
    candidate.update(overrides)
    return candidate


def test_map_candidate_to_rubric_generates_all_assignment_dimensions():
    breakdown = map_candidate_to_rubric(_candidate())

    assert breakdown["candidate_id"] == "resume_001"
    assert [score["dimension_id"] for score in breakdown["scores"]] == [
        "skills_match",
        "experience_relevance",
        "education_certifications",
        "projects_portfolio",
        "communication_quality",
    ]
    assert sum(score["weight"] for score in breakdown["scores"]) == 1.0


def test_map_candidate_to_rubric_calculates_weighted_scores():
    breakdown = map_candidate_to_rubric(_candidate())
    skills = breakdown["scores"][0]

    assert skills["dimension_name"] == "Skills Match"
    assert skills["raw_score"] == 84.3333
    assert skills["weighted_score"] == 25.3
    assert breakdown["summary"]["max_weighted_score"] == 100.0
    assert breakdown["summary"]["total_weighted_score"] > 80


def test_map_candidate_to_rubric_is_deterministic():
    first = map_candidate_to_rubric(_candidate())
    second = map_candidate_to_rubric(_candidate())

    assert first == second


def test_map_candidate_to_rubric_tracks_source_fields():
    breakdown = map_candidate_to_rubric(_candidate())
    by_id = {score["dimension_id"]: score for score in breakdown["scores"]}

    assert "extracted_skills" in by_id["skills_match"]["source_fields"]
    assert "experience" in by_id["experience_relevance"]["source_fields"]
    assert "education" in by_id["education_certifications"]["source_fields"]
    assert "projects" in by_id["projects_portfolio"]["source_fields"]
    assert "profile_text" in by_id["communication_quality"]["source_fields"]
