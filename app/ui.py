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