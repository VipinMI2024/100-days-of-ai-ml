import google.generativeai as genai
import os
from typing import Dict

class AIResumeAnalyzer:
    """Analyze resume using Google Gemini AI with roasting capability"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
    
    def analyze_resume(self, resume_text: str, roast_level: str = "medium") -> Dict:
        """
        Analyze resume and provide feedback
        
        roast_level: 'mild', 'medium', 'savage'
        """
        
        roast_instructions = {
            "mild": "Be constructive but slightly sarcastic. Point out issues humorously.",
            "medium": "Be brutally honest. Roast weak points while being helpful. Use humor.",
            "savage": "Go full Gordon Ramsay mode. Absolutely savage but still provide actionable advice."
        }
        
        prompt = f"""You are an expert resume reviewer with a brutally honest personality. Analyze this resume and provide feedback.

ROAST LEVEL: {roast_level.upper()}
{roast_instructions[roast_level]}

Resume:
{resume_text}

Provide your analysis in the following format:

## 🔥 THE ROAST
[Give your brutally honest first impression. What made you cringe? Be funny but harsh.]

## 📊 ATS SCORE
[Rate 0-100 and explain why]

## 💀 DEADLY SINS (What's killing this resume)
[List 3-5 major problems]

## 💎 HIDDEN GEMS (What's actually good)
[List 2-3 things they did right]

## 🎯 ACTION ITEMS (How to fix this disaster)
[5-7 specific, actionable improvements]

## 🚀 REWRITE EXAMPLE
[Take their worst bullet point and show how to rewrite it]

Be specific, reference actual content from the resume, and make it entertaining while being genuinely helpful."""

        try:
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "analysis": response.text,
                "model_used": "Gemini"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_ats_keywords(self, resume_text: str, job_description: str = "") -> Dict:
        """Optional: Compare resume against job description for ATS optimization"""
        
        if not job_description:
            return {"success": False, "error": "No job description provided"}
        
        prompt = f"""Compare this resume against the job description and identify:
1. Missing keywords that should be added
2. Keywords present in resume
3. ATS compatibility score

Resume:
{resume_text}

Job Description:
{job_description}

Provide structured analysis with specific recommendations."""

        try:
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "analysis": response.text
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }