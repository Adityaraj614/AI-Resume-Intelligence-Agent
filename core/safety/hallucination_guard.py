import re
from typing import Any, Dict, List

from core.safety.evidence_validator import (
    evidence_exists_for_claim,
    validate_analysis_evidence,
    validate_recommendation_support,
)
from core.safety.safety_rules import FORBIDDEN_CLAIM_PATTERNS


def _contains_forbidden_pattern(text: str) -> bool:
    normalized_text = text.lower()

    return any(
        pattern in normalized_text
        for pattern in FORBIDDEN_CLAIM_PATTERNS
    )


def extract_claims_from_analysis(analysis: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract recruiter-facing claims from structured analysis fields.
    """

    if not isinstance(analysis, dict):
        raise TypeError("analysis must be a dictionary.")

    claims = []
    summary = analysis.get("summary", "")

    if isinstance(summary, str) and summary.strip():
        for sentence in re.split(r"(?<=[.!?])\s+", summary.strip()):
            if sentence:
                claims.append({
                    "field": "summary",
                    "claim": sentence,
                })

    for field in ("strengths", "missing_skills", "evidence_used"):
        values = analysis.get(field, [])

        if not isinstance(values, list):
            continue

        for value in values:
            claim = str(value).strip()

            if claim:
                claims.append({
                    "field": field,
                    "claim": claim,
                })

    recommendation = analysis.get("recommendation", "")

    if isinstance(recommendation, str) and recommendation.strip():
        claims.append({
            "field": "recommendation",
            "claim": recommendation.strip(),
        })

    return claims


def detect_unsupported_claims(analysis: Dict[str, Any],
                              candidate_metadata: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Return unsupported or hallucination-prone claims.
    """

    matches = candidate_metadata.get("matches", [])

    if not isinstance(matches, list):
        matches = []

    unsupported_claims = []

    for claim_record in extract_claims_from_analysis(analysis):
        claim = claim_record["claim"]
        field = claim_record["field"]

        if field == "missing_skills":
            continue

        if field == "recommendation":
            if not validate_recommendation_support(analysis, candidate_metadata):
                unsupported_claims.append(claim_record)

            continue

        if _contains_forbidden_pattern(claim) or not evidence_exists_for_claim(claim, matches):
            unsupported_claims.append(claim_record)

    return unsupported_claims


def validate_evidence_alignment(analysis: Dict[str, Any],
                                candidate_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate analysis against retrieval evidence and recommendation support.
    """

    evidence_validation = validate_analysis_evidence(
        analysis=analysis,
        candidate_metadata=candidate_metadata,
    )
    unsupported_claims = detect_unsupported_claims(
        analysis=analysis,
        candidate_metadata=candidate_metadata,
    )
    recommendation_supported = validate_recommendation_support(
        analysis=analysis,
        candidate_metadata=candidate_metadata,
    )

    return {
        "is_safe": (
            evidence_validation["is_valid"]
            and not unsupported_claims
            and recommendation_supported
        ),
        "unsupported_claims": unsupported_claims,
        "evidence_validation": evidence_validation,
        "recommendation_supported": recommendation_supported,
    }


def hallucination_risk_score(analysis: Dict[str, Any],
                             candidate_metadata: Dict[str, Any]) -> float:
    """
    Calculate deterministic 0-1 hallucination risk from unsupported claims.
    """

    claims = extract_claims_from_analysis(analysis)

    if not claims:
        return 1.0

    unsupported_claims = detect_unsupported_claims(
        analysis=analysis,
        candidate_metadata=candidate_metadata,
    )

    return min(len(unsupported_claims) / len(claims), 1.0)
