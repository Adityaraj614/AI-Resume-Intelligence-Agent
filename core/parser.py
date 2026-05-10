from core.chunker import (
    clean_text,
    chunk_text,
    extract_resume_sections,
    chunk_resume_sections
)
from core.metadata_extractor import extract_candidate_metadata
from core.nlp_section_classifier import validate_and_repair_sections
import fitz


def extract_text_from_pdf(uploaded_file):
    """
    Extract raw text from PDF
    """

    pdf_text = ""

    pdf_document = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    for page in pdf_document:
        pdf_text += page.get_text()

    pdf_document.close()

    return pdf_text


def build_resume_data(uploaded_file):
    """
    Build structured resume intelligence object
    """

    # Step 1 — Extract raw text
    extracted_text = extract_text_from_pdf(uploaded_file)

    # Step 2 — Clean text
    cleaned_text = clean_text(extracted_text)

    # Step 3 — Global chunking
    global_chunks = chunk_text(cleaned_text)

    # Step 4 — Extract semantic sections
    sections = extract_resume_sections(cleaned_text)

    # Step 5 — Conditional NLP semantic validation
    # Rule-based parsing remains primary. NLP only runs when parsing quality
    # checks detect fallback-heavy or ambiguous section output.
    sections, nlp_validation = validate_and_repair_sections(
        sections=sections,
        raw_text=cleaned_text
    )

    # Step 6 — Section-wise chunking
    section_chunks = chunk_resume_sections(sections)

    # Step 7 — Extract structured candidate metadata
    metadata = extract_candidate_metadata(
        text=cleaned_text,
        fallback_name=uploaded_file.name
    )

    candidate_name = (
        metadata.get("candidate_name")
        or uploaded_file.name.replace(".pdf", "")
    )

    # Step 8 — Build structured resume object
    resume_data = {

        "candidate_name": candidate_name,

        "file_name": uploaded_file.name,

        # Structured candidate intelligence
        "metadata": metadata,

        "resume_text": cleaned_text,

        # Full resume chunks
        "chunks": global_chunks,

        # Semantic sections
        "sections": sections,

        # Conditional hybrid NLP validation diagnostics
        "nlp_validation": nlp_validation,

        # Section-wise semantic chunks
        "section_chunks": section_chunks
    }

    return resume_data
