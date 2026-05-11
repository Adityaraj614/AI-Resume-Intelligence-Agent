from typing import Any, Dict, List


def normalize_confidence(value: float) -> float:
    """
    Clamp confidence into a stable 0-1 range.
    """

    return float(min(max(float(value), 0.0), 1.0))


def confidence_from_evidence_density(match_count: int,
                                     matched_section_count: int,
                                     evidence_trace_count: int) -> float:
    """
    Estimate confidence from how much retrieval evidence supports the score.
    """

    match_signal = min(max(match_count, 0) / 5, 1.0)
    section_signal = min(max(matched_section_count, 0) / 3, 1.0)
    trace_signal = min(max(evidence_trace_count, 0) / 3, 1.0)

    return normalize_confidence(
        (match_signal * 0.4)
        + (section_signal * 0.3)
        + (trace_signal * 0.3)
    )


def _score_consistency(matches: List[Dict[str, Any]]) -> float:
    if not matches:
        return 0.0

    scores = [
        float(match.get("score", 0.0))
        for match in matches
    ]
    score_range = max(scores) - min(scores)

    return normalize_confidence(1.0 - score_range)


def calculate_confidence(candidate_metadata: Dict[str, Any],
                         analysis: Dict[str, Any]) -> float:
    """
    Calculate deterministic confidence from retrieval and analysis completeness.
    """

    if not isinstance(candidate_metadata, dict):
        raise TypeError("candidate_metadata must be a dictionary.")

    if not isinstance(analysis, dict):
        raise TypeError("analysis must be a dictionary.")

    matches = candidate_metadata.get("matches", [])

    if not isinstance(matches, list):
        matches = []

    matched_sections = candidate_metadata.get("matched_sections", [])

    if not isinstance(matched_sections, list):
        matched_sections = []

    evidence_used = analysis.get("evidence_used", [])

    if not isinstance(evidence_used, list):
        evidence_used = []

    evidence_density = confidence_from_evidence_density(
        match_count=int(candidate_metadata.get("match_count", len(matches)) or 0),
        matched_section_count=len(matched_sections),
        evidence_trace_count=len(evidence_used),
    )
    consistency = _score_consistency(matches)
    jd_coverage = normalize_confidence(
        float(candidate_metadata.get("jd_match_coverage", 0.0) or 0.0)
    )
    analysis_completeness = normalize_confidence(
        (
            bool(str(analysis.get("summary", "")).strip())
            + bool(analysis.get("strengths"))
            + bool(analysis.get("missing_skills"))
            + bool(evidence_used)
        ) / 4
    )

    return normalize_confidence(
        (evidence_density * 0.35)
        + (consistency * 0.25)
        + (jd_coverage * 0.25)
        + (analysis_completeness * 0.15)
    )
