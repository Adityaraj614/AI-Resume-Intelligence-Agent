import re
from typing import Any, Dict, List

from core.safety.safety_rules import (
    MIN_EVIDENCE_REQUIRED,
    MIN_RECOMMENDATION_SCORE,
)


_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "based",
    "candidate",
    "evidence",
    "from",
    "has",
    "in",
    "is",
    "of",
    "on",
    "section",
    "the",
    "to",
    "with",
}


def _tokens(text: Any) -> set:
    if not isinstance(text, str):
        return set()

    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]*", text.lower())
        if token not in _STOPWORDS and len(token) > 2
    }


def _evidence_text(matches: List[Dict[str, Any]]) -> str:
    evidence_parts = []

    for match in matches:
        evidence_parts.extend([
            str(match.get("section", "")),
            str(match.get("chunk_text", "")),
            str(match.get("jd_section", "")),
            str(match.get("jd_chunk_text", "")),
        ])

    return " ".join(evidence_parts)


def evidence_exists_for_claim(claim: str,
                              matches: List[Dict[str, Any]],
                              minimum_overlap: int = MIN_EVIDENCE_REQUIRED) -> bool:
    """
    Check whether a claim shares meaningful terms with retrieved evidence.
    """

    if not isinstance(matches, list):
        raise TypeError("matches must be a list.")

    claim_tokens = _tokens(claim)

    if not claim_tokens:
        return False

    evidence_tokens = _tokens(_evidence_text(matches))

    return len(claim_tokens.intersection(evidence_tokens)) >= minimum_overlap


def validate_analysis_evidence(analysis: Dict[str, Any],
                               candidate_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate strengths, summary, and evidence trace against retrieved matches.
    """

    if not isinstance(analysis, dict):
        raise TypeError("analysis must be a dictionary.")

    if not isinstance(candidate_metadata, dict):
        raise TypeError("candidate_metadata must be a dictionary.")

    matches = candidate_metadata.get("matches", [])

    if not isinstance(matches, list):
        matches = []

    unsupported_items = []

    for field in ("summary",):
        value = analysis.get(field, "")

        if value and not evidence_exists_for_claim(value, matches):
            unsupported_items.append({
                "field": field,
                "claim": value,
            })

    for field in ("strengths", "evidence_used"):
        values = analysis.get(field, [])

        if not isinstance(values, list):
            values = []

        for value in values:
            if not evidence_exists_for_claim(str(value), matches):
                unsupported_items.append({
                    "field": field,
                    "claim": value,
                })

    missing_skills = analysis.get("missing_skills", [])

    if isinstance(missing_skills, list):
        for missing_skill in missing_skills:
            missing_skill_text = str(missing_skill)
            explicitly_uncertain = (
                "no retrieved evidence" in missing_skill_text.lower()
                or "not found" in missing_skill_text.lower()
                or "insufficient evidence" in missing_skill_text.lower()
            )

            if (
                evidence_exists_for_claim(missing_skill_text, matches)
                and not explicitly_uncertain
            ):
                unsupported_items.append({
                    "field": "missing_skills",
                    "claim": missing_skill,
                })

    return {
        "is_valid": not unsupported_items,
        "unsupported_items": unsupported_items,
    }


def validate_recommendation_support(analysis: Dict[str, Any],
                                    candidate_metadata: Dict[str, Any]) -> bool:
    """
    Ensure recommendation label is consistent with retrieval score strength.
    """

    recommendation = str(analysis.get("recommendation", "")).strip()
    aggregate_score = float(candidate_metadata.get("aggregate_score", 0.0) or 0.0)

    required_score = MIN_RECOMMENDATION_SCORE.get(recommendation)

    if required_score is None:
        return True

    return aggregate_score >= required_score
