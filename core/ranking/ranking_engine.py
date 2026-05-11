from typing import Any, Dict, List, Optional

from core.ranking.ranking_explainer import build_ranking_reason
from core.ranking.ranking_schema import (
    normalize_ranking_schema,
    validate_ranking_output,
)
from core.ranking.ranking_utils import (
    calculate_evidence_quality,
    calculate_ranking_priority,
    calculate_recommendation_quality,
    normalize_final_rankings,
    sort_candidates_by_priority,
)


def _safety_for_candidate(candidate_id: str,
                          safety_results: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    if not safety_results:
        return {}

    return safety_results.get(candidate_id, {})


def _evidence_signals_for_candidate(candidate_id: str,
                                    evidence_quality_signals: Optional[Dict[str, Dict[str, Any]]]) -> Dict[str, Any]:
    if not evidence_quality_signals:
        return {}

    return evidence_quality_signals.get(candidate_id, {})


def _hallucination_risk_from_safety(safety_result: Dict[str, Any]) -> float:
    if "hallucination_risk" in safety_result:
        return float(safety_result.get("hallucination_risk", 0.0) or 0.0)

    unsupported_claims = safety_result.get("unsupported_claims", [])

    if unsupported_claims:
        return 0.50

    if safety_result and not safety_result.get("is_safe", True):
        return 0.35

    return 0.0


def _warning_flags(safety_result: Dict[str, Any],
                   hallucination_risk: float,
                   confidence: float,
                   evidence_quality: float) -> List[str]:
    warnings = []

    if not safety_result.get("is_safe", True):
        warnings.append("safety_validation_failed")

    if hallucination_risk >= 0.30:
        warnings.append("high_hallucination_risk")

    if confidence < 0.50:
        warnings.append("low_confidence")

    if safety_result.get("unsupported_claims"):
        warnings.append("unsupported_claims_detected")

    if evidence_quality < 0.45:
        warnings.append("weak_evidence_trace")

    return warnings


def _build_candidate_record(scoring_output: Dict[str, Any],
                            safety_result: Dict[str, Any],
                            evidence_signals: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    hallucination_risk = _hallucination_risk_from_safety(safety_result)
    evidence_signals = evidence_signals or {}
    candidate_record = {
        **scoring_output,
        **evidence_signals,
        "hallucination_risk": hallucination_risk,
    }
    candidate_record["evidence_quality"] = calculate_evidence_quality(candidate_record)
    candidate_record["recommendation_quality"] = calculate_recommendation_quality(
        candidate_record
    )
    candidate_record["ranking_priority"] = calculate_ranking_priority(candidate_record)
    candidate_record["warning_flags"] = _warning_flags(
        safety_result=safety_result,
        hallucination_risk=hallucination_risk,
        confidence=float(candidate_record.get("confidence", 0.0)),
        evidence_quality=float(candidate_record.get("evidence_quality", 0.0)),
    )
    candidate_record["ranking_reason"] = build_ranking_reason(candidate_record)

    return candidate_record


def rank_candidates(scoring_outputs: List[Dict[str, Any]],
                    safety_results: Optional[Dict[str, Dict[str, Any]]] = None,
                    evidence_quality_signals: Optional[Dict[str, Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Rank candidates using deterministic hybrid score, confidence, evidence, and safety.
    """

    if not isinstance(scoring_outputs, list):
        raise TypeError("scoring_outputs must be a list.")

    candidate_records = []

    for scoring_output in scoring_outputs:
        if not isinstance(scoring_output, dict):
            raise TypeError("Each scoring output must be a dictionary.")

        candidate_id = scoring_output.get("candidate_id", "unknown_candidate")
        safety_result = _safety_for_candidate(candidate_id, safety_results)
        evidence_signals = _evidence_signals_for_candidate(
            candidate_id,
            evidence_quality_signals,
        )
        candidate_records.append(
            _build_candidate_record(
                scoring_output=scoring_output,
                safety_result=safety_result,
                evidence_signals=evidence_signals,
            )
        )

    sorted_records = sort_candidates_by_priority(candidate_records)
    ranked_records = normalize_final_rankings(sorted_records)
    normalized_rankings = [
        normalize_ranking_schema(record)
        for record in ranked_records
    ]

    if not validate_ranking_output(normalized_rankings):
        raise ValueError("Ranking output failed schema validation.")

    return normalized_rankings
