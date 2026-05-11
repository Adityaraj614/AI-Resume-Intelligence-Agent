from typing import Any, Dict

from core.recruiter.comparison_schema import (
    normalize_comparison_output,
    validate_comparison_output,
)
from core.recruiter.comparison_utils import (
    build_candidate_summary,
    compare_numeric_signal,
)


def analyze_skill_overlap(candidate_a: Dict[str, Any],
                          candidate_b: Dict[str, Any]) -> Dict[str, Any]:
    summary_a = build_candidate_summary(candidate_a)
    summary_b = build_candidate_summary(candidate_b)
    skills_a = set(summary_a["skills"])
    skills_b = set(summary_b["skills"])

    return {
        "shared_skills": sorted(skills_a.intersection(skills_b)),
        "candidate_a_unique_skills": sorted(skills_a.difference(skills_b)),
        "candidate_b_unique_skills": sorted(skills_b.difference(skills_a)),
    }


def compare_missing_skills(candidate_a: Dict[str, Any],
                           candidate_b: Dict[str, Any]) -> Dict[str, Any]:
    summary_a = build_candidate_summary(candidate_a)
    summary_b = build_candidate_summary(candidate_b)
    missing_a = set(summary_a["missing_skills"])
    missing_b = set(summary_b["missing_skills"])

    return {
        "shared_missing_skills": sorted(missing_a.intersection(missing_b)),
        "candidate_a_missing_only": sorted(missing_a.difference(missing_b)),
        "candidate_b_missing_only": sorted(missing_b.difference(missing_a)),
        "candidate_a_missing_count": len(missing_a),
        "candidate_b_missing_count": len(missing_b),
    }


def compare_confidence_and_safety(candidate_a: Dict[str, Any],
                                  candidate_b: Dict[str, Any]) -> Dict[str, Any]:
    summary_a = build_candidate_summary(candidate_a)
    summary_b = build_candidate_summary(candidate_b)

    return {
        "confidence": compare_numeric_signal(
            summary_a,
            summary_b,
            "confidence_score",
            higher_is_better=True,
        ),
        "evidence_quality": compare_numeric_signal(
            summary_a,
            summary_b,
            "evidence_quality",
            higher_is_better=True,
        ),
        "hallucination_risk": compare_numeric_signal(
            summary_a,
            summary_b,
            "hallucination_risk",
            higher_is_better=False,
        ),
    }


def analyze_ranking_difference(candidate_a: Dict[str, Any],
                               candidate_b: Dict[str, Any]) -> Dict[str, Any]:
    summary_a = build_candidate_summary(candidate_a)
    summary_b = build_candidate_summary(candidate_b)
    ranking_delta = summary_b["ranking_position"] - summary_a["ranking_position"]
    score_delta = round(summary_a["final_score"] - summary_b["final_score"], 4)

    if summary_a["ranking_position"] == summary_b["ranking_position"]:
        higher_ranked = "tie"
    elif summary_a["ranking_position"] < summary_b["ranking_position"]:
        higher_ranked = "candidate_a"
    else:
        higher_ranked = "candidate_b"

    explanation_parts = []

    if higher_ranked == "candidate_a":
        explanation_parts.append("Candidate A ranks higher upstream")
    elif higher_ranked == "candidate_b":
        explanation_parts.append("Candidate B ranks higher upstream")
    else:
        explanation_parts.append("Candidates have the same upstream rank")

    if score_delta > 0:
        explanation_parts.append("Candidate A has the higher final score")
    elif score_delta < 0:
        explanation_parts.append("Candidate B has the higher final score")
    else:
        explanation_parts.append("both candidates have the same final score")

    return {
        "candidate_a_rank": summary_a["ranking_position"],
        "candidate_b_rank": summary_b["ranking_position"],
        "ranking_delta": ranking_delta,
        "score_delta": score_delta,
        "higher_ranked": higher_ranked,
        "ranking_explanation": "; ".join(explanation_parts) + ".",
    }


def build_tradeoff_summary(comparison_output: Dict[str, Any]) -> str:
    candidate_a = comparison_output["candidate_a"]["candidate_name"]
    candidate_b = comparison_output["candidate_b"]["candidate_name"]
    skill_overlap = comparison_output["skill_overlap"]
    safety = comparison_output["confidence_and_safety"]
    ranking = comparison_output["ranking_analysis"]
    parts = []

    if ranking["higher_ranked"] == "candidate_a":
        parts.append(f"{candidate_a} is ranked higher in the upstream ranking")
    elif ranking["higher_ranked"] == "candidate_b":
        parts.append(f"{candidate_b} is ranked higher in the upstream ranking")
    else:
        parts.append("Both candidates have the same upstream ranking position")

    if skill_overlap["shared_skills"]:
        parts.append(
            f"both share {len(skill_overlap['shared_skills'])} retrieved skills"
        )
    else:
        parts.append("no shared retrieved skills are listed")

    if safety["evidence_quality"]["preferred"] == "candidate_a":
        parts.append(f"{candidate_a} has stronger evidence quality")
    elif safety["evidence_quality"]["preferred"] == "candidate_b":
        parts.append(f"{candidate_b} has stronger evidence quality")
    else:
        parts.append("evidence quality is tied")

    if safety["hallucination_risk"]["preferred"] == "candidate_a":
        parts.append(f"{candidate_a} has lower hallucination risk")
    elif safety["hallucination_risk"]["preferred"] == "candidate_b":
        parts.append(f"{candidate_b} has lower hallucination risk")
    else:
        parts.append("hallucination risk is tied")

    return "; ".join(parts) + "."


def compare_candidates(candidate_a: Dict[str, Any],
                       candidate_b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a deterministic side-by-side comparison for two candidates.
    """

    comparison_output = {
        "candidate_a": build_candidate_summary(candidate_a),
        "candidate_b": build_candidate_summary(candidate_b),
        "skill_overlap": analyze_skill_overlap(candidate_a, candidate_b),
        "missing_skill_comparison": compare_missing_skills(candidate_a, candidate_b),
        "confidence_and_safety": compare_confidence_and_safety(candidate_a, candidate_b),
        "ranking_analysis": analyze_ranking_difference(candidate_a, candidate_b),
    }
    comparison_output["comparison_summary"] = build_tradeoff_summary(comparison_output)
    normalized_output = normalize_comparison_output(comparison_output)

    if not validate_comparison_output(normalized_output):
        raise ValueError("Candidate comparison output failed schema validation.")

    return normalized_output

