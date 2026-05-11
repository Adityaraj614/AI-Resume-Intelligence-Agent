from typing import Any, Dict, List

import streamlit as st


def render_upload_section() -> Dict[str, Any]:
    left, right = st.columns([1.08, 0.92], gap="large")

    with left:
        job_description = st.text_area(
            "Job Description",
            height=190,
            placeholder="Paste the complete job description here...",
            help="Used by the existing retrieval and ranking workflow.",
        )
        jd_file = st.file_uploader(
            "Optional JD File",
            type=["txt", "md", "pdf"],
            accept_multiple_files=False,
            help="Use this if the JD is available as a file.",
        )

    with right:
        resume_files = st.file_uploader(
            "Resume PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload one or more PDF resumes.",
        )
        linkedin_files = st.file_uploader(
            "LinkedIn JSON Profiles",
            type=["json"],
            accept_multiple_files=True,
            help="Upload structured LinkedIn-style JSON. No scraping is performed.",
        )
        st.markdown(
            """
            <div class="upload-guidance">
                Intake supports resume PDFs and structured LinkedIn JSON. The backend workflow remains retrieval-first and deterministic.
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "job_description": job_description,
        "jd_file": jd_file,
        "resume_files": resume_files or [],
        "linkedin_files": linkedin_files or [],
    }


def validate_dashboard_inputs(inputs: Dict[str, Any]) -> List[str]:
    warnings = []
    job_description = str(inputs.get("job_description", "")).strip()
    jd_file = inputs.get("jd_file")
    resume_files = inputs.get("resume_files", [])
    linkedin_files = inputs.get("linkedin_files", [])

    if not job_description and jd_file is None:
        warnings.append("Add a job description by pasting text or uploading a JD file.")

    if not resume_files and not linkedin_files:
        warnings.append("Upload at least one resume PDF or LinkedIn JSON profile.")

    for file in resume_files:
        if not str(file.name).lower().endswith(".pdf"):
            warnings.append(f"Unsupported resume file type: {file.name}")

    for file in linkedin_files:
        if not str(file.name).lower().endswith(".json"):
            warnings.append(f"Unsupported LinkedIn file type: {file.name}")

    return warnings
