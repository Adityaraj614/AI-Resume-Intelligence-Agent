from core.llm.context_formatter import (
    format_job_description_context,
    format_retrieved_evidence,
)
from core.llm.retrieval_summarizer import (
    compress_long_chunk,
    deduplicate_chunks,
    summarize_retrieval_context,
)


def _retrieved_chunks():
    return [
        {
            "candidate_id": "resume_001",
            "section": "skills",
            "score": 0.87321,
            "jd_section": "requirements",
            "jd_chunk_text": "Experience with Python and PyTorch.",
            "chunk_text": "Experienced in Python, PyTorch, and Transformers.",
        },
        {
            "candidate_id": "resume_001",
            "section": "projects",
            "score": 0.82111,
            "jd_section": "responsibilities",
            "jd_chunk_text": "Build NLP systems.",
            "chunk_text": "Built NLP-based recommendation system.",
        },
    ]


def test_retrieved_evidence_formatting_is_deterministic():
    chunks = _retrieved_chunks()

    first_context = format_retrieved_evidence(chunks)
    second_context = format_retrieved_evidence(chunks)

    assert first_context == second_context
    assert "[RETRIEVED CANDIDATE EVIDENCE]" in first_context
    assert "Section: Skills" in first_context
    assert "Similarity Score: 0.87" in first_context
    assert "\"Experienced in Python, PyTorch, and Transformers.\"" in first_context


def test_job_description_formatting_preserves_sections():
    jd_chunks = [
        {
            "section": "required_skills",
            "chunk_text": "Python",
        },
        {
            "section": "responsibilities",
            "chunk_text": "Build machine learning services",
        },
    ]

    context = format_job_description_context(jd_chunks)

    assert "[JOB DESCRIPTION]" in context
    assert "Section: Required Skills" in context
    assert "Section: Responsibilities" in context
    assert "\"Python\"" in context


def test_deduplicate_chunks_removes_repeated_chunk_text():
    chunks = _retrieved_chunks() + [
        {
            **_retrieved_chunks()[0],
            "score": 0.75,
        }
    ]

    deduplicated_chunks = deduplicate_chunks(chunks)

    assert len(deduplicated_chunks) == 2
    assert deduplicated_chunks[0]["score"] == 0.87321


def test_compress_long_chunk_truncates_without_inventing_text():
    chunk_text = "Python " * 100

    compressed_text = compress_long_chunk(
        chunk_text=chunk_text,
        max_characters=25,
    )

    assert compressed_text.endswith("...")
    assert len(compressed_text) <= 28
    assert "Python" in compressed_text


def test_summarize_retrieval_context_deduplicates_and_limits_chunks():
    chunks = _retrieved_chunks() + [
        {
            "candidate_id": "resume_002",
            "section": "education",
            "score": 0.50,
            "jd_section": "requirements",
            "jd_chunk_text": "Python",
            "chunk_text": "Coursework in Python.",
        },
        {
            **_retrieved_chunks()[0],
            "score": 0.40,
        },
    ]

    summarized_chunks = summarize_retrieval_context(
        retrieved_chunks=chunks,
        max_chunks=2,
    )

    assert len(summarized_chunks) == 2
    assert summarized_chunks[0]["section"] == "skills"
    assert summarized_chunks[1]["section"] == "projects"
