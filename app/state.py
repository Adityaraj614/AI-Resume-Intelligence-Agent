from copy import deepcopy
from typing import Any, Dict, List

import streamlit as st


CANONICAL_KEYS = (
    "workflow_result",
    "ranked_candidates",
    "candidate_profiles",
    "analytics",
    "comparison_data",
    "audit_data",
    "selected_candidate",
    "override_history",
    "override_results",
)


def initialize_session_state() -> None:
    st.session_state.setdefault("workflow_result", {})
    st.session_state.setdefault("ranked_candidates", [])
    st.session_state.setdefault("candidate_profiles", [])
    st.session_state.setdefault("analytics", {})
    st.session_state.setdefault("comparison_data", {})
    st.session_state.setdefault("audit_data", [])
    st.session_state.setdefault("override_history", [])
    st.session_state.setdefault("override_results", {})


def set_workflow_result(workflow_result: Dict[str, Any]) -> None:
    if not isinstance(workflow_result, dict):
        workflow_result = {}

    st.session_state["workflow_result"] = workflow_result
    st.session_state["ranked_candidates"] = _workflow_output("ranked_candidates", [])
    st.session_state["candidate_profiles"] = _workflow_output("candidate_profiles", [])
    st.session_state["analytics"] = _workflow_output("analytics_report", {})
    st.session_state["comparison_data"] = _workflow_output("comparison_report", {})
    st.session_state["audit_data"] = get_override_history()

    _sync_final_candidates()
    _sync_selected_candidate()


def get_workflow_result() -> Dict[str, Any]:
    initialize_session_state()
    workflow_result = st.session_state.get("workflow_result", {})
    return workflow_result if isinstance(workflow_result, dict) else {}


def get_workflow_outputs() -> Dict[str, Any]:
    workflow_result = get_workflow_result()
    outputs = workflow_result.get("workflow_outputs", {})
    return outputs if isinstance(outputs, dict) else {}


def get_ranked_candidates(final: bool = False) -> List[Dict[str, Any]]:
    initialize_session_state()

    if final:
        final_candidates = _workflow_output("final_ranked_candidates", [])

        if isinstance(final_candidates, list) and final_candidates:
            return [candidate for candidate in final_candidates if isinstance(candidate, dict)]

    candidates = st.session_state.get("ranked_candidates", [])
    return [candidate for candidate in candidates if isinstance(candidate, dict)] if isinstance(candidates, list) else []


def get_candidate_profiles() -> List[Dict[str, Any]]:
    initialize_session_state()
    profiles = st.session_state.get("candidate_profiles", [])
    return [profile for profile in profiles if isinstance(profile, dict)] if isinstance(profiles, list) else []


def get_analytics() -> Dict[str, Any]:
    initialize_session_state()
    analytics = st.session_state.get("analytics", {})
    return analytics if isinstance(analytics, dict) else {}


def get_comparison_data() -> Dict[str, Any]:
    initialize_session_state()
    comparison_data = st.session_state.get("comparison_data", {})
    return comparison_data if isinstance(comparison_data, dict) else {}


def get_override_history() -> List[Dict[str, Any]]:
    initialize_session_state()
    history = st.session_state.get("override_history", [])
    return [entry for entry in history if isinstance(entry, dict)] if isinstance(history, list) else []


def get_override_results() -> Dict[str, Dict[str, Any]]:
    initialize_session_state()
    results = st.session_state.get("override_results", {})
    return results if isinstance(results, dict) else {}


def get_selected_candidate() -> Dict[str, Any]:
    initialize_session_state()
    _sync_selected_candidate()
    selected = st.session_state.get("selected_candidate", {})
    return selected if isinstance(selected, dict) else {}


def set_selected_candidate(candidate: Dict[str, Any]) -> None:
    if isinstance(candidate, dict):
        st.session_state["selected_candidate"] = candidate


def record_override_result(candidate_id: str, final_result: Dict[str, Any], audit_history: List[Dict[str, Any]]) -> None:
    initialize_session_state()
    override_results = get_override_results()

    if candidate_id and isinstance(final_result, dict):
        override_results[candidate_id] = final_result

    st.session_state["override_results"] = override_results
    st.session_state["override_history"] = audit_history if isinstance(audit_history, list) else []
    st.session_state["audit_data"] = st.session_state["override_history"]
    _sync_final_candidates()
    _sync_selected_candidate(prefer_candidate_id=candidate_id)


def reset_review_state() -> None:
    st.session_state["override_history"] = []
    st.session_state["override_results"] = {}
    st.session_state["audit_data"] = []
    _sync_final_candidates()


def has_workflow() -> bool:
    return bool(get_ranked_candidates())


def _workflow_output(key: str, default: Any) -> Any:
    outputs = get_workflow_outputs()
    value = outputs.get(key, default)
    return value if value is not None else default


def _sync_final_candidates() -> None:
    workflow_result = get_workflow_result()
    outputs = workflow_result.get("workflow_outputs", {})

    if not isinstance(outputs, dict):
        return

    override_results = get_override_results()
    final_candidates = []

    for candidate in get_ranked_candidates(final=False):
        candidate_id = str(candidate.get("candidate_id", ""))
        final_candidates.append(deepcopy(override_results.get(candidate_id, candidate)))

    outputs["final_ranked_candidates"] = final_candidates
    workflow_result["workflow_outputs"] = outputs
    st.session_state["workflow_result"] = workflow_result


def _sync_selected_candidate(prefer_candidate_id: str = "") -> None:
    candidates = get_ranked_candidates(final=True)

    if not candidates:
        st.session_state["selected_candidate"] = {}
        return

    selected = st.session_state.get("selected_candidate", {})
    selected_id = prefer_candidate_id or (selected.get("candidate_id", "") if isinstance(selected, dict) else "")
    candidates_by_id = {
        str(candidate.get("candidate_id", "")): candidate
        for candidate in candidates
    }

    st.session_state["selected_candidate"] = candidates_by_id.get(selected_id, candidates[0])
