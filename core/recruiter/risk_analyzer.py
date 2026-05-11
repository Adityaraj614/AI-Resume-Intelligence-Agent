from typing import Any, Dict, Iterable, List, Optional

from core.recruiter.comparison_utils import (
    get_evidence_quality,
    get_hallucination_risk,
    get_semantic_score,
    normalize_missing_skills,
    normalize_weaknesses,
)
from core.recruiter.shortlist_utils import (
    get_confidence_score,
    get_warning_flags,
)


DEFAULT_CRITICAL_SKILLS = (
    "mlops",
    "docker",
    "kubernetes",
    "production deployment",
)


def find_missing_critical_skills(
    candidate: Dict[str, Any],
    critical_skills: Optional[Iterable[str]] = None,
) -> List[str]:
    critical = {
        str(skill).strip().lower()
        for skill in (critical_skills or DEFAULT_CRITICAL_SKILLS)
        if str(skill).strip()
    }
    missing_skills = set(normalize_missing_skills(candidate))

    return sorted(missing_skills.intersection(critical))


def generate_risk_flags(
    candidate: Dict[str, Any],
    critical_skills: Optional[Iterable[str]] = None,
) -> List[str]:
    """
    Generate deterministic recruiter-safe risk flags from provided evidence fields.
    """

    risk_flags = []
    confidence = get_confidence_score(candidate)
    hallucination_risk = get_hallucination_risk(candidate)
    evidence_quality = get_evidence_quality(candidate)
    semantic_score = get_semantic_score(candidate)
    warning_flags = get_warning_flags(candidate)
    weaknesses = normalize_weaknesses(candidate)
    missing_critical_skills = find_missing_critical_skills(candidate, critical_skills)

    if evidence_quality < 0.45:
        risk_flags.append("LOW_EVIDENCE_QUALITY")

    if confidence < 0.50:
        risk_flags.append("LOW_CONFIDENCE")

    if hallucination_risk >= 0.30:
        risk_flags.append("HIGH_HALLUCINATION_RISK")

    if semantic_score < 0.55:
        risk_flags.append("WEAK_SEMANTIC_ALIGNMENT")

    if missing_critical_skills:
        risk_flags.append("MISSING_CRITICAL_SKILLS")

    if "unsupported_claims_detected" in warning_flags:
        risk_flags.append("UNSUPPORTED_CLAIMS")

    if len(weaknesses) >= 3:
        risk_flags.append("MULTIPLE_PROFILE_WEAKNESSES")

    return risk_flags


def has_blocking_risk(candidate: Dict[str, Any],
                      critical_skills: Optional[Iterable[str]] = None) -> bool:
    risk_flags = generate_risk_flags(candidate, critical_skills)

    return any(
        flag in risk_flags
        for flag in (
            "HIGH_HALLUCINATION_RISK",
            "UNSUPPORTED_CLAIMS",
            "LOW_EVIDENCE_QUALITY",
        )
    )

