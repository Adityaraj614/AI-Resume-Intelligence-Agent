from core.rubric.rubric_explainer import explain_dimension, explain_rubric_breakdown
from core.rubric.rubric_mapper import map_candidate_to_rubric


def test_explain_dimension_uses_existing_skills_and_missing_skills():
    explanation = explain_dimension(
        "skills_match",
        72,
        {
            "extracted_skills": ["Python", "SQL"],
            "missing_skills": ["Docker"],
        },
        ["extracted_skills", "missing_skills"],
    )

    assert explanation == "Good skills alignment with recorded gaps in docker."


def test_explain_dimension_does_not_invent_missing_evidence():
    explanation = explain_dimension(
        "projects_portfolio",
        40,
        {},
        [],
    )

    assert explanation == "Limited project and portfolio signal based on available evidence fields."
    assert "production" not in explanation.lower()


def test_explain_rubric_breakdown_returns_dimension_linked_lines():
    breakdown = map_candidate_to_rubric({
        "candidate_id": "resume_001",
        "candidate_name": "Asha Rao",
        "extracted_skills": ["Python"],
        "missing_skills": [],
        "projects": ["ML platform"],
    })
    explanations = explain_rubric_breakdown(breakdown)

    assert len(explanations) == 5
    assert explanations[0].startswith("Skills Match:")
