from typing import Any, Dict, List

import streamlit as st

from app.styles.theme import render_metric_card


def render_analytics_cards(analytics_report: Dict[str, Any]) -> None:
    metrics = build_analytics_metrics(analytics_report)
    first_row = st.columns(3, gap="small")
    second_row = st.columns(3, gap="small")

    for column, metric in zip(first_row + second_row, metrics):
        with column:
            render_metric_card(metric["label"], metric["value"], metric["help"])


def build_analytics_metrics(analytics_report: Dict[str, Any]) -> List[Dict[str, str]]:
    analytics_report = analytics_report if isinstance(analytics_report, dict) else {}
    pool = analytics_report.get("candidate_pool_summary", {})
    ranking = analytics_report.get("ranking_analytics", {})
    confidence = analytics_report.get("confidence_analytics", {})
    evidence = analytics_report.get("evidence_analytics", {})
    buckets = analytics_report.get("bucket_analytics", {})
    total = int(pool.get("total_candidates", ranking.get("candidate_count", 0)) or 0)

    return [
        {"label": "Total Candidates", "value": str(total), "help": "Current ranked pool"},
        {"label": "Average Match Score", "value": f"{float(pool.get('average_score', 0.0) or 0.0):.2f}", "help": "Backend analytics mean score"},
        {"label": "Strong Matches", "value": str(buckets.get("strong_match_count", pool.get("strong_match_count", 0))), "help": "Backend bucket analytics"},
        {"label": "High Confidence", "value": str(confidence.get("high_confidence_count", 0)), "help": "Confidence >= 0.80"},
        {"label": "Strong Evidence", "value": str(evidence.get("strong_evidence_count", 0)), "help": "Evidence quality >= 0.75"},
        {"label": "Top Skill", "value": str(pool.get("top_skill", "") or "N/A"), "help": "Backend skill analytics"},
    ]
