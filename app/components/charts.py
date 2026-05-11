from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_bar_distribution(title: str, distribution: Dict[str, int]) -> None:
    st.markdown(
        f"""
        <div class="dashboard-panel-title">{escape(title)}</div>
        <div class="dashboard-panel-subtitle">Compact distribution for recruiter review.</div>
        """,
        unsafe_allow_html=True,
    )

    if not distribution:
        st.info("No candidate data available yet.")
    else:
        max_value = max(distribution.values()) or 1

        for label, value in distribution.items():
            _render_bar(label, value, max_value)


def recommendation_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    distribution = {
        "Interview": 0,
        "Consider": 0,
        "Reject": 0,
    }

    for candidate in candidates:
        recommendation = str(candidate.get("recommendation", "")).lower()

        if "reject" in recommendation or "weak" in recommendation:
            distribution["Reject"] += 1
        elif "interview" in recommendation or "strong" in recommendation:
            distribution["Interview"] += 1
        else:
            distribution["Consider"] += 1

    return distribution


def confidence_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    distribution = {
        "High": 0,
        "Medium": 0,
        "Low": 0,
    }

    for candidate in candidates:
        confidence = float(candidate.get("confidence", candidate.get("confidence_score", 0.0)) or 0.0)

        if confidence >= 0.8:
            distribution["High"] += 1
        elif confidence >= 0.5:
            distribution["Medium"] += 1
        else:
            distribution["Low"] += 1

    return distribution


def source_distribution(candidates: List[Dict[str, Any]]) -> Dict[str, int]:
    distribution = {
        "Resume": 0,
        "LinkedIn": 0,
    }

    for candidate in candidates:
        source = str(candidate.get("source", "resume")).lower()

        if source == "linkedin":
            distribution["LinkedIn"] += 1
        else:
            distribution["Resume"] += 1

    return distribution


def confidence_distribution_from_analytics(analytics_report: Dict[str, Any]) -> Dict[str, int]:
    confidence = analytics_report.get("confidence_analytics", {}) if isinstance(analytics_report, dict) else {}
    ranking = analytics_report.get("ranking_analytics", {}) if isinstance(analytics_report, dict) else {}
    total = int(ranking.get("candidate_count", 0) or 0)
    high = int(confidence.get("high_confidence_count", 0) or 0)
    low = int(confidence.get("low_confidence_count", 0) or 0)
    return {
        "High": high,
        "Medium": max(total - high - low, 0),
        "Low": low,
    }


def score_distribution_from_analytics(analytics_report: Dict[str, Any]) -> Dict[str, int]:
    ranking = analytics_report.get("ranking_analytics", {}) if isinstance(analytics_report, dict) else {}
    distribution = ranking.get("score_distribution", {})
    return _title_distribution(distribution)


def evidence_distribution_from_analytics(analytics_report: Dict[str, Any]) -> Dict[str, int]:
    evidence = analytics_report.get("evidence_analytics", {}) if isinstance(analytics_report, dict) else {}
    distribution = evidence.get("evidence_quality_distribution", {})
    return _title_distribution(distribution)


def bucket_distribution_from_analytics(analytics_report: Dict[str, Any]) -> Dict[str, int]:
    buckets = analytics_report.get("bucket_analytics", {}) if isinstance(analytics_report, dict) else {}
    distribution = buckets.get("bucket_counts", {})
    return {
        str(label).replace("_", " ").title(): int(value or 0)
        for label, value in distribution.items()
    }


def _title_distribution(distribution: Dict[str, Any]) -> Dict[str, int]:
    if not isinstance(distribution, dict):
        return {}

    return {
        str(label).replace("_", " ").title(): int(value or 0)
        for label, value in distribution.items()
    }


def _render_bar(label: str, value: int, max_value: int) -> None:
    width = int(round((value / max_value) * 100)) if max_value else 0
    st.markdown(
        f"""
        <div class="chart-row">
            <div class="chart-label-row">
                <span>{escape(label)}</span>
                <span>{value}</span>
            </div>
            <div class="chart-track">
                <div class="chart-fill" style="width:{width}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
