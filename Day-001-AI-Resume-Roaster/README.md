# Day 001: AI Resume Roaster

Part of [100 Days of AI & ML Challenge](../)

![Demo](demo.png)

## Overview

AI-powered resume analyzer that provides brutally honest feedback, ATS scoring, and actionable improvements.

**Live Demo:** [https://100-days-of-ai-ml-mzdqwkfrz8hdt46svwwhqv.streamlit.app/](link)

## Features

- Upload PDF/DOCX resumes
- ATS compatibility scoring
- AI-powered analysis with multiple roast levels
- Specific improvement suggestions
- Downloadable analysis report

## Tech Stack

- **Frontend:** Streamlit
- **AI:** Google Gemini API
- **Libraries:** PyPDF2, python-docx, pdfplumber
- **Deployment:** Streamlit Cloud

## Installation

```bash
# Clone the repo
git clone https://github.com/VipinMI2024/100-days-of-ai-ml.git
cd 100-days-of-ai-ml/Day-001-AI-Resume-Roaster

# Install dependencies
pip install -r requirements.txt

# Add API key to .env
echo "GEMINI_API_KEY=your_key" > .env

# Run
streamlit run app.py
```

## Usage

1. Upload your resume (PDF or DOCX)
2. Select roast level (mild/medium/savage)
3. Click "Analyze Resume"
4. Review feedback and download analysis

## Code Structure

```
Day-001-AI-Resume-Roaster/
├── app.py              # Main Streamlit app
├── resume_parser.py    # PDF/DOCX parser
├── ai_analyzer.py      # Gemini AI integration
├── scoring.py          # ATS scoring logic
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## Key Learnings

- Working with Google Gemini API
- Parsing different document formats
- Building interactive Streamlit apps
- Handling rate limits and errors
- Deploying to cloud platforms

## Challenges Faced

1. **API Rate Limits:** Had to switch from experimental to stable Gemini model
2. **File Parsing:** Different PDF structures required robust parsing
3. **Error Handling:** Needed comprehensive error handling for user uploads

## Future Improvements

- [ ] Add job description comparison
- [ ] Support more file formats
- [ ] Add resume templates
- [ ] Implement caching for faster results
- [ ] Add analytics dashboard



## Time to Build

**Total Time:** 4 hours
- Planning: 30 min
- Coding: 2.5 hours
- Testing: 30 min
- Documentation: 30 min


## License

MIT

---

**Day:** 001/100  
**Date:** November 19, 2025  
**Status:** ✅ Complete
