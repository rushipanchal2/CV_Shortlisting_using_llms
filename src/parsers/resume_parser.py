import PyPDF2
import docx
import re
import json
from typing import Dict, List, Optional
import spacy
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class ResumeParser:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Please install spaCy English model: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
        return text
    
    def extract_text(self, file_path: str) -> str:
        """Extract text based on file extension"""
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            raise ValueError("Unsupported file format")
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using regex"""
        contact_info = {}
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)
        contact_info['email'] = email_match.group() if email_match else ""
        
        # Phone
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        contact_info['phone'] = phone_match.group() if phone_match else ""
        
        # Name (first line typically contains name)
        lines = text.strip().split('\n')
        contact_info['name'] = lines[0].strip() if lines else ""
        
        return contact_info
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills using keyword matching and NLP"""
        # Common skill keywords
        skill_keywords = [
            # Programming languages
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'typescript', 'kotlin', 'swift', 'scala', 'r', 'matlab', 'sql',
            # Frameworks and libraries
            'react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            # Technologies
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'jenkins',
            'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            # Soft skills
            'leadership', 'communication', 'teamwork', 'problem solving',
            'project management', 'agile', 'scrum'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Use spaCy for additional entity extraction if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'PRODUCT']:
                    # Additional skill extraction logic can be added here
                    pass
        
        return list(set(found_skills))  # Remove duplicates
    
    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience information"""
        experience = []
        
        # Look for experience sections
        experience_patterns = [
            r'(experience|work history|employment|professional experience)',
            r'(\d{4}\s*[-–]\s*\d{4}|\d{4}\s*[-–]\s*present)',
        ]
        
        # Simple extraction - can be enhanced with more sophisticated NLP
        lines = text.split('\n')
        in_experience_section = False
        current_job = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if we're entering experience section
            if re.search(experience_patterns[0], line.lower()):
                in_experience_section = True
                continue
            
            if in_experience_section:
                # Look for date patterns
                date_match = re.search(r'(\d{4})\s*[-–]\s*(\d{4}|present)', line.lower())
                if date_match:
                    if current_job:
                        experience.append(current_job)
                    current_job = {
                        'duration': date_match.group(),
                        'description': line
                    }
        
        if current_job:
            experience.append(current_job)
        
        return experience
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information"""
        education = []
        
        # Education keywords and degree patterns
        education_keywords = ['education', 'academic', 'qualification', 'degree']
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|associate|diploma|certificate)',
            r'(b\.s\.|m\.s\.|ph\.d\.|b\.a\.|m\.a\.|mba)',
            r'(\d{4})\s*[-–]\s*(\d{4})'
        ]
        
        lines = text.split('\n')
        in_education_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if we're entering education section
            if any(keyword in line.lower() for keyword in education_keywords):
                in_education_section = True
                continue
            
            if in_education_section:
                # Look for degree patterns
                for pattern in degree_patterns:
                    if re.search(pattern, line.lower()):
                        education.append({
                            'degree': line,
                            'details': line
                        })
                        break
        
        return education
    
    def parse_resume(self, file_path: str) -> Dict:
        """Main method to parse resume and extract structured data"""
        try:
            text = self.extract_text(file_path)
            
            parsed_data = {
                'raw_text': text,
                'contact_info': self.extract_contact_info(text),
                'skills': self.extract_skills(text),
                'experience': self.extract_experience(text),
                'education': self.extract_education(text),
                'file_path': file_path
            }
            
            return parsed_data
            
        except Exception as e:
            print(f"Error parsing resume {file_path}: {e}")
            return {}