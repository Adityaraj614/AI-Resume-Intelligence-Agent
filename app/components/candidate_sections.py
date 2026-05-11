from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_candidate_sections(candidate: Dict[str, Any]) -> None:
    st.markdown(
        """
        <div class="info-card">
            <div class="dashboard-panel-title">Structured Candidate Sections</div>
            <div class="dashboard-panel-subtitle">Candidate profile details organized for recruiter review.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sections = build_candidate_sections(candidate)

    for section in sections:
        with st.expander(section["title"], expanded=section["expanded"]):
            if section["items"]:
                st.markdown(_render_list(section["items"]), unsafe_allow_html=True)
            else:
                st.caption("No structured data available for this section.")


def build_candidate_sections(candidate: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "title": "Skills",
            "items": _simple_items(candidate.get("extracted_skills", candidate.get("skills", []))),
            "expanded": True,
        },
        {
            "title": "Experience",
            "items": _structured_items(candidate.get("experience", []), ("title", "company", "description")),
            "expanded": True,
        },
        {
            "title": "Education",
            "items": _structured_items(candidate.get("education", []), ("school", "degree", "field_of_study")),
            "expanded": False,
        },
        {
            "title": "Projects",
            "items": _simple_items(candidate.get("projects", [])),
            "expanded": False,
        },
        {
            "title": "Certifications",
            "items": _structured_items(candidate.get("certifications", []), ("name", "issuer", "issue_date")),
            "expanded": False,
        },
    ]


def _simple_items(value: Any) -> List[str]:
    if value is None:
        return []

    values = value if isinstance(value, list) else [value]

    return [str(item).strip() for item in values if str(item).strip()]


def _structured_items(value: Any, fields: tuple) -> List[str]:
    if value is None:
        return []

    values = value if isinstance(value, list) else [value]
    items = []

    for entry in values:
        if isinstance(entry, dict):
            parts = [str(entry.get(field, "")).strip() for field in fields]
            text = " | ".join(part for part in parts if part)
        else:
            text = str(entry).strip()

        if text:
            items.append(text)

    return items


def _render_list(items: List[str]) -> str:
    rendered_items = "".join(f"<li>{escape(item)}</li>" for item in items)
    return f'<ul class="section-list">{rendered_items}</ul>'
