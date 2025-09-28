import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict

class CompatibleCharts:
    """Charts that work across different plotly versions"""
    
    @staticmethod
    def create_radar_chart_alternative(candidates_data: List[Dict], categories: List[str]) -> go.Figure:
        """Create radar chart using scatter plot for compatibility"""
        
        fig = go.Figure()
        
        # Number of categories
        N = len(categories)
        
        # Calculate angles for each category
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        for candidate in candidates_data:
            # Get scores for each category
            scores = [
                candidate.get('skills_match', {}).get('score', 0),
                candidate.get('experience_match', {}).get('score', 0),
                candidate.get('education_match', {}).get('score', 0),
                candidate.get('overall_score', 0)
            ]
            scores += scores[:1]  # Complete the circle
            
            # Convert to cartesian coordinates
            x = [score * np.cos(angle) for score, angle in zip(scores, angles)]
            y = [score * np.sin(angle) for score, angle in zip(scores, angles)]
            
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                fill='toself',
                name=candidate['candidate_name'][:20],
                mode='lines+markers'
            ))
        
        # Add category labels
        label_x = [110 * np.cos(angle) for angle in angles[:-1]]
        label_y = [110 * np.sin(angle) for angle in angles[:-1]]
        
        fig.add_trace(go.Scatter(
            x=label_x,
            y=label_y,
            mode='text',
            text=categories,
            textposition='middle center',
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add grid circles
        for r in [20, 40, 60, 80, 100]:
            circle_x = [r * np.cos(angle) for angle in angles]
            circle_y = [r * np.sin(angle) for angle in angles]
            
            fig.add_trace(go.Scatter(
                x=circle_x,
                y=circle_y,
                mode='lines',
                line=dict(color='lightgray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add radial lines
        for angle in angles[:-1]:
            fig.add_trace(go.Scatter(
                x=[0, 100 * np.cos(angle)],
                y=[0, 100 * np.sin(angle)],
                mode='lines',
                line=dict(color='lightgray', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        fig.update_layout(
            title="Top 5 Candidates - Skills Comparison",
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            showlegend=True,
            width=600,
            height=600
        )
        
        return fig
    
    @staticmethod
    def create_skill_comparison_chart(results: List[Dict], max_candidates: int = 5) -> go.Figure:
        """Create a comprehensive skill comparison chart"""
        
        top_candidates = results[:max_candidates]
        
        # Prepare data for grouped bar chart
        candidates = []
        skills_scores = []
        experience_scores = []
        education_scores = []
        overall_scores = []
        
        for candidate in top_candidates:
            candidates.append(candidate['candidate_name'][:15])
            skills_scores.append(candidate.get('skills_match', {}).get('score', 0))
            experience_scores.append(candidate.get('experience_match', {}).get('score', 0))
            education_scores.append(candidate.get('education_match', {}).get('score', 0))
            overall_scores.append(candidate.get('overall_score', 0))
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Skills Match',
            x=candidates,
            y=skills_scores,
            marker_color='rgb(158,202,225)'
        ))
        
        fig.add_trace(go.Bar(
            name='Experience Match',
            x=candidates,
            y=experience_scores,
            marker_color='rgb(94,158,217)'
        ))
        
        fig.add_trace(go.Bar(
            name='Education Match',
            x=candidates,
            y=education_scores,
            marker_color='rgb(32,102,148)'
        ))
        
        fig.add_trace(go.Bar(
            name='Overall Score',
            x=candidates,
            y=overall_scores,
            marker_color='rgb(255,127,14)'
        ))
        
        fig.update_layout(
            title='Top Candidates - Detailed Score Comparison',
            xaxis_title='Candidates',
            yaxis_title='Scores',
            barmode='group',
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    @staticmethod
    def create_score_distribution_detailed(results: List[Dict]) -> go.Figure:
        """Create detailed score distribution with multiple metrics"""
        
        # Extract all scores
        overall_scores = [r['overall_score'] for r in results]
        weighted_scores = [r['weighted_score'] for r in results]
        skills_scores = [r.get('skills_match', {}).get('score', 0) for r in results]
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=overall_scores,
            name='Overall Scores',
            opacity=0.7,
            nbinsx=15
        ))
        
        fig.add_trace(go.Histogram(
            x=weighted_scores,
            name='Weighted Scores',
            opacity=0.7,
            nbinsx=15
        ))
        
        fig.add_trace(go.Histogram(
            x=skills_scores,
            name='Skills Scores',
            opacity=0.7,
            nbinsx=15
        ))
        
        fig.update_layout(
            title='Score Distribution Comparison',
            xaxis_title='Score Range',
            yaxis_title='Number of Candidates',
            barmode='overlay'
        )
        
        return fig
    
    @staticmethod
    def create_recommendation_pie_chart(results: List[Dict]) -> go.Figure:
        """Create pie chart showing recommendation distribution"""
        
        recommendations = [r.get('overall_fit', {}).get('recommendation', 'UNKNOWN') for r in results]
        
        # Count recommendations
        rec_counts = {}
        for rec in recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        labels = list(rec_counts.keys())
        values = list(rec_counts.values())
        
        colors = {
            'STRONG_FIT': '#2E8B57',
            'GOOD_FIT': '#32CD32', 
            'MODERATE_FIT': '#FFD700',
            'POOR_FIT': '#FF6347',
            'UNKNOWN': '#D3D3D3'
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker_colors=[colors.get(label, '#D3D3D3') for label in labels]
        )])
        
        fig.update_layout(
            title="Candidate Recommendation Distribution",
            annotations=[dict(text='Recommendations', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return fig