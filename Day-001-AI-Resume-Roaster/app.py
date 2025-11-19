import streamlit as st
from resume_parser import ResumeParser
from ai_analyzer import AIResumeAnalyzer
from scoring import ATSScorer
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Resume Roaster",
    page_icon="🔥",
    layout="centered"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #ff4444;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .score-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2em;
        font-weight: bold;
        margin: 20px 0;
    }
    .score-excellent { background-color: #4CAF50; color: white; }
    .score-good { background-color: #8BC34A; color: white; }
    .score-average { background-color: #FFC107; color: white; }
    .score-poor { background-color: #FF9800; color: white; }
    .score-fail { background-color: #F44336; color: white; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">AI Resume Roaster</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Get honest feedback on your resume</p>', unsafe_allow_html=True)

# Get API key from environment
api_key = os.getenv("GEMINI_API_KEY", "")
model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

if not api_key:
    st.error("API Key not found. Please add GEMINI_API_KEY to your .env file")
    st.stop()

# Main content
st.header("Upload Your Resume")
uploaded_file = st.file_uploader(
    "Choose a PDF or DOCX file",
    type=['pdf', 'docx', 'doc']
)

if uploaded_file:
    st.success(f"Uploaded: {uploaded_file.name}")

# Roast level selector
roast_level = st.select_slider(
    "Roast Level",
    options=["mild", "medium", "savage"],
    value="medium"
)

st.markdown("---")

# Analyze button
analyze_button = st.button("Analyze Resume", type="primary", use_container_width=True)

# Analysis section
if uploaded_file and analyze_button:
    with st.spinner("Analyzing your resume..."):
        try:
            # Parse resume
            resume_text = ResumeParser.parse_resume(uploaded_file)
            
            if len(resume_text) < 50:
                st.error("Resume text too short. Make sure the file is readable.")
            else:
                # Calculate ATS score
                st.markdown("---")
                st.header("ATS Score")
                
                ats_result = ATSScorer.calculate_score(resume_text)
                
                # Display score with color coding
                score = ats_result['score']
                if score >= 80:
                    score_class = "score-excellent"
                elif score >= 70:
                    score_class = "score-good"
                elif score >= 60:
                    score_class = "score-average"
                elif score >= 50:
                    score_class = "score-poor"
                else:
                    score_class = "score-fail"
                
                st.markdown(f'<div class="score-box {score_class}">{score}/100 - {ats_result["grade"]}</div>', 
                          unsafe_allow_html=True)
                
                # Show feedback
                if ats_result['feedback']:
                    st.markdown("**Issues Found:**")
                    for item in ats_result['feedback']:
                        st.markdown(f"- {item}")
                
                # AI Analysis
                st.markdown("---")
                st.header("AI Analysis")
                
                analyzer = AIResumeAnalyzer(api_key, model_name)
                result = analyzer.analyze_resume(resume_text, roast_level)
                
                if result['success']:
                    st.markdown(result['analysis'])
                    
                    # Download button
                    st.download_button(
                        label="Download Analysis",
                        data=result['analysis'],
                        file_name="resume_analysis.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(f"Error: {result['error']}")
                    st.info("Check your API key or try again later.")
        
        except Exception as e:
            st.error(f"Error processing resume: {str(e)}")
            st.info("Make sure your resume file is valid and readable.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Made by <a href='https://github.com/VipinMI2024'>VipinMI2024</a></p>
</div>
""", unsafe_allow_html=True)