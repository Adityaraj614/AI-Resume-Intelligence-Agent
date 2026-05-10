import streamlit as st

from app.ui import render_ui
from core.parser import build_resume_data


def main():

    uploaded_resumes, job_description, analyze_button = render_ui()

    if analyze_button:

        # -----------------------------
        # Validation Checks
        # -----------------------------

        if not uploaded_resumes:
            st.warning("Please upload at least one resume.")
            return

        if not job_description.strip():
            st.warning("Please enter a job description.")
            return

        # -----------------------------
        # Display Job Description
        # -----------------------------

        st.subheader("Job Description")

        st.text_area(
            label="Entered JD",
            value=job_description,
            height=250
        )

        # -----------------------------
        # Resume Summary
        # -----------------------------

        st.subheader("Uploaded Resume Summary")

        st.write(f"Total Resumes Uploaded: {len(uploaded_resumes)}")

        for file in uploaded_resumes:
            st.write(f"- {file.name}")

        # -----------------------------
        # Structured Resume Data
        # -----------------------------

        st.subheader("Structured Resume Data")

        all_resumes_data = []

        for uploaded_file in uploaded_resumes:

            resume_data = build_resume_data(uploaded_file)

            all_resumes_data.append(resume_data)

            with st.expander(f"{resume_data['candidate_name']}"):

                st.json({
                    "candidate_name": resume_data["candidate_name"],
                    "file_name": resume_data["file_name"]
                })

                st.text_area(
                    label=f"Resume Text - {resume_data['candidate_name']}",
                    value=resume_data["resume_text"],
                    height=300
                )


if __name__ == "__main__":
    main()