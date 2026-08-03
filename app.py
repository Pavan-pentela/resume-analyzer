import streamlit as st
import pdfplumber
import json
import os
import base64
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ---------------------------------------------------
# BACKGROUND IMAGE
# ---------------------------------------------------




st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

h1, h2, h3, h4, h5, h6, p, label {
    color: white !important;
}

.stTextArea textarea {
    background-color: rgba(255,255,255,0.08) !important;
    color: white !important;
    border-radius: 12px;
}

.stButton>button {
    background: linear-gradient(135deg,#2563EB,#1D4ED8);
    color: white;
    border-radius: 12px;
    font-weight: bold;
    height: 50px;
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------

st.title("📄 AI Resume Analyzer")
st.write("Upload your resume and get an AI-powered ATS analysis.")

# ---------------------------------------------------
# GEMINI
# ---------------------------------------------------

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("GOOGLE_API_KEY not found in .env file")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-3.6-flash")
def extract_text_from_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text.strip()
def get_ai_analysis(resume_text, job_description):

    prompt = f"""
You are an ATS Resume Analyzer.

Compare the resume with the job description.

Resume:
{resume_text}

Job Description:
{job_description}

Return ONLY valid JSON in this format:

{{
    "ats_score": 0,
    "matched_skills": [],
    "missing_skills": [],
    "improvement_suggestions": [],
    "overall_feedback": "",
    "keywords_to_add": [],
    "formatting_tips": ""
}}
"""

    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type":"application/json"
        }
    )

    return json.loads(response.text)

def main():

    st.subheader("📤 Step 1: Upload Resume")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    st.subheader("📝 Step 2: Job Description")
    job_description = st.text_area("Paste the job description here", height=180)
    analyze_button = st.button(
        "🚀 Analyze Resume",
        use_container_width=True
    )

    if analyze_button:
        if uploaded_file is not None and job_description:
            with st.spinner("Gemini is analyzing your resume..."):
                try:
                    resume_text = extract_text_from_pdf(uploaded_file)
                    analysis = get_ai_analysis(resume_text, job_description)

                    # Score
                    score = analysis.get("ats_score", 0)
                    st.metric("ATS Score", f"{score}/100")
                    st.progress(score / 100)

                    st.subheader("Overall Feedback")
                    st.write(analysis.get("overall_feedback"))

                    st.subheader("Matched Skills")
                    st.info(", ".join(analysis.get("matched_skills", [])))

                    st.subheader("Missing Skills")
                    st.warning(", ".join(analysis.get("missing_skills", [])))

                    st.subheader("Improvement Suggestions")
                    for s in analysis.get("improvement_suggestions", []):
                        st.write(f"✅ {s}")

                    st.subheader("Keywords to Add")
                    st.write(", ".join(analysis.get("keywords_to_add", [])))

                    st.subheader("Formatting Tips")
                    st.write(analysis.get("formatting_tips"))

                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.warning("Please upload a resume and provide a job description.")




if __name__ == "__main__":
    main()