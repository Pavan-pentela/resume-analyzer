import streamlit as st
import pdfplumber
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')
model = genai.GenerativeModel('gemini-3.6-flash')
model = genai.GenerativeModel('gemini-3.5-flash-lite')

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text



def get_ai_analysis(resume_text, job_description):
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and Career Coach. 
    Analyze the following resume against the job description provided.

    Resume Text: {resume_text}
    Job Description: {job_description}

    Return a detailed analysis in strictly valid JSON format with these keys:
    1. "ats_score": A number (0-100).
    2. "matched_skills": List of skills found in both.
    3. "missing_skills": List of important skills from the job description missing in the resume.
    4. "improvement_suggestions": Specific actionable steps.
    5. "overall_feedback": A brief summary.
    6. "keywords_to_add": High-impact keywords to include.
    7. "formatting_tips": Advice for ATS-friendliness.
    """

    # Generate content with JSON constraint
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )

    return json.loads(response.text)


def main():
    st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
    st.title("📄 AI Resume Analyzer (Powered by Gemini)")
    st.markdown("Upload your resume and a job description to get a free ATS analysis.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("Step 1: Upload Resume")
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

        st.header("Step 2: Job Description")
        job_description = st.text_area("Paste the job description here", height=300)

        analyze_button = st.button("Analyze Resume")

    if analyze_button:
        if uploaded_file is not None and job_description:
            with st.spinner("Gemini is analyzing your resume..."):
                try:
                    resume_text = extract_text_from_pdf(uploaded_file)
                    analysis = get_ai_analysis(resume_text, job_description)

                    with col2:
                        st.header("Analysis Results")

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

from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


with st.sidebar:

    st.title("AI Resume Analyzer")

    option = st.radio(
        "Menu",
        ["Home", "Analyze", "History", "About"]
    )
import streamlit as st

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf"]
)

if uploaded_file is not None:
    st.success("Resume uploaded!")
