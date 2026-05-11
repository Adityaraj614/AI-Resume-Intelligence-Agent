from typing import Any, Dict, List

from core.recruiter.comparison_schema import (
    normalize_multi_comparison_output,
    validate_multi_comparison_output,
)
from core.recruiter.comparison_utils import (
    build_candidate_summary,
    normalize_strengths,
    normalize_candidate_skills,
    sort_candidates_for_comparison,
)


def build_ranking_overview(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "candidate_id": summary["candidate_id"],
            "candidate_name": summary["candidate_name"],
            "ranking_position": summary["ranking_position"],
            "final_score": summary["final_score"],
            "bucket": summary["bucket"],
        }
        for summary in [
            build_candidate_summary(candidate)
            for candidate in sort_candidates_for_comparison(candidates)
        ]
    ]


def build_comparison_table(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        build_candidate_summary(candidate)
        for candidate in sort_candidates_for_comparison(candidates)
    ]


def build_skill_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    distribution: Dict[str, List[str]] = {}

    for candidate in sort_candidates_for_comparison(candidates):
        summary = build_candidate_summary(candidate)

        for skill in normalize_candidate_skills(candidate):
            distribution.setdefault(skill, []).append(summary["candidate_id"])

    return {
        skill: sorted(candidate_ids)
        for skill, candidate_ids in sorted(distribution.items())
    }


def build_strength_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    distribution: Dict[str, List[str]] = {}

    for candidate in sort_candidates_for_comparison(candidates):
        summary = build_candidate_summary(candidate)

        for strength in normalize_strengths(candidate):
            distribution.setdefault(strength, []).append(summary["candidate_id"])

    return {
        strength: sorted(candidate_ids)
        for strength, candidate_ids in sorted(distribution.items())
    }


def build_multi_comparison_summary(comparison_table: List[Dict[str, Any]]) -> str:
    if not comparison_table:
        return "No candidates available for comparison."

    top_candidate = comparison_table[0]
    strongest_evidence = max(
        comparison_table,
        key=lambda candidate: (
            candidate["evidence_quality"],
            -candidate["hallucination_risk"],
            -candidate["ranking_position"],
        ),
    )
    safest_candidate = min(
        comparison_table,
        key=lambda candidate: (
            candidate["hallucination_risk"],
            -candidate["evidence_quality"],
            candidate["ranking_position"],
        ),
    )

    return (
        f"{top_candidate['candidate_name']} is first by upstream ranking; "
        f"{strongest_evidence['candidate_name']} has the strongest evidence quality; "
        f"{safest_candidate['candidate_name']} has the lowest hallucination risk."
    )


def compare_multiple_candidates(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a deterministic multi-candidate comparison view.
    """

    if not isinstance(candidates, list):
        raise TypeError("candidates must be a list.")

    ordered_candidates = sort_candidates_for_comparison(candidates)
    comparison_table = build_comparison_table(ordered_candidates)
    multi_comparison = normalize_multi_comparison_output({
        "candidate_count": len(comparison_table),
        "ranking_overview": build_ranking_overview(ordered_candidates),
        "comparison_table": comparison_table,
        "skill_distribution": build_skill_distribution(ordered_candidates),
        "strength_distribution": build_strength_distribution(ordered_candidates),
        "comparison_summary": build_multi_comparison_summary(comparison_table),
    })

    if not validate_multi_comparison_output(multi_comparison):
        raise ValueError("Multi-candidate comparison output failed schema validation.")

    return multi_comparison

