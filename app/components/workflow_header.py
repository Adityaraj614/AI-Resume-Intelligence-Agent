import streamlit as st

from app.styles.theme import render_hero, render_sidebar, render_top_navbar


def render_workflow_header(
    candidates_processed: int = 0,
    average_score: float = 0.0,
    shortlisted: int = 0,
) -> None:
    render_sidebar(active="Dashboard")
    render_top_navbar()
    render_hero(
        candidates_processed=candidates_processed,
        average_score=average_score,
        shortlisted=shortlisted,
    )
