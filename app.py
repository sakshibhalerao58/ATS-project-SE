import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found in environment. Please check your .env file.")
    st.stop()

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# PDF Text Extraction
def extract_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

# Gemini Content Generation
def get_gemini_response(prompt):
    model = genai.GenerativeModel("gemini-1.5-pro-001")  # ✅ No "models/" prefix
    response = model.generate_content(prompt)
    return response.text

# Streamlit App UI
st.set_page_config(page_title="Smart ATS")
st.title("📄 Smart ATS Resume Checker")
st.markdown("Upload your resume and paste a job description to analyze ATS match.")

job_description = st.text_area("💼 Job Description", height=200)
uploaded_resume = st.file_uploader("📎 Upload Resume (PDF)", type="pdf")

if st.button("🚀 Analyze"):
    if not uploaded_resume or not job_description.strip():
        st.warning("Please upload a PDF and fill the job description.")
        st.stop()

    with st.spinner("Analyzing..."):
        resume_text = extract_pdf_text(uploaded_resume)

        prompt = f"""
You are an advanced ATS system with deep domain knowledge in tech hiring.

Evaluate this candidate resume against the job description.

Resume:
\"\"\"
{resume_text}
\"\"\"

Job Description:
\"\"\"
{job_description}
\"\"\"

Respond strictly in the following JSON format:
{{
  "JD Match": "XX%",
  "MissingKeywords": ["keyword1", "keyword2", ...],
  "Profile Summary": "A 3-4 sentence summary of the candidate"
}}
"""
        try:
            raw_response = get_gemini_response(prompt)
            parsed = json.loads(raw_response.strip())
            st.success("✅ Resume evaluated successfully.")
            st.json(parsed)
        except Exception as e:
            st.error(f"❌ Error: {e}")
