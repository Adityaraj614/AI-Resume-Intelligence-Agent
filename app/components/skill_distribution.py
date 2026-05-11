from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_skill_distribution(candidates: List[Dict[str, Any]], limit: int = 8) -> None:
    skills = top_skills(candidates, limit=limit)
    render_skill_distribution_rows(skills)


def render_skill_distribution_from_analytics(analytics_report: Dict[str, Any], limit: int = 8) -> None:
    skill_analytics = analytics_report.get("skill_analytics", {}) if isinstance(analytics_report, dict) else {}
    skills = skill_analytics.get("top_skills", [])

    if isinstance(skills, list):
        skills = skills[:limit]
    else:
        skills = []

    render_skill_distribution_rows(skills)


def render_skill_distribution_rows(skills: List[Dict[str, Any]]) -> None:
    st.markdown(
        """
        <div class="dashboard-panel-title">Skill Distribution</div>
        <div class="dashboard-panel-subtitle">Most common candidate skills from backend analytics.</div>
        """,
        unsafe_allow_html=True,
    )

    if not skills:
        st.info("No skill data available yet.")
    else:
        for skill in skills:
            st.markdown(
                f"""
                <div class="skill-row">
                    <div class="skill-name">{escape(str(skill["skill"]))}</div>
                    <div class="skill-count">{escape(str(skill["count"]))} candidates</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def top_skills(candidates: List[Dict[str, Any]], limit: int = 8) -> List[Dict[str, Any]]:
    counts: Dict[str, int] = {}
    display_names: Dict[str, str] = {}

    for candidate in candidates:
        skills = candidate.get("extracted_skills", candidate.get("skills", []))

        if not isinstance(skills, list):
            skills = [skills]

        for skill in skills:
            normalized = str(skill).strip()

            if not normalized:
                continue

            key = normalized.lower()
            counts[key] = counts.get(key, 0) + 1
            display_names.setdefault(key, normalized)

    return [
        {
            "skill": display_names[key],
            "count": counts[key],
        }
        for key in sorted(counts, key=lambda item: (-counts[item], item))[:limit]
    ]
