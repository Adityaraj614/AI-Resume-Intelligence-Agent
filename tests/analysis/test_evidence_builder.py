from core.llm.evidence_builder import build_evidence_context


def _jd_chunks():
    return [
        {
            "section": "requirements",
            "chunk_text": "Python and machine learning experience",
        },
        {
            "section": "responsibilities",
            "chunk_text": "Build NLP applications",
        },
    ]


def _retrieved_chunks():
    return [
        {
            "candidate_id": "resume_001",
            "section": "skills",
            "score": 0.91,
            "jd_section": "requirements",
            "jd_chunk_text": "Python and machine learning experience",
            "chunk_text": "Experienced in Python and PyTorch.",
        },
        {
            "candidate_id": "resume_001",
            "section": "projects",
            "score": 0.84,
            "jd_section": "responsibilities",
            "jd_chunk_text": "Build NLP applications",
            "chunk_text": "Built transformer-based text classifier.",
        },
    ]


def test_build_evidence_context_is_stable_and_structured():
    first_context = build_evidence_context(
        jd_chunks=_jd_chunks(),
        retrieved_chunks=_retrieved_chunks(),
    )
    second_context = build_evidence_context(
        jd_chunks=_jd_chunks(),
        retrieved_chunks=_retrieved_chunks(),
    )

    assert first_context == second_context
    assert "[JOB DESCRIPTION]" in first_context
    assert "[RETRIEVED CANDIDATE EVIDENCE]" in first_context
    assert "Similarity Score: 0.91" in first_context
    assert "Section: Skills" in first_context
    assert "Matched JD Section: Requirements" in first_context


def test_build_evidence_context_uses_candidate_result_matches():
    candidate_result = {
        "candidate_id": "resume_001",
        "aggregate_score": 0.88,
        "jd_match_coverage": 1.0,
        "match_count": 2,
        "matched_sections": ["skills", "projects"],
        "matches": _retrieved_chunks(),
    }

    context = build_evidence_context(
        jd_chunks=_jd_chunks(),
        candidate_result=candidate_result,
    )

    assert "[CANDIDATE RETRIEVAL SUMMARY]" in context
    assert "Candidate ID: resume_001" in context
    assert "Aggregate Score: 0.88" in context
    assert "JD Match Coverage: 1.00" in context
    assert "Matched Sections: Skills, Projects" in context


def test_build_evidence_context_suppresses_duplicate_evidence():
    duplicate_chunks = _retrieved_chunks() + [
        {
            **_retrieved_chunks()[0],
            "score": 0.70,
        }
    ]

    context = build_evidence_context(
        jd_chunks=_jd_chunks(),
        retrieved_chunks=duplicate_chunks,
    )

    assert context.count("Experienced in Python and PyTorch.") == 1


def test_build_evidence_context_limits_long_chunks():
    long_chunk = {
        "candidate_id": "resume_001",
        "section": "experience",
        "score": 0.77,
        "jd_section": "requirements",
        "jd_chunk_text": "Python",
        "chunk_text": "Python " * 100,
    }

    context = build_evidence_context(
        jd_chunks=_jd_chunks(),
        retrieved_chunks=[long_chunk],
        max_characters_per_chunk=40,
    )

    assert "..." in context
    assert "Similarity Score: 0.77" in context
    assert "Section: Experience" in context
