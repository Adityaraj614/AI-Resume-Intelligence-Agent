from typing import Any, Dict, List

import streamlit as st


PREVIEW_COLUMNS = (
    "Rank",
    "Candidate",
    "Final Score",
    "Recommendation",
    "Override Status",
    "Recruiter Notes",
)


def render_export_preview(
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
    limit: int = 8,
) -> None:
    rows = build_export_preview_rows(final_candidates, override_history, limit=limit)

    if not rows:
        st.info("No export preview is available until ranked candidates exist.")
        st.dataframe([], width="stretch", hide_index=True)
        return

    st.dataframe(
        rows,
        column_order=list(PREVIEW_COLUMNS),
        width="stretch",
        hide_index=True,
    )
    st.caption(f"Previewing {len(rows)} of {len(final_candidates)} export rows.")


def build_export_preview_rows(
    final_candidates: List[Dict[str, Any]],
    override_history: List[Dict[str, Any]],
    limit: int = 8,
) -> List[Dict[str, str]]:
    overridden_ids = {
        str(entry.get("candidate_id", ""))
        for entry in override_history
        if isinstance(entry, dict) and entry.get("candidate_id")
    }

    rows = []

    for index, candidate in enumerate(final_candidates[:limit], start=1):
        candidate_id = str(candidate.get("candidate_id", ""))
        rows.append({
            "Rank": str(candidate.get("rank", candidate.get("ranking_position", index))),
            "Candidate": str(candidate.get("candidate_name", candidate.get("name", candidate_id or "Unknown"))),
            "Final Score": f"{float(candidate.get('final_score', candidate.get('score', 0.0)) or 0.0):.2f}",
            "Recommendation": str(candidate.get("recommendation", "Needs Review")),
            "Override Status": "Override Applied" if candidate_id in overridden_ids else "AI Result",
            "Recruiter Notes": str(candidate.get("review_notes", "")) or "None",
        })

    return rows
