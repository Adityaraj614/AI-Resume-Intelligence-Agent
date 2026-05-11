from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import streamlit as st

from app.components.audit_timeline import render_audit_timeline
from app.components.original_vs_override import (
    render_original_ai_output,
    render_original_vs_override,
)
from app.components.override_controls import render_override_controls
from app.components.override_summary import render_override_summary
from app.components.reviewer_card import render_reviewer_card
from app.state import (
    get_override_history as get_canonical_override_history,
    get_override_results,
    get_ranked_candidates,
    initialize_session_state,
    record_override_result,
    set_selected_candidate,
)
from app.styles.theme import apply_theme, render_panel_end, render_panel_heading, render_panel_start
from core.human_review.override_engine import apply_override
from core.human_review.override_history import append_override_event, get_override_history
from core.human_review.reviewer_registry import normalize_reviewer_metadata
from core.human_review.review_schema import OverrideDecision


def render_override_workspace() -> None:
    apply_theme()
    initialize_session_state()
    candidates = resolve_ranked_candidates()

    st.markdown(
        """
        <div class="page-heading">
            <div class="eyebrow">Human review workspace</div>
            <h1>Override & Audit</h1>
            <p>Review original AI recommendations, apply recruiter-visible overrides, and inspect the audit trail behind every change.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_panel_start()
    render_panel_heading(
        "Candidate Selection",
        "Choose a candidate from the existing ranked workflow output.",
    )
    selected_candidate = render_candidate_selector(candidates)
    render_panel_end()

    if not selected_candidate:
        render_empty_override_state()
        return

    candidate_id = str(selected_candidate.get("candidate_id", ""))
    current_result = _current_presented_result(selected_candidate)
    set_selected_candidate(current_result)
    candidate_history = get_override_history(st.session_state["override_history"], candidate_id)
    latest_entry = candidate_history.get("entries", [])[-1] if candidate_history.get("entries") else {}

    left, right = st.columns([0.68, 0.32], gap="large")

    with left:
        render_panel_start()
        render_panel_heading(
            "Original AI Recommendation",
            "Read-only AI output preserved from the ranking workflow.",
        )
        render_original_ai_output(selected_candidate)
        render_panel_end()

    with right:
        render_reviewer_card(st.session_state.get("override_reviewer_name", ""), latest_entry)

    render_panel_start()
    render_panel_heading(
        "Recruiter Override Controls",
        "Apply presentation-layer human review decisions through the existing override backend.",
    )
    form_data = render_override_controls(selected_candidate, current_result)
    render_panel_end()

    if form_data.get("submitted"):
        _handle_override_submit(selected_candidate, current_result, form_data)
        st.rerun()

    current_result = _current_presented_result(selected_candidate)
    candidate_history = get_override_history(st.session_state["override_history"], candidate_id)

    render_panel_start()
    render_panel_heading(
        "Final Recruiter Decision",
        "Transparent comparison between the original AI output and the recruiter-facing result.",
    )
    render_original_vs_override(selected_candidate, current_result)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "Audit Timeline",
        "Chronological override history with reviewer, timestamp, reason, and before/after values.",
    )
    render_audit_timeline(candidate_history)
    render_panel_end()

    render_panel_start()
    render_panel_heading(
        "Override Summary",
        "Concise summary derived only from recorded override data.",
    )
    render_override_summary(candidate_history, current_result)
    render_panel_end()


def resolve_ranked_candidates() -> List[Dict[str, Any]]:
    """
    Consume existing workflow-ranked candidates without rerunning scoring,
    retrieval, ranking, or LLM logic.
    """

    return get_ranked_candidates(final=False)


def render_candidate_selector(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    ordered_candidates = _ordered_candidates(candidates)

    if not ordered_candidates:
        st.info("Run the recruiter workflow to populate ranked candidates for override review.")
        return {}

    selected_index = st.selectbox(
        "Candidate",
        range(len(ordered_candidates)),
        format_func=lambda index: _candidate_label(ordered_candidates[index]),
        key="override_candidate_index",
    )

    selected_candidate = ordered_candidates[selected_index]

    return selected_candidate


def render_empty_override_state() -> None:
    render_panel_start()
    render_panel_heading(
        "Override Workspace Not Ready",
        "This interface is ready to visualize existing ranked candidates and human review history.",
    )
    st.info(
        "No candidate data was found in workflow outputs. The page does not fabricate "
        "AI recommendations or audit records."
    )
    render_panel_end()


def _handle_override_submit(
    selected_candidate: Dict[str, Any],
    current_result: Dict[str, Any],
    form_data: Dict[str, Any],
) -> None:
    candidate_id = str(selected_candidate.get("candidate_id", ""))
    reviewer_name = _clean_text(form_data.get("reviewer_name"))
    reason = _clean_text(form_data.get("override_reason"))
    changes = _build_changed_decisions(current_result, form_data)

    if not changes:
        st.info("No override was applied because the final recruiter decision already matches the form values.")
        return

    if not reviewer_name:
        st.warning("Enter the recruiter reviewer name before applying an override.")
        return

    if not reason:
        st.warning("Enter a short override reason before applying an override.")
        return

    reviewer = normalize_reviewer_metadata(reviewer_name, source="override_interface")
    timestamp = _current_review_timestamp()
    final_result = current_result
    applied_count = 0

    try:
        for override_type, payload in changes:
            decision = OverrideDecision(
                candidate_id=candidate_id,
                override_type=override_type,
                reviewer=reviewer,
                reason=reason,
                timestamp=timestamp,
                source="override_interface",
                **payload,
            )
            reviewed = apply_override(final_result, decision)
            final_result = reviewed["final_presented_result"]
            updated_history = append_override_event(
                get_canonical_override_history(),
                reviewed["audit_entry"],
            )
            st.session_state["override_history"] = updated_history
            applied_count += 1
    except ValueError as exc:
        st.warning(str(exc))
        return

    record_override_result(candidate_id, final_result, get_canonical_override_history())
    st.success(f"Applied {applied_count} recruiter override event(s) and updated the audit timeline.")


def _build_changed_decisions(
    current_result: Dict[str, Any],
    form_data: Dict[str, Any],
) -> List[Tuple[str, Dict[str, Any]]]:
    changes: List[Tuple[str, Dict[str, Any]]] = []
    current_score = _score(current_result)
    score_override = float(form_data.get("score_override", current_score) or 0.0)

    if round(score_override, 4) != round(current_score, 4):
        changes.append(("score_override", {"override_score": score_override}))

    current_recommendation = _clean_text(current_result.get("recommendation", "Needs Review"))
    recommendation_override = _clean_text(form_data.get("recommendation_override"))

    if recommendation_override and recommendation_override != current_recommendation:
        changes.append((
            "recommendation_override",
            {"override_recommendation": recommendation_override},
        ))

    current_shortlist = _clean_text(
        current_result.get("shortlist_status", _shortlist_label(current_result))
    )
    shortlist_override = _clean_text(form_data.get("shortlist_override"))

    if shortlist_override and shortlist_override != current_shortlist:
        changes.append(("shortlist_override", {"shortlist_status": shortlist_override}))

    current_notes = _clean_text(current_result.get("review_notes", ""))
    recruiter_notes = _clean_text(form_data.get("recruiter_notes"))

    if recruiter_notes and recruiter_notes != current_notes:
        changes.append(("recruiter_notes", {"review_notes": recruiter_notes}))

    return changes


def _current_presented_result(candidate: Dict[str, Any]) -> Dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id", ""))
    override_results = get_override_results()

    if isinstance(override_results, dict) and isinstance(override_results.get(candidate_id), dict):
        return override_results[candidate_id]

    return dict(candidate)


def _ordered_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        [candidate for candidate in candidates if isinstance(candidate, dict)],
        key=lambda candidate: (
            int(candidate.get("rank", candidate.get("ranking_position", 9999)) or 9999),
            str(candidate.get("candidate_name", candidate.get("name", ""))).lower(),
            str(candidate.get("candidate_id", "")),
        ),
    )


def _candidate_label(candidate: Dict[str, Any]) -> str:
    name = candidate.get("candidate_name", candidate.get("name", "Unknown Candidate"))
    score = _score(candidate)
    rank = candidate.get("rank", candidate.get("ranking_position", ""))
    rank_label = f"Rank {rank} · " if rank else ""

    return f"{rank_label}{name} — Match Score {score:.2f}"


def _score(candidate: Dict[str, Any]) -> float:
    if "final_score" in candidate:
        return float(candidate.get("final_score", 0.0) or 0.0)

    return float(candidate.get("score", 0.0) or 0.0)


def _shortlist_label(candidate: Dict[str, Any]) -> str:
    if candidate.get("is_shortlisted") is True:
        return "Shortlisted"

    if candidate.get("is_shortlisted") is False:
        return "No Decision"

    return "No Decision"


def _current_review_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


if __name__ == "__main__":
    render_override_workspace()
