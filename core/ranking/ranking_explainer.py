from typing import Any, Dict


def summarize_ranking_signals(candidate_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the key ranking signals for recruiter-facing explanation.
    """

    if not isinstance(candidate_record, dict):
        raise TypeError("candidate_record must be a dictionary.")

    return {
        "final_score": float(candidate_record.get("final_score", 0.0)),
        "confidence": float(candidate_record.get("confidence", 0.0)),
        "semantic_score": float(candidate_record.get("semantic_score", 0.0)),
        "evidence_quality": float(candidate_record.get("evidence_quality", 0.0)),
        "evidence_coverage": float(
            candidate_record.get(
                "evidence_coverage",
                candidate_record.get("jd_match_coverage", 0.0),
            )
        ),
        "retrieval_quality": float(
            candidate_record.get(
                "retrieval_quality",
                candidate_record.get("semantic_score", 0.0),
            )
        ),
        "hallucination_risk": float(candidate_record.get("hallucination_risk", 0.0)),
        "recommendation": candidate_record.get("recommendation", "Needs Review"),
    }


def build_ranking_reason(candidate_record: Dict[str, Any]) -> str:
    """
    Build a concise explanation for why a candidate ranked where they did.
    """

    signals = summarize_ranking_signals(candidate_record)
    reason_parts = []

    if signals["final_score"] >= 8:
        reason_parts.append("strong overall hybrid score")
    elif signals["final_score"] >= 6:
        reason_parts.append("moderate overall hybrid score")
    else:
        reason_parts.append("lower overall hybrid score")

    retrieval_signal = max(
        signals["semantic_score"],
        signals["retrieval_quality"],
    )

    if retrieval_signal >= 0.8:
        reason_parts.append("strong retrieval alignment")
    elif retrieval_signal >= 0.6:
        reason_parts.append("moderate retrieval alignment")
    else:
        reason_parts.append("limited retrieval alignment")

    if signals["evidence_quality"] >= 0.8 or signals["evidence_coverage"] >= 0.8:
        reason_parts.append("high evidence coverage")
    elif signals["evidence_quality"] >= 0.5 or signals["evidence_coverage"] >= 0.5:
        reason_parts.append("usable evidence coverage")
    else:
        reason_parts.append("weak evidence coverage")

    if signals["confidence"] >= 0.8:
        reason_parts.append("high confidence")
    elif signals["confidence"] >= 0.5:
        reason_parts.append("moderate confidence")
    else:
        reason_parts.append("low confidence")

    if signals["hallucination_risk"] >= 0.30:
        reason_parts.append(
            "safety penalty applied; recruiter review recommended for unsupported claims"
        )
    elif signals["hallucination_risk"] > 0:
        reason_parts.append("safety penalty applied for unsupported claims")
    else:
        reason_parts.append("no hallucination penalty")

    return "; ".join(reason_parts) + "."


def explain_candidate_priority(candidate_record: Dict[str, Any]) -> str:
    """
    Build a recruiter-readable priority statement.
    """

    candidate_id = candidate_record.get("candidate_id", "unknown_candidate")
    recommendation = candidate_record.get("recommendation", "Needs Review")
    reason = build_ranking_reason(candidate_record)

    return f"{candidate_id}: {recommendation}. {reason}"
