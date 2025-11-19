import PyPDF2
import docx
import pdfplumber
from typing import Optional

class ResumeParser:
    """Extract text from PDF and DOCX resume files"""
    
    @staticmethod
    def extract_text_from_pdf(file) -> str:
        """Extract text from PDF using pdfplumber (better for resumes)"""
        try:
            text = ""
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return "\n".join(text)
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    @staticmethod
    def parse_resume(file) -> str:
        """Main function to parse resume based on file type"""
        file_type = file.name.split('.')[-1].lower()
        
        if file_type == 'pdf':
            return ResumeParser.extract_text_from_pdf(file)
        elif file_type in ['docx', 'doc']:
            return ResumeParser.extract_text_from_docx(file)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")