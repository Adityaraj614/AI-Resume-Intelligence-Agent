from typing import Any, Dict, List

import streamlit as st

from app.components.candidate_snapshot import render_candidate_snapshot
from app.components.comparison_evidence import render_comparison_evidence
from app.components.comparison_selector import render_comparison_selector
from app.components.comparison_table import render_comparison_table
from app.state import get_comparison_data, get_ranked_candidates, initialize_session_state
from app.styles.theme import render_panel_end, render_panel_heading, render_panel_start


def render_comparison_workspace() -> None:
    initialize_session_state()
    candidates = resolve_ranked_candidates()
    comparison_data = get_comparison_data()

    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow">Comparison workspace</div>
            <h1>Candidate Comparison</h1>
            <p>Compare ranked candidates side-by-side to understand score differences, semantic signals, recruiter risks, and evidence-backed strengths.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_panel_start()
    render_panel_heading(
        "Candidate Selection",
        "Choose two candidates from the existing ranked workflow output.",
    )
    candidate_a, candidate_b = render_comparison_selector(candidates)
    render_panel_end()

    if not candidate_a or not candidate_b or candidate_a.get("candidate_id") == candidate_b.get("candidate_id"):
        render_empty_comparison_state()
        return

    left, right = st.columns(2, gap="large")

    with left:
        render_candidate_snapshot(candidate_a, "Candidate A")

    with right:
        render_candidate_snapshot(candidate_b, "Candidate B")

    render_panel_start()
    render_panel_heading(
        "Side-by-Side Comparison",
        "Compact recruiter view of ranking, confidence, fit, recommendation, and risk signals.",
    )
    render_comparison_table(candidate_a, candidate_b)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "AI Comparison Insights",
        "Deterministic comparison summary from the canonical workflow output.",
    )
    render_workflow_comparison_summary(comparison_data)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "Evidence Comparison",
        "Retrieved evidence snippets attached to each candidate, shown without fabrication.",
    )
    render_comparison_evidence(candidate_a, candidate_b)
    render_panel_end()


def resolve_ranked_candidates() -> List[Dict[str, Any]]:
    """
    Integration hook for workflow-ranked candidates.

    The comparison page consumes existing candidate dictionaries and does not
    run ranking, scoring, retrieval, or LLM comparison logic.
    """

    return get_ranked_candidates(final=True)


def render_workflow_comparison_summary(comparison_data: Dict[str, Any]) -> None:
    summary = comparison_data.get("comparison_summary", "") if isinstance(comparison_data, dict) else ""

    if summary:
        st.markdown(f'<div class="insight-card">{summary}</div>', unsafe_allow_html=True)
        return

    st.info("No comparison summary is available in the current workflow output.")


def render_empty_comparison_state() -> None:
    render_panel_start()
    render_panel_heading(
        "Comparison Not Ready",
        "Run the recruiter workflow or provide at least two ranked candidates to compare.",
    )
    st.info(
        "This workspace is ready to consume existing ranked candidates. It does not "
        "create fake comparisons or rerun scoring pipelines."
    )
    render_panel_end()


if __name__ == "__main__":
    render_comparison_workspace()
