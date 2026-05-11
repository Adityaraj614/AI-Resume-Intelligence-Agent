from core.human_review.override_engine import apply_override
from core.human_review.reviewer_registry import normalize_reviewer_metadata
from core.human_review.review_schema import OverrideDecision
from core.linkedin.linkedin_mapper import map_linkedin_to_candidate_profile
from core.rubric.rubric_mapper import map_candidate_to_rubric
from core.workflow.recruiter_pipeline import RecruiterPipeline


def _ranked_candidate():
    return {
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "ranking_position": 1,
        "final_score": 9.0,
        "semantic_score": 0.90,
        "confidence_score": 0.92,
        "confidence": 0.92,
        "hallucination_risk": 0.04,
        "evidence_quality": 0.88,
        "recommendation": "Strong Match",
        "extracted_skills": ["Python", "ML"],
        "missing_skills": [],
        "strengths": ["retrieval evidence"],
        "years_experience": 5,
        "projects": ["Model monitoring dashboard"],
    }


def test_rubric_mapping_is_compatible_with_workflow_outputs():
    workflow = RecruiterPipeline().run([_ranked_candidate()])
    candidate = workflow["workflow_outputs"]["ranked_candidates"][0]
    breakdown = map_candidate_to_rubric(candidate)

    assert breakdown["candidate_id"] == "resume_001"
    assert breakdown["summary"]["overall_percentage"] > 0
    assert breakdown["scores"][0]["dimension_name"] == "Skills Match"


def test_rubric_mapping_supports_linkedin_candidate_profiles():
    candidate = map_linkedin_to_candidate_profile({
        "name": "John Doe",
        "headline": "ML Engineer",
        "summary": "Builds retrieval systems.",
        "skills": ["Python", "Machine Learning"],
        "experience": [{"title": "Engineer", "company": "Example Co"}],
        "education": [{"school": "Example University", "degree": "MS"}],
        "projects": ["Search dashboard"],
    })
    breakdown = map_candidate_to_rubric(candidate)
    by_id = {score["dimension_id"]: score for score in breakdown["scores"]}

    assert breakdown["candidate_id"].startswith("linkedin_")
    assert by_id["skills_match"]["raw_score"] == 100.0
    assert by_id["projects_portfolio"]["raw_score"] > 0


def test_rubric_mapping_accepts_override_aware_final_output():
    reviewer = normalize_reviewer_metadata("Priya Shah")
    reviewed = apply_override(
        _ranked_candidate(),
        OverrideDecision(
            candidate_id="resume_001",
            override_type="recruiter_notes",
            reviewer=reviewer,
            reason="Verified portfolio evidence.",
            review_notes="Portfolio evidence reviewed by recruiter.",
            timestamp="2026-01-01T00:00:00Z",
        ),
    )
    breakdown = map_candidate_to_rubric(reviewed["final_presented_result"])
    communication = [
        score
        for score in breakdown["scores"]
        if score["dimension_id"] == "communication_quality"
    ][0]

    assert communication["confidence"] > 0.92
    assert "review_notes" in communication["source_fields"]
