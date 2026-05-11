from html import escape
from typing import Any, Dict, List

import streamlit as st


def render_evidence_panel(candidate: Dict[str, Any]) -> None:
    evidence_items = extract_evidence_items(candidate)
    st.markdown(
        """
        <div class="dashboard-panel-title">Retrieved Evidence</div>
        <div class="dashboard-panel-subtitle">Grounding snippets from retrieval, evidence, or candidate profile outputs.</div>
        """,
        unsafe_allow_html=True,
    )

    if not evidence_items:
        st.info(
            "No retrieved evidence is attached to this candidate yet. "
            "Once the retrieval workflow provides matched chunks, they will appear here."
        )
    else:
        for item in evidence_items:
            _render_evidence_item(item)


def extract_evidence_items(candidate: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = []

    for match in _as_list(candidate.get("matches", [])):
        if isinstance(match, dict):
            candidates.append(_evidence_from_match(match))

    top_match = candidate.get("top_match")

    if isinstance(top_match, dict):
        candidates.append(_evidence_from_match(top_match))

    for index, evidence in enumerate(_as_list(candidate.get("evidence_used", []))):
        if str(evidence).strip():
            candidates.append({
                "section": "Evidence",
                "score": "",
                "text": str(evidence).strip(),
                "source": "analysis",
                "order": 100 + index,
            })

    for index, evidence in enumerate(_as_list(candidate.get("retrieved_evidence", []))):
        if isinstance(evidence, dict):
            candidates.append(_evidence_from_match({**evidence, "_order": 200 + index}))
        elif str(evidence).strip():
            candidates.append({
                "section": "Retrieved",
                "score": "",
                "text": str(evidence).strip(),
                "source": "retrieval",
                "order": 200 + index,
            })

    return _dedupe_evidence(candidates)


def _evidence_from_match(match: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "section": match.get("section", match.get("jd_section", "Retrieved Match")),
        "score": _format_score(match.get("score", match.get("weighted_score", ""))),
        "text": match.get("chunk_text", match.get("jd_chunk_text", match.get("text", ""))),
        "source": match.get("source", "retrieval"),
        "order": int(match.get("_order", match.get("chunk_index", 0)) or 0),
    }


def _render_evidence_item(item: Dict[str, Any]) -> None:
    score_text = f" · score {item['score']}" if item.get("score") else ""
    st.markdown(
        f"""
        <div class="evidence-card">
            <div class="evidence-meta">{escape(str(item.get("section", "Evidence")))} · {escape(str(item.get("source", "retrieval")))}{escape(score_text)}</div>
            <div class="evidence-text">{escape(str(item.get("text", "")))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _dedupe_evidence(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    deduped = []

    for item in sorted(items, key=lambda value: (value.get("order", 0), value.get("section", ""))):
        text = str(item.get("text", "")).strip()

        if not text:
            continue

        key = text.lower()

        if key in seen:
            continue

        seen.add(key)
        deduped.append({**item, "text": text})

    return deduped


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _format_score(value: Any) -> str:
    if value == "":
        return ""

    return f"{float(value or 0.0):.2f}"
