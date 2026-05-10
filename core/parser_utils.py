from core.section_aliases import CANONICAL_SECTIONS


def initialize_resume_sections() -> dict:
    """
    Create stable parser output with every canonical section present.

    This module owns parser-state helpers. Keeping these utilities outside the
    chunker makes the high-level extraction flow easier to read and gives future
    NLP fallback code a single place to reuse defensive section buffers.
    """

    return {
        section_name: []
        for section_name in CANONICAL_SECTIONS
    }


def append_section_line(sections: dict, section_name: str, line: str):
    """
    Append content without allowing malformed state to corrupt the result.

    If parser state ever points to an unexpected key, route content to "other"
    instead of creating a surprise section that retrieval/scoring code may not
    understand.
    """

    safe_section_name = (
        section_name
        if section_name in sections
        else "other"
    )

    sections[safe_section_name].append(line)


def finalize_resume_sections(sections: dict) -> dict:
    """
    Convert parser buffers into clean strings while preserving canonical keys.
    """

    finalized_sections = {}

    for section_name in CANONICAL_SECTIONS:
        finalized_sections[section_name] = "\n".join(
            sections.get(section_name, [])
        ).strip()

    return finalized_sections
