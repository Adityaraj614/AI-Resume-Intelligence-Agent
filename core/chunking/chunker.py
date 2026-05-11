import re

from core.parsing.parser_utils import (
    append_section_line,
    finalize_resume_sections,
    initialize_resume_sections,
)
from core.parsing.section_aliases import (
    is_known_section_heading,
    is_noisy_extraction_artifact,
    is_potential_section_heading,
    normalize_section_name,
)
from core.chunking.semantic_boundary import (
    NARRATIVE_SECTIONS,
    merge_tiny_low_signal_sections,
    resolve_content_section,
)


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text for better processing.
    """

    # Normalize line breaks
    text = text.replace("\r", "\n")

    # Remove excessive empty lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove excessive spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove leading/trailing spaces
    text = text.strip()

    return text


def chunk_text(text: str,
               chunk_size: int = 500,
               chunk_overlap: int = 50):
    """
    Split text into overlapping chunks.
    """

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


def extract_resume_sections(text: str):
    """
    Extract semantic resume sections from resume text.

    Architecture:
    - Section aliases live in ``core.parsing.section_aliases`` so resume vocabulary can
      grow without making this parser harder to read.
    - This function only performs line scanning and state management.
    - Every detected heading is converted to a canonical section name before it
      reaches downstream chunking, embeddings, FAISS, or scoring logic.
    - Unknown heading-like blocks are routed to "other" so noisy or new resume
      formats do not contaminate the last known section.
    - Semantic boundary repair lives in ``core.chunking.semantic_boundary`` so future
      NLP fallback classification can evolve independently from chunking.
    """

    lines = text.split("\n")

    sections = initialize_resume_sections()
    current_section = "contact_info"
    previous_content_section = "contact_info"

    for line in lines:

        clean_line = line.strip()

        # Empty lines, page markers, and decorative separators are layout
        # artifacts. They should not become embedding input or section content.
        if is_noisy_extraction_artifact(clean_line):
            continue

        # Only short, known heading lines are treated as section boundaries.
        # This avoids brittle substring matching where a sentence like
        # "Built projects using Python" could accidentally start a new section.
        if is_known_section_heading(clean_line):

            new_section = normalize_section_name(clean_line)

            if (
                current_section != new_section
                and current_section in NARRATIVE_SECTIONS
            ):
                previous_content_section = current_section

            current_section = new_section

            # Duplicate headings are safe: we keep the same list buffer and
            # append later content instead of resetting previously parsed data.
            continue

        # If a line strongly looks like a section heading but is unknown to the
        # alias dictionary, quarantine that block under "other". This protects
        # known sections from malformed headings and gives future NLP fallback
        # classifiers useful text to inspect.
        if is_potential_section_heading(clean_line):
            if current_section in NARRATIVE_SECTIONS:
                previous_content_section = current_section
            current_section = "other"
            append_section_line(sections, current_section, clean_line)
            continue

        target_section = resolve_content_section(
            current_section=current_section,
            previous_content_section=previous_content_section,
            line=clean_line
        )

        append_section_line(sections, target_section, clean_line)

        if target_section in NARRATIVE_SECTIONS:
            previous_content_section = target_section

    sections = merge_tiny_low_signal_sections(sections)

    return finalize_resume_sections(sections)


def chunk_resume_sections(sections: dict,
                          chunk_size: int = 500,
                          chunk_overlap: int = 50):
    """
    Chunk each resume section separately.
    """

    section_chunks = {}

    for section_name, content in sections.items():

        if not content:
            continue

        chunks = chunk_text(
            text=content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        section_chunks[section_name] = chunks

    return section_chunks
