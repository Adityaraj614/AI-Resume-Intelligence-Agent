from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_override_summary(history: Dict[str, Any], final_result: Dict[str, Any]) -> None:
    entries = history.get("entries", []) if isinstance(history, dict) else []
    summaries = build_override_summary_lines(entries, final_result)

    for line in summaries:
        st.markdown(
            f"""
            <div class="insight-card">
                {escape(line)}
            </div>
            """,
            unsafe_allow_html=True,
        )


def build_override_summary_lines(
    entries: List[Dict[str, Any]],
    final_result: Dict[str, Any],
) -> List[str]:
    if not entries:
        return [
            "No recruiter override has been applied. The final result currently matches the AI recommendation."
        ]

    latest = entries[-1]
    reason = _text(latest.get("reason", ""))
    reviewer = latest.get("reviewer", {}) if isinstance(latest.get("reviewer"), dict) else {}
    reviewer_name = _text(reviewer.get("reviewer_name", "the reviewer"))
    changed_fields = _changed_fields(entries)
    lines = [
        f"{reviewer_name} most recently updated {latest.get('override_type', 'override').replace('_', ' ')}."
    ]

    if reason:
        lines.append(f"Recorded reason: {reason}")

    if changed_fields:
        lines.append(f"Audited fields changed: {', '.join(changed_fields)}.")

    notes = _text(final_result.get("review_notes", ""))

    if notes:
        lines.append(f"Reviewer notes: {notes}")

    return lines


def _changed_fields(entries: List[Dict[str, Any]]) -> List[str]:
    fields = set()

    for entry in entries:
        before = entry.get("before", {}) if isinstance(entry, dict) else {}
        after = entry.get("after", {}) if isinstance(entry, dict) else {}

        if not isinstance(before, dict) or not isinstance(after, dict):
            continue

        for key in set(before) | set(after):
            if before.get(key) != after.get(key):
                fields.add(key.replace("_", " ").title())

    return sorted(fields)


def _text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())
