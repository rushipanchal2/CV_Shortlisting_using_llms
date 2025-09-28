import pandas as pd
from typing import Dict, List
import yaml

class CandidateRanker:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        self.weights = self.config['scoring']['weights']
    
    def calculate_weighted_score(self, match_result: Dict) -> float:
        """Calculate weighted score based on configuration"""
        
        weighted_score = (
            match_result.get('skills_match', {}).get('score', 0) * self.weights['skills_match'] +
            match_result.get('experience_match', {}).get('score', 0) * self.weights['experience_match'] +
            match_result.get('education_match', {}).get('score', 0) * self.weights['education_match'] +
            match_result.get('overall_score', 0) * self.weights['overall_fit']
        )
        
        return round(weighted_score, 2)
    
    def rank_candidates(self, match_results: List[Dict]) -> List[Dict]:
        """Rank candidates and add additional metadata"""
        
        # Calculate weighted scores
        for result in match_results:
            result['weighted_score'] = self.calculate_weighted_score(result)
            result['rank'] = 0  # Will be set after sorting
        
        # Sort by weighted score
        ranked_results = sorted(match_results, key=lambda x: x['weighted_score'], reverse=True)
        
        # Add rank numbers
        for i, result in enumerate(ranked_results):
            result['rank'] = i + 1
            result['percentile'] = round((1 - i / len(ranked_results)) * 100, 1)
        
        return ranked_results
    
    def generate_summary_report(self, ranked_results: List[Dict], job_data: Dict) -> Dict:
        """Generate summary analytics for the ranking"""
        
        if not ranked_results:
            return {"error": "No candidates to analyze"}
        
        scores = [r['weighted_score'] for r in ranked_results]
        
        summary = {
            "job_info": {
                "title": job_data.get('job_title', 'Unknown'),
                "total_candidates": len(ranked_results)
            },
            "score_statistics": {
                "highest_score": max(scores),
                "lowest_score": min(scores),
                "average_score": round(sum(scores) / len(scores), 2),
                "median_score": round(sorted(scores)[len(scores)//2], 2)
            },
            "top_candidates": ranked_results[:3],
            "skill_analysis": self._analyze_skill_gaps(ranked_results),
            "recommendations": self._generate_recommendations(ranked_results)
        }
        
        return summary
    
    def _analyze_skill_gaps(self, results: List[Dict]) -> Dict:
        """Analyze common skill gaps across candidates"""
        
        all_missing_skills = []
        all_matched_skills = []
        
        for result in results:
            skills_match = result.get('skills_match', {})
            all_missing_skills.extend(skills_match.get('missing_skills', []))
            all_matched_skills.extend(skills_match.get('matched_skills', []))
        
        # Count frequency
        missing_skill_counts = {}
        matched_skill_counts = {}
        
        for skill in all_missing_skills:
            missing_skill_counts[skill] = missing_skill_counts.get(skill, 0) + 1
        
        for skill in all_matched_skills:
            matched_skill_counts[skill] = matched_skill_counts.get(skill, 0) + 1
        
        return {
            "most_common_gaps": sorted(missing_skill_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "most_common_matches": sorted(matched_skill_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "total_unique_gaps": len(missing_skill_counts),
            "total_unique_matches": len(matched_skill_counts)
        }
    
    def _generate_recommendations(self, results: List[Dict]) -> List[str]:
        """Generate hiring recommendations based on analysis"""
        
        recommendations = []
        
        if not results:
            return ["No candidates to evaluate"]
        
        top_score = results[0]['weighted_score']
        
        if top_score >= 80:
            recommendations.append("Strong candidate pool - recommend interviewing top 3 candidates")
        elif top_score >= 60:
            recommendations.append("Moderate candidate pool - consider expanding search or reviewing requirements")
        else:
            recommendations.append("Weak candidate pool - recommend revising job requirements or expanding search")
        
        # Check for skill gaps
        skill_analysis = self._analyze_skill_gaps(results)
        if skill_analysis['total_unique_gaps'] > 5:
            recommendations.append("Consider offering training for common skill gaps")
        
        # Check score distribution
        scores = [r['weighted_score'] for r in results]
        score_range = max(scores) - min(scores)
        
        if score_range > 40:
            recommendations.append("Wide variation in candidate quality - focus on top performers")
        else:
            recommendations.append("Similar candidate quality - consider additional evaluation criteria")
        
        return recommendations
    
    def export_results_to_csv(self, ranked_results: List[Dict], filename: str = "candidate_ranking.csv"):
        """Export results to CSV for further analysis"""
        
        # Flatten the nested structure for CSV export
        flattened_data = []
        
        for result in ranked_results:
            flat_record = {
                'rank': result.get('rank', 0),
                'candidate_name': result.get('candidate_name', 'Unknown'),
                'overall_score': result.get('overall_score', 0),
                'weighted_score': result.get('weighted_score', 0),
                'percentile': result.get('percentile', 0),
                'skills_score': result.get('skills_match', {}).get('score', 0),
                'experience_score': result.get('experience_match', {}).get('score', 0),
                'education_score': result.get('education_match', {}).get('score', 0),
                'recommendation': result.get('overall_fit', {}).get('recommendation', 'UNKNOWN'),
                'matched_skills': ', '.join(result.get('skills_match', {}).get('matched_skills', [])),
                'missing_skills': ', '.join(result.get('skills_match', {}).get('missing_skills', [])),
                'key_strengths': ', '.join(result.get('overall_fit', {}).get('strengths', [])),
                'concerns': ', '.join(result.get('overall_fit', {}).get('concerns', []))
            }
            flattened_data.append(flat_record)
        
        df = pd.DataFrame(flattened_data)
        df.to_csv(filename, index=False)
        print(f"Results exported to {filename}")
        
        return df