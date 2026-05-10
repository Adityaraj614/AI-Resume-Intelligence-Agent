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
    Build structured resume data
    """

    extracted_text = extract_text_from_pdf(uploaded_file)

    resume_data = {
        "candidate_name": uploaded_file.name.replace(".pdf", ""),
        "file_name": uploaded_file.name,
        "resume_text": extracted_text
    }

    return resume_data