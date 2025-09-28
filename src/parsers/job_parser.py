import re
import json
from typing import Dict, List
from src.llm_client.client import FreeLLMClient

class JobDescriptionParser:
    def __init__(self):
        self.llm_client = FreeLLMClient()
    
    def parse_job_description(self, job_text: str) -> Dict:
        """Parse job description using LLM to extract structured information"""
        
        prompt = f"""
        Please analyze the following job description and extract structured information in JSON format:
        
        Job Description:
        {job_text}
        
        Please extract:
        1. job_title: The job title
        2. required_skills: List of technical and soft skills required
        3. preferred_skills: List of preferred/nice-to-have skills
        4. experience_required: Years of experience required
        5. education_required: Education requirements
        6. responsibilities: List of key responsibilities
        7. company_info: Company name and basic info if mentioned
        8. location: Job location
        9. key_requirements: Most important requirements for this role
        
        Return only valid JSON format without any additional text or explanation.
        """
        
        try:
            response = self.llm_client.generate_response(prompt)
            
            # Clean response to extract JSON
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                parsed_job = json.loads(json_str)
                parsed_job['raw_text'] = job_text
                return parsed_job
            else:
                # Fallback to basic parsing if LLM fails
                return self._basic_job_parsing(job_text)
                
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return self._basic_job_parsing(job_text)
    
    def _basic_job_parsing(self, job_text: str) -> Dict:
        """Fallback basic parsing using regex patterns"""
        
        # Extract skills using common patterns
        skills_pattern = r'(?:skills?|technologies?|requirements?)[:\s]*([^.]*(?:python|java|javascript|react|sql|aws|docker|kubernetes|git|agile|scrum|machine learning|data science|html|css|node|angular|vue|spring|django|flask|tensorflow|pytorch)[^.]*)'
        skills_matches = re.findall(skills_pattern, job_text.lower())
        
        skills = []
        for match in skills_matches:
            # Extract individual skills from the match
            skill_words = re.findall(r'\b(?:python|java|javascript|react|sql|aws|docker|kubernetes|git|agile|scrum|html|css|node|angular|vue|spring|django|flask|tensorflow|pytorch)\b', match.lower())
            skills.extend(skill_words)
        
        # Extract experience requirements
        experience_pattern = r'(\d+)(?:\+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
        experience_match = re.search(experience_pattern, job_text.lower())
        experience_required = experience_match.group(1) if experience_match else "Not specified"
        
        # Extract education requirements
        education_pattern = r'(bachelor|master|phd|degree|diploma|certificate)'
        education_match = re.search(education_pattern, job_text.lower())
        education_required = education_match.group() if education_match else "Not specified"
        
        return {
            'job_title': 'Not extracted',
            'required_skills': list(set(skills)),
            'preferred_skills': [],
            'experience_required': experience_required,
            'education_required': education_required,
            'responsibilities': [],
            'company_info': 'Not specified',
            'location': 'Not specified',
            'key_requirements': skills,
            'raw_text': job_text
        }