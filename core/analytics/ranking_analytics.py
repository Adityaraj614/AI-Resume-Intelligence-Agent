from typing import Any, Dict, List

from core.analytics.analytics_utils import (
    EVIDENCE_BUCKETS,
    RISK_BUCKETS,
    SCORE_BUCKETS,
    bucket_numeric_values,
    candidate_ratio,
    count_candidate_skills,
    count_missing_skills,
    count_values,
    get_bucket,
    normalized_confidences,
    normalized_evidence_scores,
    normalized_hallucination_risks,
    normalized_scores,
    safe_average,
    safe_median,
    safe_round,
    sort_candidates_for_analytics,
    top_count_items,
)


def analyze_ranking_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_candidates = sort_candidates_for_analytics(candidates)
    scores = normalized_scores(ordered_candidates)

    if not scores:
        return {
            "average_score": 0.0,
            "median_score": 0.0,
            "top_score": 0.0,
            "lowest_score": 0.0,
            "score_spread": 0.0,
            "score_distribution": bucket_numeric_values([], SCORE_BUCKETS),
            "candidate_count": 0,
        }

    top_score = max(scores)
    lowest_score = min(scores)

    return {
        "average_score": safe_average(scores),
        "median_score": safe_median(scores),
        "top_score": top_score,
        "lowest_score": lowest_score,
        "score_spread": safe_round(top_score - lowest_score),
        "score_distribution": bucket_numeric_values(scores, SCORE_BUCKETS),
        "candidate_count": len(scores),
    }


def analyze_confidence(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_candidates = sort_candidates_for_analytics(candidates)
    confidences = normalized_confidences(ordered_candidates)
    low_confidence_count = len([value for value in confidences if value < 0.50])
    high_confidence_count = len([value for value in confidences if value >= 0.80])

    return {
        "average_confidence": safe_average(confidences),
        "median_confidence": safe_median(confidences),
        "lowest_confidence": min(confidences) if confidences else 0.0,
        "highest_confidence": max(confidences) if confidences else 0.0,
        "confidence_spread": safe_round((max(confidences) - min(confidences)) if confidences else 0.0),
        "low_confidence_count": low_confidence_count,
        "high_confidence_count": high_confidence_count,
        "high_confidence_ratio": candidate_ratio(high_confidence_count, len(confidences)),
    }


def analyze_hallucination_risk(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_candidates = sort_candidates_for_analytics(candidates)
    risks = normalized_hallucination_risks(ordered_candidates)
    high_risk_count = len([value for value in risks if value >= 0.30])
    low_risk_count = len([value for value in risks if value <= 0.10])

    return {
        "average_hallucination_risk": safe_average(risks),
        "low_risk_count": low_risk_count,
        "high_risk_count": high_risk_count,
        "unsafe_candidate_ratio": candidate_ratio(high_risk_count, len(risks)),
        "hallucination_distribution": bucket_numeric_values(risks, RISK_BUCKETS),
    }


def analyze_evidence_quality(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_candidates = sort_candidates_for_analytics(candidates)
    evidence_scores = normalized_evidence_scores(ordered_candidates)
    strong_count = len([value for value in evidence_scores if value >= 0.75])
    weak_count = len([value for value in evidence_scores if value < 0.45])

    return {
        "average_evidence_quality": safe_average(evidence_scores),
        "strong_evidence_count": strong_count,
        "weak_evidence_count": weak_count,
        "strong_evidence_ratio": candidate_ratio(strong_count, len(evidence_scores)),
        "evidence_quality_distribution": bucket_numeric_values(
            evidence_scores,
            EVIDENCE_BUCKETS,
        ),
    }


def analyze_skill_coverage(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_candidates = sort_candidates_for_analytics(candidates)
    skill_counts = count_candidate_skills(ordered_candidates)

    return {
        "top_skills": [
            {"skill": item["value"], "count": item["count"]}
            for item in top_count_items(skill_counts)
        ],
        "unique_skill_count": len(skill_counts),
        "skill_counts": skill_counts,
    }


def analyze_missing_skills(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_candidates = sort_candidates_for_analytics(candidates)
    missing_skill_counts = count_missing_skills(ordered_candidates)

    return {
        "top_missing_skills": [
            {"skill": item["value"], "count": item["count"]}
            for item in top_count_items(missing_skill_counts)
        ],
        "unique_missing_skill_count": len(missing_skill_counts),
        "missing_skill_counts": missing_skill_counts,
    }


def analyze_bucket_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_candidates = sort_candidates_for_analytics(candidates)
    bucket_counts = count_values(get_bucket(candidate) for candidate in ordered_candidates)

    for bucket in ("strong_match", "good_match", "potential_match", "weak_match"):
        bucket_counts.setdefault(bucket, 0)

    return {
        "bucket_counts": {
            key: bucket_counts[key]
            for key in sorted(bucket_counts)
        },
        "strong_match_count": bucket_counts.get("strong_match", 0),
        "good_match_count": bucket_counts.get("good_match", 0),
        "potential_match_count": bucket_counts.get("potential_match", 0),
        "weak_match_count": bucket_counts.get("weak_match", 0),
    }


def build_candidate_pool_summary(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ranking = analyze_ranking_distribution(candidates)
    confidence = analyze_confidence(candidates)
    skills = analyze_skill_coverage(candidates)
    buckets = analyze_bucket_distribution(candidates)

    top_skill = ""

    if skills["top_skills"]:
        top_skill = skills["top_skills"][0]["skill"]

    return {
        "total_candidates": ranking["candidate_count"],
        "strong_match_count": buckets["strong_match_count"],
        "average_score": ranking["average_score"],
        "average_confidence": confidence["average_confidence"],
        "top_skill": top_skill,
    }


def build_full_ranking_analytics(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "ranking_analytics": analyze_ranking_distribution(candidates),
        "confidence_analytics": analyze_confidence(candidates),
        "hallucination_analytics": analyze_hallucination_risk(candidates),
        "evidence_analytics": analyze_evidence_quality(candidates),
        "skill_analytics": analyze_skill_coverage(candidates),
        "missing_skill_analytics": analyze_missing_skills(candidates),
        "bucket_analytics": analyze_bucket_distribution(candidates),
        "candidate_pool_summary": build_candidate_pool_summary(candidates),
    }

