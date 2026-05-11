from typing import Any, Dict, List

from core.rubric.rubric_utils import clean_text, normalize_list_text


def explain_dimension(
    dimension_id: str,
    raw_score: float,
    candidate: Dict[str, Any],
    source_fields: List[str],
) -> str:
    level = _score_level(raw_score)

    if dimension_id == "skills_match":
        skills = normalize_list_text(candidate.get("extracted_skills", candidate.get("skills", [])))
        missing = normalize_list_text(candidate.get("missing_skills", []))

        if missing:
            return f"{level} skills alignment with recorded gaps in {', '.join(missing[:3])}."

        if skills:
            return f"{level} skills alignment supported by recorded skills: {', '.join(skills[:3])}."

        return f"{level} skills alignment based on available scoring fields."

    if dimension_id == "experience_relevance":
        years = candidate.get("years_experience", "")

        if years != "":
            return f"{level} experience relevance with {years} years of recorded experience."

        return f"{level} experience relevance based on semantic and experience evidence."

    if dimension_id == "education_certifications":
        has_education = bool(candidate.get("education"))
        has_certifications = bool(candidate.get("certifications"))

        if has_education and has_certifications:
            return f"{level} education and certification support from structured profile fields."

        if has_education:
            return f"{level} education support from structured education evidence."

        if has_certifications:
            return f"{level} certification support from structured certification evidence."

        return f"{level} education and certification evidence is limited in available candidate data."

    if dimension_id == "projects_portfolio":
        projects = candidate.get("projects", [])

        if projects:
            return f"{level} project and portfolio signal from recorded project evidence."

        return f"{level} project and portfolio signal based on available evidence fields."

    if dimension_id == "communication_quality":
        if "profile_text" in source_fields or "text" in source_fields:
            return f"{level} communication quality based on profile completeness and readable structure."

        return f"{level} communication quality based on available summary and confidence signals."

    return f"{level} rubric signal based on available candidate fields."


def explain_rubric_breakdown(breakdown: Dict[str, Any]) -> List[str]:
    scores = breakdown.get("scores", []) if isinstance(breakdown, dict) else []
    explanations = []

    for score in scores:
        if not isinstance(score, dict):
            continue

        dimension_name = clean_text(score.get("dimension_name"))
        explanation = clean_text(score.get("explanation"))

        if dimension_name and explanation:
            explanations.append(f"{dimension_name}: {explanation}")

    return explanations


def _score_level(raw_score: float) -> str:
    score = float(raw_score)

    if score >= 85:
        return "Strong"

    if score >= 70:
        return "Good"

    if score >= 55:
        return "Moderate"

    return "Limited"
