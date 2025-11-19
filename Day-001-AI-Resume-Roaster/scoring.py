import re
from typing import Dict, List

class ATSScorer:
    """Calculate basic ATS score based on common criteria"""
    
    @staticmethod
    def calculate_score(resume_text: str) -> Dict:
        """Calculate ATS compatibility score"""
        
        score = 0
        max_score = 100
        feedback = []
        
        # Check for email (10 points)
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
            score += 10
        else:
            feedback.append("❌ No email found")
        
        # Check for phone number (10 points)
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', resume_text):
            score += 10
        else:
            feedback.append("❌ No phone number found")
        
        # Check for LinkedIn (5 points)
        if 'linkedin' in resume_text.lower():
            score += 5
        else:
            feedback.append("⚠️ No LinkedIn profile")
        
        # Check for action verbs (15 points)
        action_verbs = ['led', 'managed', 'developed', 'created', 'implemented', 
                       'designed', 'built', 'achieved', 'increased', 'improved']
        found_verbs = sum(1 for verb in action_verbs if verb in resume_text.lower())
        verb_score = min(15, found_verbs * 2)
        score += verb_score
        if verb_score < 10:
            feedback.append("⚠️ Weak action verbs - use more powerful words")
        
        # Check for quantifiable achievements (20 points)
        numbers = re.findall(r'\d+%|\$\d+|\d+x|\d+ years?', resume_text)
        if len(numbers) >= 5:
            score += 20
        elif len(numbers) >= 3:
            score += 15
            feedback.append("⚠️ Add more quantifiable achievements")
        else:
            score += 5
            feedback.append("❌ Seriously lacking numbers and metrics")
        
        # Check for skills section (15 points)
        skills_keywords = ['skills', 'technologies', 'tools', 'expertise']
        has_skills = any(keyword in resume_text.lower() for keyword in skills_keywords)
        if has_skills:
            score += 15
        else:
            feedback.append("❌ No clear skills section")
        
        # Check length (10 points) - ideal is 1-2 pages (~500-1500 words)
        word_count = len(resume_text.split())
        if 400 <= word_count <= 1500:
            score += 10
        elif word_count < 400:
            score += 5
            feedback.append("⚠️ Resume too short - add more detail")
        else:
            score += 5
            feedback.append("⚠️ Resume too long - be more concise")
        
        # Check for education section (10 points)
        education_keywords = ['university', 'college', 'degree', 'bachelor', 'master', 'phd']
        has_education = any(keyword in resume_text.lower() for keyword in education_keywords)
        if has_education:
            score += 10
        else:
            feedback.append("❌ No education section found")
        
        # Check for experience/work section (5 points)
        experience_keywords = ['experience', 'employment', 'work history']
        has_experience = any(keyword in resume_text.lower() for keyword in experience_keywords)
        if has_experience:
            score += 5
        else:
            feedback.append("❌ No clear experience section")
        
        # Determine grade
        if score >= 90:
            grade = "A+ (ATS will love this)"
        elif score >= 80:
            grade = "A (Strong candidate)"
        elif score >= 70:
            grade = "B (Good, needs minor tweaks)"
        elif score >= 60:
            grade = "C (Needs improvement)"
        elif score >= 50:
            grade = "D (Barely passing)"
        else:
            grade = "F (This won't make it through ATS)"
        
        return {
            "score": score,
            "grade": grade,
            "feedback": feedback,
            "word_count": word_count
        }