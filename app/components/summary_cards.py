from typing import Any, Dict, List

import streamlit as st

from app.styles.theme import render_metric_card


def render_summary_cards(workflow_result: Dict[str, Any] = None) -> None:
    metrics = build_summary_metrics(workflow_result or {})
    columns = st.columns(4, gap="small")

    for column, metric in zip(columns, metrics):
        with column:
            render_metric_card(
                label=metric["label"],
                value=metric["value"],
                help_text=metric["help"],
                icon=metric["icon"],
                trend=metric["trend"],
            )


def build_summary_metrics(workflow_result: Dict[str, Any]) -> List[Dict[str, str]]:
    outputs = workflow_result.get("workflow_outputs", {}) if isinstance(workflow_result, dict) else {}
    metadata = workflow_result.get("workflow_metadata", {}) if isinstance(workflow_result, dict) else {}
    ranked_candidates = outputs.get("ranked_candidates", [])
    shortlist = outputs.get("shortlist", [])
    decision_support = outputs.get("decision_support", {})
    analytics_report = outputs.get("analytics_report", {})
    pool_summary = analytics_report.get("candidate_pool_summary", {}) if isinstance(analytics_report, dict) else {}
    hallucination = analytics_report.get("hallucination_analytics", {}) if isinstance(analytics_report, dict) else {}
    top_candidate = ranked_candidates[0] if ranked_candidates else {}
    average_score = float(pool_summary.get("average_score", 0.0) or 0.0)
    normalized_average_score = _score_to_percent(average_score)
    top_score = _score_to_percent(float(top_candidate.get("final_score", 0.0) or 0.0))
    jd_strength = top_score if ranked_candidates else normalized_average_score
    risk_count = _risk_count(decision_support, hallucination)
    candidate_count = int(metadata.get("candidate_count", len(ranked_candidates)) or 0)

    return [
        {
            "label": "Candidates Processed",
            "value": str(candidate_count),
            "help": "Resume PDFs and LinkedIn profiles",
            "icon": "CP",
            "trend": "Live",
        },
        {
            "label": "Average Match Score",
            "value": f"{normalized_average_score:.0f}%",
            "help": "Mean score across ranked candidates",
            "icon": "MS",
            "trend": "+AI",
        },
        {
            "label": "Shortlisted Candidates",
            "value": str(len(shortlist)),
            "help": "Recruiter-safe shortlist",
            "icon": "SL",
            "trend": "Ready",
        },
        {
            "label": "JD Match Strength",
            "value": f"{jd_strength:.0f}%",
            "help": f"Top-fit signal, {risk_count} risk flags",
            "icon": "JD",
            "trend": "Stable",
        },
    ]


def _risk_count(
    decision_support: Dict[str, Any],
    hallucination_analytics: Dict[str, Any],
) -> int:
    risk_summary = decision_support.get("risk_summary", {}) if isinstance(decision_support, dict) else {}
    high_risk_count = int(hallucination_analytics.get("high_risk_count", 0) or 0)

    return high_risk_count + sum(int(value) for value in risk_summary.values())


def _score_to_percent(score: float) -> float:
    if score <= 1:
        return max(0.0, min(score * 100, 100.0))

    return max(0.0, min(score, 100.0))
