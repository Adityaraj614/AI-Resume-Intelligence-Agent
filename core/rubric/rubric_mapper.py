from typing import Any, Dict, List, Optional, Tuple

from core.rubric.rubric_explainer import explain_dimension
from core.rubric.rubric_schema import RubricBreakdown, RubricScore, RubricSummary
from core.rubric.rubric_utils import (
    bounded_float,
    clean_text,
    collect_source_fields,
    dimension_definitions,
    field_present,
    non_empty_count,
    normalize_list_text,
    normalize_score_to_100,
    safe_average,
    weighted_score,
)


def map_candidate_to_rubric(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate existing recruiter intelligence into assignment rubric dimensions.

    This function does not run retrieval, ranking, scoring, or LLM logic. It
    only maps already-available candidate signals into deterministic rubric
    interpretation fields.
    """

    if not isinstance(candidate, dict):
        raise TypeError("candidate must be a dictionary.")

    scores = [
        _build_score(candidate, dimension)
        for dimension in dimension_definitions()
    ]
    summary = _build_summary(candidate, scores)
    breakdown = RubricBreakdown(
        candidate_id=_candidate_id(candidate),
        candidate_name=_candidate_name(candidate),
        scores=scores,
        summary=summary,
    )

    return breakdown.to_dict()


def _build_score(candidate: Dict[str, Any], dimension: Dict[str, Any]) -> RubricScore:
    dimension_id = dimension["dimension_id"]
    raw_score, source_fields = _dimension_raw_score(candidate, dimension_id)
    raw_score = normalize_score_to_100(raw_score)
    confidence = _dimension_confidence(candidate, source_fields)
    explanation = explain_dimension(dimension_id, raw_score, candidate, source_fields)

    return RubricScore(
        dimension_id=dimension_id,
        dimension_name=dimension["dimension_name"],
        weight=dimension["weight"],
        raw_score=raw_score,
        weighted_score=weighted_score(raw_score, dimension["weight"]),
        explanation=explanation,
        confidence=confidence,
        source_fields=source_fields,
    )


def _dimension_raw_score(candidate: Dict[str, Any], dimension_id: str) -> Tuple[float, List[str]]:
    if dimension_id == "skills_match":
        fields = (
            "skill_alignment",
            "skills_match_score",
            "semantic_score",
            "evidence_quality",
            "extracted_skills",
            "skills",
            "missing_skills",
            "matches",
            "retrieved_evidence",
        )
        explicit = _first_score(candidate, ("skill_alignment", "skills_match_score"))
        skill_coverage = _skill_coverage_score(candidate)
        evidence = _optional_score_1(candidate, "evidence_quality", "evidence_coverage")
        semantic = _optional_score_1(candidate, "semantic_score")

        return _average_available(explicit, skill_coverage, evidence, semantic), collect_source_fields(candidate, fields)

    if dimension_id == "experience_relevance":
        fields = (
            "experience_relevance",
            "years_experience",
            "experience",
            "semantic_score",
            "matched_sections",
            "matches",
        )
        explicit = _first_score(candidate, ("experience_relevance",))
        years = _years_experience_score(candidate)
        semantic = _optional_score_1(candidate, "semantic_score")
        section = _section_presence_score(candidate, ("experience", "work_experience"))

        return _average_available(explicit, years, semantic, section), collect_source_fields(candidate, fields)

    if dimension_id == "education_certifications":
        fields = (
            "education_fit",
            "education",
            "certifications",
            "licenses",
            "section_chunks",
        )
        explicit = _first_score(candidate, ("education_fit", "education_score"))
        education = 100.0 if field_present(candidate, "education") else 0.0
        certifications = 100.0 if field_present(candidate, "certifications", "licenses") else 0.0

        if explicit is not None:
            raw = _average_available(explicit, education, certifications)
        else:
            raw = max(education * 0.70 + certifications * 0.30, _section_presence_score(candidate, ("education", "certifications")))

        return raw, collect_source_fields(candidate, fields)

    if dimension_id == "projects_portfolio":
        fields = (
            "project_relevance",
            "retrieval_quality",
            "projects",
            "portfolio",
            "github",
            "evidence_quality",
            "retrieved_evidence",
        )
        explicit = _first_score(candidate, ("project_relevance", "retrieval_quality"))
        project_presence = _section_presence_score(candidate, ("projects", "portfolio", "github"))
        evidence = _optional_score_1(candidate, "evidence_quality", "evidence_coverage")

        return _average_available(explicit, project_presence, evidence), collect_source_fields(candidate, fields)

    if dimension_id == "communication_quality":
        fields = (
            "communication_quality",
            "profile_text",
            "text",
            "decision_summary",
            "ranking_reason",
            "confidence_score",
            "confidence",
            "review_notes",
        )
        explicit = _first_score(candidate, ("communication_quality", "profile_quality"))
        completeness = _profile_completeness_score(candidate)
        confidence = _optional_score_1(candidate, "confidence_score", "confidence")

        return _average_available(explicit, completeness, confidence), collect_source_fields(candidate, fields)

    return 0.0, []


def _build_summary(candidate: Dict[str, Any], scores: List[RubricScore]) -> RubricSummary:
    total = round(sum(score.weighted_score for score in scores), 4)
    max_total = round(sum(score.weight * 100.0 for score in scores), 4)
    percentage = round(total / max_total, 4) if max_total else 0.0
    strongest = max(scores, key=lambda score: (score.raw_score, score.dimension_name))
    weakest = min(scores, key=lambda score: (score.raw_score, score.dimension_name))
    label = _overall_label(percentage)

    return RubricSummary(
        candidate_id=_candidate_id(candidate),
        candidate_name=_candidate_name(candidate),
        total_weighted_score=total,
        max_weighted_score=max_total,
        overall_percentage=percentage,
        overall_label=label,
        strongest_dimension=strongest.dimension_name,
        weakest_dimension=weakest.dimension_name,
        explanation=(
            f"{_candidate_name(candidate)} maps to {label} rubric alignment; "
            f"strongest dimension is {strongest.dimension_name} and weakest dimension is {weakest.dimension_name}."
        ),
    )


def _first_score(candidate: Dict[str, Any], field_names: Tuple[str, ...]) -> Optional[float]:
    for field_name in field_names:
        if field_name in candidate and candidate.get(field_name) is not None:
            return normalize_score_to_100(candidate.get(field_name))

    return None


def _average_available(*values: Optional[float]) -> float:
    available = [float(value) for value in values if value is not None]
    return safe_average(available)


def _score_1(value: Any) -> float:
    return bounded_float(value, 0.0, 1.0) * 100.0


def _optional_score_1(candidate: Dict[str, Any], *field_names: str) -> Optional[float]:
    for field_name in field_names:
        if field_name in candidate and candidate.get(field_name) is not None:
            return _score_1(candidate.get(field_name))

    return None


def _skill_coverage_score(candidate: Dict[str, Any]) -> float:
    skills = normalize_list_text(candidate.get("extracted_skills", candidate.get("skills", [])))
    missing = normalize_list_text(candidate.get("missing_skills", []))
    total = len(skills) + len(missing)

    if total == 0:
        return 0.0

    return round((len(skills) / total) * 100.0, 4)


def _years_experience_score(candidate: Dict[str, Any]) -> float:
    years = bounded_float(candidate.get("years_experience", 0.0), 0.0, 10.0)
    return round((years / 6.0) * 100.0 if years < 6.0 else 100.0, 4)


def _section_presence_score(candidate: Dict[str, Any], section_names: Tuple[str, ...]) -> float:
    direct_counts = [non_empty_count(candidate.get(section_name)) for section_name in section_names]
    section_chunks = candidate.get("section_chunks", {})

    if isinstance(section_chunks, dict):
        direct_counts.extend(non_empty_count(section_chunks.get(section_name)) for section_name in section_names)

    count = max(direct_counts) if direct_counts else 0

    if count <= 0:
        return 0.0

    return 100.0 if count >= 2 else 70.0


def _profile_completeness_score(candidate: Dict[str, Any]) -> float:
    fields = ("profile_text", "text", "decision_summary", "ranking_reason")
    text_lengths = [len(clean_text(candidate.get(field_name))) for field_name in fields]
    structure_fields = ("extracted_skills", "skills", "experience", "education", "projects")
    structure_count = sum(1 for field_name in structure_fields if field_present(candidate, field_name))
    text_score = 100.0 if max(text_lengths or [0]) >= 300 else 70.0 if max(text_lengths or [0]) >= 80 else 35.0
    structure_score = min(structure_count / 4.0, 1.0) * 100.0

    return safe_average([text_score, structure_score])


def _dimension_confidence(candidate: Dict[str, Any], source_fields: List[str]) -> float:
    base = bounded_float(candidate.get("confidence_score", candidate.get("confidence", 0.0)), 0.0, 1.0)
    evidence_bonus = 0.05 if source_fields else 0.0
    override_bonus = 0.05 if candidate.get("override_applied") else 0.0

    return round(bounded_float(base + evidence_bonus + override_bonus, 0.0, 1.0), 4)


def _overall_label(percentage: float) -> str:
    if percentage >= 0.85:
        return "Strong"

    if percentage >= 0.70:
        return "Good"

    if percentage >= 0.55:
        return "Moderate"

    return "Limited"


def _candidate_id(candidate: Dict[str, Any]) -> str:
    return clean_text(candidate.get("candidate_id", "unknown_candidate")) or "unknown_candidate"


def _candidate_name(candidate: Dict[str, Any]) -> str:
    return clean_text(candidate.get("candidate_name", candidate.get("name", _candidate_id(candidate)))) or _candidate_id(candidate)
