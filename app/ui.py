import streamlit as st


def render_ui():
    st.set_page_config(
        page_title="AI Resume Intelligence Agent",
        layout="wide"
    )

    st.title("AI Resume Intelligence Agent")

    st.markdown("### Upload Candidate Resumes")

    uploaded_resumes = st.file_uploader(
        label="Upload PDF Resumes",
        type=["pdf"],
        accept_multiple_files=True
    )

    st.markdown("### Paste Job Description")

    job_description = st.text_area(
        label="Enter Job Description",
        height=250,
        placeholder="Paste the complete job description here..."
    )

    analyze_button = st.button("Analyze Resumes")

    return uploaded_resumes, job_description, analyze_button


def display_resume_data(resumes_data):
    """
    Display preprocessing and chunk validation data
    """

    st.markdown("---")
    st.header("Resume Processing Debug View")

    for resume in resumes_data:

        st.subheader(f"Candidate: {resume['candidate_name']}")

        # =========================================
        # Structured Candidate Metadata
        # =========================================

        st.write("## Candidate Metadata")

        st.json(resume.get("metadata", {}))

        st.markdown("---")

        # =========================================
        # Hybrid NLP Validation Diagnostics
        # =========================================

        st.write("## NLP Section Validation")

        st.json(resume.get("nlp_validation", {}))

        st.markdown("---")

        # =========================================
        # Cleaned Resume Preview
        # =========================================

        st.write("## Cleaned Resume Preview")

        st.write(resume["resume_text"][:1500])

        st.markdown("---")

        # =========================================
        # Global Chunk Information
        # =========================================

        st.write("## Global Chunk Information")

        st.write(f"Total Global Chunks: {len(resume['chunks'])}")

        for i, chunk in enumerate(resume["chunks"]):

            st.write(f"### Global Chunk {i + 1}")

            st.write(f"Chunk Length: {len(chunk)}")

            st.write(chunk[:500])

            st.markdown("---")

        # =========================================
        # Extracted Resume Sections
        # =========================================

        st.write("## Extracted Resume Sections")

        for section_name, content in resume["sections"].items():

            st.write(f"### {section_name.upper()}")

            st.write(content[:1000])

            st.write(f"Content Length: {len(content)}")

            st.markdown("---")

        # =========================================
        # Section-wise Chunk Validation
        # =========================================

        st.write("## Section-wise Chunks")

        for section_name, chunks in resume["section_chunks"].items():

            st.write(f"### {section_name.upper()} Chunks")

            st.write(f"Total Chunks: {len(chunks)}")

            for i, chunk in enumerate(chunks):

                st.write(f"Chunk {i + 1}")

                st.write(f"Chunk Length: {len(chunk)}")

                st.write(chunk[:500])

                st.markdown("---")

        st.markdown("====================================")
