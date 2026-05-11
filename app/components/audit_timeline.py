from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_audit_timeline(history: Dict[str, Any]) -> None:
    entries = history.get("entries", []) if isinstance(history, dict) else []

    if not entries:
        st.info("No recruiter overrides have been recorded for this candidate yet.")
        return

    for entry in entries:
        st.markdown(_timeline_card(entry), unsafe_allow_html=True)


def _timeline_card(entry: Dict[str, Any]) -> str:
    reviewer = entry.get("reviewer", {}) if isinstance(entry.get("reviewer"), dict) else {}
    reviewer_name = reviewer.get("reviewer_name", "Unknown reviewer")
    timestamp = entry.get("timestamp", "not_provided")
    override_type = _override_label(entry.get("override_type", "Override"))
    reason = entry.get("reason", "")
    changes = _change_lines(entry.get("before", {}), entry.get("after", {}))

    return f"""
    <div class="evidence-card" style="border-left:4px solid #2563EB;">
        <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;">
            <div>
                <div style="color:#111827;font-weight:750;font-size:0.98rem;">
                    {escape(str(reviewer_name))} changed {escape(override_type)}
                </div>
                <div class="candidate-meta" style="margin-top:0.2rem;">{escape(str(timestamp))}</div>
            </div>
            <span class="status-badge">{escape(override_type)}</span>
        </div>
        <div style="color:#111827;font-size:0.94rem;line-height:1.5;margin-top:0.7rem;">
            {changes}
        </div>
        <div style="color:#6B7280;font-size:0.9rem;line-height:1.45;margin-top:0.65rem;">
            Reason: {escape(str(reason or "No reason recorded"))}
        </div>
    </div>
    """


def _change_lines(before: Dict[str, Any], after: Dict[str, Any]) -> str:
    if not isinstance(before, dict) or not isinstance(after, dict):
        return "No before or after values were recorded."

    keys = sorted(set(before) | set(after))

    if not keys:
        return "No field changes were recorded."

    return "<br>".join(
        f"<strong>{escape(_field_label(key))}:</strong> "
        f"{escape(_format_value(before.get(key)))} &rarr; {escape(_format_value(after.get(key)))}"
        for key in keys
    )


def _override_label(value: Any) -> str:
    return str(value or "override").replace("_", " ").title()


def _field_label(value: Any) -> str:
    return str(value or "").replace("_", " ").title()


def _format_value(value: Any) -> str:
    if value is None:
        return "None"

    if isinstance(value, float):
        return f"{value:.2f}"

    return " ".join(str(value).strip().split()) or "None"
