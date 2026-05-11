from typing import Any, Dict, List, Tuple

import streamlit as st


def render_comparison_selector(candidates: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Select two candidates from an existing ranked workflow result.
    """

    if len(candidates) < 2:
        st.info("At least two ranked candidates are required for comparison.")
        return {}, {}

    ordered_candidates = _ordered_candidates(candidates)
    labels = [_candidate_label(candidate) for candidate in ordered_candidates]
    label_to_candidate = dict(zip(labels, ordered_candidates))
    default_b_index = 1 if len(labels) > 1 else 0

    left, right = st.columns(2, gap="large")

    with left:
        candidate_a_label = st.selectbox(
            "Candidate A",
            labels,
            index=0,
            key="comparison_candidate_a",
        )

    with right:
        candidate_b_label = st.selectbox(
            "Candidate B",
            labels,
            index=default_b_index,
            key="comparison_candidate_b",
        )

    candidate_a = label_to_candidate.get(candidate_a_label, {})
    candidate_b = label_to_candidate.get(candidate_b_label, {})

    if candidate_a.get("candidate_id") == candidate_b.get("candidate_id"):
        st.warning("Select two different candidates to compare ranking signals.")

    return candidate_a, candidate_b


def _ordered_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [candidate for candidate in candidates if isinstance(candidate, dict)],
        key=lambda candidate: int(
            candidate.get("rank", candidate.get("ranking_position", 9999)) or 9999
        ),
    )


def _candidate_label(candidate: Dict[str, Any]) -> str:
    name = candidate.get("candidate_name", candidate.get("candidate_id", "Unknown"))
    score = float(candidate.get("final_score", 0.0) or 0.0)
    rank = candidate.get("rank", candidate.get("ranking_position", ""))
    rank_label = f"Rank {rank} · " if rank else ""

    return f"{rank_label}{name} — Match Score {score:.2f}"
