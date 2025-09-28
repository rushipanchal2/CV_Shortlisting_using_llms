import json
from typing import Dict, List, Tuple
from src.llm_client.client import FreeLLMClient

class LLMResumeJobMatcher:
    def __init__(self):
        self.llm_client = FreeLLMClient()
    
    def calculate_match_score(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Calculate comprehensive match score between resume and job"""
        
        prompt = f"""
        You are an expert HR recruiter. Please analyze the match between this candidate's resume and the job requirements.
        
        CANDIDATE RESUME:
        Name: {resume_data.get('contact_info', {}).get('name', 'Not provided')}
        Skills: {', '.join(resume_data.get('skills', []))}
        Experience: {json.dumps(resume_data.get('experience', []), indent=2)}
        Education: {json.dumps(resume_data.get('education', []), indent=2)}
        
        JOB REQUIREMENTS:
        Title: {job_data.get('job_title', 'Not specified')}
        Required Skills: {', '.join(job_data.get('required_skills', []))}
        Preferred Skills: {', '.join(job_data.get('preferred_skills', []))}
        Experience Required: {job_data.get('experience_required', 'Not specified')}
        Education Required: {job_data.get('education_required', 'Not specified')}
        Key Requirements: {', '.join(job_data.get('key_requirements', []))}
        
        Please provide a detailed analysis in the following JSON format:
        {{
            "overall_score": <score from 0-100>,
            "skills_match": {{
                "score": <score from 0-100>,
                "matched_skills": ["list of matched skills"],
                "missing_skills": ["list of missing important skills"],
                "explanation": "detailed explanation of skills alignment"
            }},
            "experience_match": {{
                "score": <score from 0-100>,
                "relevant_experience": "summary of relevant experience",
                "experience_gap": "any gaps in experience",
                "explanation": "detailed explanation"
            }},
            "education_match": {{
                "score": <score from 0-100>,
                "meets_requirements": true/false,
                "explanation": "explanation of education fit"
            }},
            "overall_fit": {{
                "score": <score from 0-100>,
                "strengths": ["candidate's key strengths for this role"],
                "concerns": ["potential concerns or gaps"],
                "recommendation": "STRONG_FIT/GOOD_FIT/MODERATE_FIT/POOR_FIT",
                "explanation": "comprehensive explanation of overall fit"
            }}
        }}
        
        Be objective and thorough in your analysis. Consider both technical and soft skills alignment.
        Return only valid JSON without any additional text.
        """
        
        try:
            response = self.llm_client.generate_response(prompt)
            
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                match_result = json.loads(json_str)
                
                # Add metadata
                match_result['candidate_name'] = resume_data.get('contact_info', {}).get('name', 'Unknown')
                match_result['job_title'] = job_data.get('job_title', 'Unknown Position')
                
                return match_result
            else:
                return self._fallback_scoring(resume_data, job_data)
                
        except Exception as e:
            print(f"LLM matching failed: {e}")
            return self._fallback_scoring(resume_data, job_data)
    
    def _fallback_scoring(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Fallback scoring mechanism if LLM fails"""
        
        candidate_skills = set([skill.lower() for skill in resume_data.get('skills', [])])
        required_skills = set([skill.lower() for skill in job_data.get('required_skills', [])])
        
        # Simple skill matching
        matched_skills = candidate_skills.intersection(required_skills)
        missing_skills = required_skills - candidate_skills
        
        skills_score = (len(matched_skills) / max(len(required_skills), 1)) * 100
        
        return {
            "overall_score": min(skills_score + 10, 85),  # Conservative scoring
            "skills_match": {
                "score": skills_score,
                "matched_skills": list(matched_skills),
                "missing_skills": list(missing_skills),
                "explanation": f"Basic skill matching: {len(matched_skills)}/{len(required_skills)} skills matched"
            },
            "experience_match": {
                "score": 60,  # Default moderate score
                "relevant_experience": "Unable to analyze with fallback method",
                "experience_gap": "Analysis not available",
                "explanation": "Fallback scoring - detailed analysis not available"
            },
            "education_match": {
                "score": 70,  # Default moderate score
                "meets_requirements": True,
                "explanation": "Basic evaluation only"
            },
            "overall_fit": {
                "score": min(skills_score + 5, 75),
                "strengths": list(matched_skills),
                "concerns": list(missing_skills),
                "recommendation": "MODERATE_FIT" if skills_score > 50 else "POOR_FIT",
                "explanation": "Fallback analysis based on skill matching only"
            },
            'candidate_name': resume_data.get('contact_info', {}).get('name', 'Unknown'),
            'job_title': job_data.get('job_title', 'Unknown Position')
        }
    
    def batch_match_candidates(self, resume_list: List[Dict], job_data: Dict) -> List[Dict]:
        """Process multiple resumes against a job description"""
        results = []
        
        for resume in resume_list:
            try:
                match_result = self.calculate_match_score(resume, job_data)
                results.append(match_result)
            except Exception as e:
                print(f"Error matching resume: {e}")
                continue
        
        # Sort by overall score
        results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        return results