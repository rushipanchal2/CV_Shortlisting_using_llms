import streamlit as st
import os
import tempfile
import json
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from src.parsers.resume_parser import ResumeParser
from src.parsers.job_parser import JobDescriptionParser
from src.matching.llm_matcher import LLMResumeJobMatcher
from src.matching.scorer import CandidateRanker

class CVSortingApp:
    def __init__(self):
        self.resume_parser = ResumeParser()
        self.job_parser = JobDescriptionParser()
        self.matcher = LLMResumeJobMatcher()
        self.ranker = CandidateRanker()
        
        # Initialize session state
        if 'processed_resumes' not in st.session_state:
            st.session_state.processed_resumes = []
        if 'job_data' not in st.session_state:
            st.session_state.job_data = None
        if 'ranking_results' not in st.session_state:
            st.session_state.ranking_results = []

def main():
    st.set_page_config(
        page_title="CV Sorting using LLMs",
        page_icon="📄",
        layout="wide"
    )
    
    app = CVSortingApp()
    
    st.title("🎯 CV Sorting System using Free-Tier LLMs")
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Home", "📄 Upload Resumes", "💼 Job Description", "🔍 Matching & Ranking", "📊 Analytics", "⚙️ Settings"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📄 Upload Resumes":
        show_resume_upload_page(app)
    elif page == "💼 Job Description":
        show_job_description_page(app)
    elif page == "🔍 Matching & Ranking":
        show_matching_page(app)
    elif page == "📊 Analytics":
        show_analytics_page(app)
    elif page == "⚙️ Settings":
        show_settings_page()

def show_home_page():
    st.markdown("""
    ## Welcome to the CV Sorting System! 🎉
    
    This application uses state-of-the-art Language Models to automatically sort and rank candidate resumes 
    against job descriptions. Here's how it works:
    
    ### 🚀 Features:
    - **Smart Resume Parsing**: Extracts skills, experience, education, and contact info from PDF/DOCX files
    - **Intelligent Job Analysis**: Uses LLMs to understand job requirements and key criteria
    - **AI-Powered Matching**: Sophisticated matching algorithm using free-tier LLM APIs
    - **Comprehensive Ranking**: Multi-factor scoring with customizable weights
    - **Interactive Analytics**: Visual insights and detailed candidate analysis
    - **Export Capabilities**: Download results in CSV format for further analysis
    
    ### 📋 How to Use:
    1. **Upload Resumes**: Go to the 'Upload Resumes' page and upload candidate CVs
    2. **Add Job Description**: Paste or upload the job description you're hiring for
    3. **Run Matching**: Let our AI analyze and rank all candidates
    4. **Review Results**: Examine detailed match scores and explanations
    5. **Export Data**: Download results for your hiring team
    
    ### 🔧 Technical Details:
    - Uses OpenRouter and Hugging Face free-tier APIs
    - Supports PDF, DOCX, and TXT resume formats
    - Advanced NLP for skill and experience extraction
    - Configurable scoring weights and criteria
    
    **Ready to get started? Use the navigation menu to begin! 👈**
    """)
    
    # Quick stats if data is available
    if st.session_state.processed_resumes:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Resumes Uploaded", len(st.session_state.processed_resumes))
        with col2:
            st.metric("💼 Job Descriptions", 1 if st.session_state.job_data else 0)
        with col3:
            st.metric("🎯 Candidates Ranked", len(st.session_state.ranking_results))

def show_resume_upload_page(app):
    st.header("📄 Upload Candidate Resumes")
    
    st.info("Upload multiple resume files (PDF, DOCX, or TXT format) to begin the sorting process.")
    
    # File upload
    uploaded_files = st.file_uploader(
        "Choose resume files",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="You can upload multiple files at once. Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Process files button
        if st.button("🔄 Process All Resumes", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            processed_resumes = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    # Parse resume
                    resume_data = app.resume_parser.parse_resume(tmp_file_path)
                    resume_data['filename'] = uploaded_file.name
                    processed_resumes.append(resume_data)
                    
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
                
                finally:
                    # Clean up temp file
                    os.unlink(tmp_file_path)
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Store in session state
            st.session_state.processed_resumes = processed_resumes
            status_text.text("✅ All resumes processed successfully!")
            
            st.balloons()
    
    # Display processed resumes
    if st.session_state.processed_resumes:
        st.markdown("---")
        st.subheader("📋 Processed Resumes")
        
        for i, resume in enumerate(st.session_state.processed_resumes):
            with st.expander(f"👤 {resume.get('contact_info', {}).get('name', f'Candidate {i+1}')} - {resume.get('filename', 'Unknown')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Contact Information:**")
                    contact = resume.get('contact_info', {})
                    st.write(f"📧 Email: {contact.get('email', 'Not found')}")
                    st.write(f"📱 Phone: {contact.get('phone', 'Not found')}")
                    
                    st.markdown("**Skills Found:**")
                    skills = resume.get('skills', [])
                    if skills:
                        st.write(", ".join(skills[:10]) + ("..." if len(skills) > 10 else ""))
                    else:
                        st.write("No skills extracted")
                
                with col2:
                    st.markdown("**Experience:**")
                    experience = resume.get('experience', [])
                    st.write(f"Experience entries: {len(experience)}")
                    
                    st.markdown("**Education:**")
                    education = resume.get('education', [])
                    st.write(f"Education entries: {len(education)}")
                    
                # Show raw text preview
                if st.checkbox(f"Show raw text preview for {resume.get('filename', 'this resume')}", key=f"show_text_{i}"):
                    st.text_area(
                        "Raw extracted text:",
                        value=resume.get('raw_text', '')[:500] + "..." if len(resume.get('raw_text', '')) > 500 else resume.get('raw_text', ''),
                        height=100,
                        key=f"raw_text_{i}"
                    )

def show_job_description_page(app):
    st.header("💼 Job Description Analysis")
    
    st.info("Provide the job description to match candidates against. The AI will extract key requirements automatically.")
    
    # Input methods
    input_method = st.radio(
        "How would you like to provide the job description?",
        ["✏️ Paste Text", "📁 Upload File"]
    )
    
    job_text = ""
    
    if input_method == "✏️ Paste Text":
        job_text = st.text_area(
            "Paste the job description here:",
            height=300,
            placeholder="Paste the complete job description including requirements, responsibilities, qualifications, etc."
        )
    
    elif input_method == "📁 Upload File":
        uploaded_job_file = st.file_uploader(
            "Upload job description file",
            type=['txt', 'pdf', 'docx'],
            help="Upload a file containing the job description"
        )
        
        if uploaded_job_file:
            # Save and read file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_job_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_job_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                job_text = app.resume_parser.extract_text(tmp_file_path)  # Reuse text extraction
                st.text_area("Extracted job description:", value=job_text, height=200)
            except Exception as e:
                st.error(f"Error reading file: {e}")
            finally:
                os.unlink(tmp_file_path)
    
    # Process job description
    if job_text and st.button("🔍 Analyze Job Description", type="primary"):
        with st.spinner("Analyzing job description using AI..."):
            try:
                job_data = app.job_parser.parse_job_description(job_text)
                st.session_state.job_data = job_data
                
                st.success("✅ Job description analyzed successfully!")
                
                # Display extracted information
                st.markdown("---")
                st.subheader("📊 Extracted Job Information")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Job Details:**")
                    st.write(f"🏢 **Title:** {job_data.get('job_title', 'Not specified')}")
                    st.write(f"🏢 **Company:** {job_data.get('company_info', 'Not specified')}")
                    st.write(f"📍 **Location:** {job_data.get('location', 'Not specified')}")
                    st.write(f"⏳ **Experience Required:** {job_data.get('experience_required', 'Not specified')}")
                    st.write(f"🎓 **Education Required:** {job_data.get('education_required', 'Not specified')}")
                
                with col2:
                    st.markdown("**Required Skills:**")
                    required_skills = job_data.get('required_skills', [])
                    if required_skills:
                        for skill in required_skills[:10]:  # Show first 10
                            st.write(f"• {skill}")
                        if len(required_skills) > 10:
                            st.write(f"... and {len(required_skills) - 10} more")
                    else:
                        st.write("No specific skills extracted")
                
                # Key requirements
                if job_data.get('key_requirements'):
                    st.markdown("**🎯 Key Requirements:**")
                    for req in job_data.get('key_requirements', [])[:5]:
                        st.write(f"• {req}")
                
                # Responsibilities
                if job_data.get('responsibilities'):
                    st.markdown("**📋 Responsibilities:**")
                    for resp in job_data.get('responsibilities', [])[:3]:
                        st.write(f"• {resp}")
                
            except Exception as e:
                st.error(f"Error analyzing job description: {e}")
    
    # Show current job data if available
    elif st.session_state.job_data:
        st.markdown("---")
        st.subheader("📊 Current Job Description")
        job_data = st.session_state.job_data
        
        st.info(f"Currently analyzing for: **{job_data.get('job_title', 'Unknown Position')}**")
        
        with st.expander("View job details"):
            st.json(job_data)
        
        if st.button("🗑️ Clear Job Description"):
            st.session_state.job_data = None
            st.experimental_rerun()

def show_matching_page(app):
    st.header("🔍 Resume Matching & Ranking")
    
    # Check if we have the required data
    if not st.session_state.processed_resumes:
        st.warning("⚠️ No resumes uploaded yet. Please go to the 'Upload Resumes' page first.")
        return
    
    if not st.session_state.job_data:
        st.warning("⚠️ No job description provided yet. Please go to the 'Job Description' page first.")
        return
    
    # Display summary
    st.success(f"✅ Ready to match {len(st.session_state.processed_resumes)} candidates against '{st.session_state.job_data.get('job_title', 'the position')}'")
    
    # Matching configuration
    st.subheader("⚙️ Matching Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Scoring Weights:**")
        skills_weight = st.slider("Skills Match Weight", 0.0, 1.0, 0.3, 0.05)
        experience_weight = st.slider("Experience Match Weight", 0.0, 1.0, 0.25, 0.05)
        education_weight = st.slider("Education Match Weight", 0.0, 1.0, 0.2, 0.05)
        overall_weight = st.slider("Overall Fit Weight", 0.0, 1.0, 0.25, 0.05)
    
    with col2:
        st.markdown("**Options:**")
        show_detailed_analysis = st.checkbox("Show detailed match analysis", value=True)
        auto_export = st.checkbox("Auto-export results to CSV", value=False)
        max_candidates = st.number_input("Max candidates to display", min_value=5, max_value=50, value=10)
    
    # Normalize weights
    total_weight = skills_weight + experience_weight + education_weight + overall_weight
    if total_weight > 0:
        skills_weight /= total_weight
        experience_weight /= total_weight
        education_weight /= total_weight
        overall_weight /= total_weight
    
    # Run matching
    if st.button("🚀 Start Matching Process", type="primary"):
        with st.spinner("🤖 AI is analyzing candidates... This may take a few minutes."):
            try:
                # Update weights in ranker
                app.ranker.weights = {
                    'skills_match': skills_weight,
                    'experience_match': experience_weight,
                    'education_match': education_weight,
                    'overall_fit': overall_weight,
                    'keywords_match': 0  # Not used in this implementation
                }
                
                # Run batch matching
                match_results = app.matcher.batch_match_candidates(
                    st.session_state.processed_resumes,
                    st.session_state.job_data
                )
                
                # Rank candidates
                ranked_results = app.ranker.rank_candidates(match_results)
                
                # Store results
                st.session_state.ranking_results = ranked_results
                
                st.success(f"✅ Successfully analyzed {len(ranked_results)} candidates!")
                
                # Auto-export if enabled
                if auto_export and ranked_results:
                    df = app.ranker.export_results_to_csv(ranked_results)
                    st.download_button(
                        label="📥 Download Results CSV",
                        data=df.to_csv(index=False),
                        file_name=f"candidate_ranking_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )
                
            except Exception as e:
                st.error(f"Error during matching process: {e}")
                st.exception(e)
    
    # Display results
    if st.session_state.ranking_results:
        st.markdown("---")
        st.subheader("🏆 Ranking Results")
        
        results = st.session_state.ranking_results[:max_candidates]
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👑 Top Score", f"{results[0]['weighted_score']:.1f}")
        
        with col2:
            avg_score = sum(r['weighted_score'] for r in results) / len(results)
            st.metric("📊 Average Score", f"{avg_score:.1f}")
        
        with col3:
            strong_fits = sum(1 for r in results if r.get('overall_fit', {}).get('recommendation') == 'STRONG_FIT')
            st.metric("💪 Strong Fits", strong_fits)
        
        with col4:
            st.metric("📈 Total Analyzed", len(results))
        
        # Detailed results
        for i, result in enumerate(results):
            with st.expander(f"#{result['rank']} - {result['candidate_name']} (Score: {result['weighted_score']:.1f})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 Scores Breakdown:**")
                    st.write(f"🎯 **Overall Score:** {result['overall_score']:.1f}/100")
                    st.write(f"🔧 **Skills Match:** {result.get('skills_match', {}).get('score', 0):.1f}/100")
                    st.write(f"💼 **Experience Match:** {result.get('experience_match', {}).get('score', 0):.1f}/100")
                    st.write(f"🎓 **Education Match:** {result.get('education_match', {}).get('score', 0):.1f}/100")
                    st.write(f"⚖️ **Weighted Score:** {result['weighted_score']:.1f}/100")
                    
                    recommendation = result.get('overall_fit', {}).get('recommendation', 'UNKNOWN')
                    color = {"STRONG_FIT": "🟢", "GOOD_FIT": "🟡", "MODERATE_FIT": "🟠", "POOR_FIT": "🔴"}.get(recommendation, "⚪")
                    st.write(f"📋 **Recommendation:** {color} {recommendation}")
                
                with col2:
                    st.markdown("**✅ Strengths:**")
                    strengths = result.get('overall_fit', {}).get('strengths', [])
                    for strength in strengths[:5]:
                        st.write(f"• {strength}")
                    
                    st.markdown("**⚠️ Concerns:**")
                    concerns = result.get('overall_fit', {}).get('concerns', [])
                    for concern in concerns[:5]:
                        st.write(f"• {concern}")
                
                if show_detailed_analysis:
                    st.markdown("**🔍 Detailed Analysis:**")
                    
                    # Skills analysis
                    skills_match = result.get('skills_match', {})
                    if skills_match:
                        st.markdown("*Skills Analysis:*")
                        st.write(f"Matched: {', '.join(skills_match.get('matched_skills', [])[:5])}")
                        st.write(f"Missing: {', '.join(skills_match.get('missing_skills', [])[:5])}")
                        st.write(f"Explanation: {skills_match.get('explanation', 'N/A')}")
                    
                    # Overall fit explanation
                    overall_explanation = result.get('overall_fit', {}).get('explanation', 'No detailed explanation available')
                    st.write(f"**Overall Assessment:** {overall_explanation}")

def show_analytics_page_1(app):
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.ranking_results:
        st.warning("⚠️ No ranking results available yet. Please complete the matching process first.")
        return
    
    results = st.session_state.ranking_results
    job_data = st.session_state.job_data
    
    # Generate summary report
    summary_report = app.ranker.generate_summary_report(results, job_data)
    
    # Overview metrics
    st.subheader("📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", summary_report['job_info']['total_candidates'])
    
    with col2:
        st.metric("Average Score", f"{summary_report['score_statistics']['average_score']:.1f}")
    
    with col3:
        st.metric("Highest Score", f"{summary_report['score_statistics']['highest_score']:.1f}")
    
    with col4:
        st.metric("Score Range", f"{summary_report['score_statistics']['highest_score'] - summary_report['score_statistics']['lowest_score']:.1f}")
    
    # Score distribution chart
    st.subheader("📊 Score Distribution")
    
    scores = [r['weighted_score'] for r in results]
    names = [r['candidate_name'] for r in results]
    
    fig = px.histogram(
        x=scores,
        nbins=10,
        title="Distribution of Candidate Scores",
        labels={'x': 'Weighted Score', 'y': 'Number of Candidates'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Top candidates comparison
    st.subheader("🏆 Top Candidates Comparison")
    
    top_candidates = results[:5]
    categories = ['Skills Match', 'Experience Match', 'Education Match', 'Overall Score']
    
    fig = go.Figure()
    
    for candidate in top_candidates:
        scores_list = [
            candidate.get('skills_match', {}).get('score', 0),
            candidate.get('experience_match', {}).get('score', 0),
            candidate.get('education_match', {}).get('score', 0),
            candidate.get('overall_score', 0)
        ]
        
        fig.add_trace(go.Radar(
            r=scores_list,
            theta=categories,
            fill='toself',
            name=candidate['candidate_name'][:20]  # Truncate long names
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Top 5 Candidates - Skills Comparison"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Skill gap analysis
    st.subheader("🎯 Skill Gap Analysis")
    
    skill_analysis = summary_report.get('skill_analysis', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Most Common Missing Skills:**")
        missing_skills = skill_analysis.get('most_common_gaps', [])
        for skill, count in missing_skills:
            percentage = (count / len(results)) * 100
            st.write(f"• **{skill}**: {count} candidates ({percentage:.1f}%)")
    
    with col2:
        st.markdown("**Most Common Matched Skills:**")
        matched_skills = skill_analysis.get('most_common_matches', [])
        for skill, count in matched_skills:
            percentage = (count / len(results)) * 100
            st.write(f"• **{skill}**: {count} candidates ({percentage:.1f}%)")
    
    # Recommendations
    st.subheader("💡 Hiring Recommendations")
    
    recommendations = summary_report.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Export options
    st.subheader("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Full Results"):
            df = app.ranker.export_results_to_csv(results)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Results CSV",
                data=csv_data,
                file_name=f"full_candidate_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🏆 Export Top 10"):
            top_10_df = app.ranker.export_results_to_csv(results[:10])
            csv_data = top_10_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Top 10 CSV",
                data=csv_data,
                file_name=f"top_10_candidates_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Export Summary Report"):
            summary_json = json.dumps(summary_report, indent=2)
            st.download_button(
                label="📥 Download Summary JSON",
                data=summary_json,
                file_name=f"hiring_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )

def show_settings_page():
    st.header("⚙️ System Settings")
    
    st.subheader("🔑 API Configuration")
    
    st.info("Configure your free-tier LLM API keys. You can get free keys from:")
    st.markdown("""
    - **OpenRouter**: [https://openrouter.ai](https://openrouter.ai) - Free tier available
    - **Hugging Face**: [https://huggingface.co](https://huggingface.co) - Free inference API
    """)
    
    # API Key inputs
    openrouter_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        help="Get a free API key from OpenRouter for access to various free models"
    )
    
    huggingface_key = st.text_input(
        "Hugging Face API Key",
        type="password",
        help="Get a free API key from Hugging Face for their inference API"
    )
    
    if st.button("💾 Save API Keys"):
        # In a real application, you'd save these securely
        # For demo purposes, we'll just show a success message
        if openrouter_key or huggingface_key:
            st.success("✅ API keys updated! Please restart the application to apply changes.")
            st.info("💡 In production, add these to your .env file:\n```\nOPENROUTER_API_KEY=your_key_here\nHUGGINGFACE_API_KEY=your_key_here\n```")
        else:
            st.warning("Please provide at least one API key.")
    
    st.markdown("---")
    
    st.subheader("🎛️ Scoring Preferences")
    
    st.markdown("Default scoring weights for candidate evaluation:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.slider("Skills Match Weight", 0.0, 1.0, 0.3, 0.05, key="default_skills_weight")
        st.slider("Experience Match Weight", 0.0, 1.0, 0.25, 0.05, key="default_experience_weight")
    
    with col2:
        st.slider("Education Match Weight", 0.0, 1.0, 0.2, 0.05, key="default_education_weight")
        st.slider("Overall Fit Weight", 0.0, 1.0, 0.25, 0.05, key="default_overall_weight")
    
    st.markdown("---")
    
    st.subheader("📁 File Processing Settings")
    
    max_file_size = st.number_input("Max file size (MB)", min_value=1, max_value=50, value=10)
    supported_formats = st.multiselect(
        "Supported file formats",
        ['.pdf', '.docx', '.txt'],
        default=['.pdf', '.docx', '.txt']
    )
    
    st.markdown("---")
    
    st.subheader("🔧 System Information")
    
    st.info("""
    **CV Sorting System v1.0**
    
    - Built with Streamlit and Python
    - Uses free-tier LLM APIs for cost-effective processing
    - Supports multiple resume formats
    - Provides detailed matching analytics
    - Exportable results for hiring teams
    
    For support or feature requests, please check the README.md file.
    """)


def show_analytics_page(app):
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.ranking_results:
        st.warning("⚠️ No ranking results available yet. Please complete the matching process first.")
        return
    
    results = st.session_state.ranking_results
    job_data = st.session_state.job_data
    
    # Import charts helper
    try:
        from src.ui.charts import CompatibleCharts
        charts = CompatibleCharts()
    except ImportError:
        charts = None
    
    # Generate summary report
    summary_report = app.ranker.generate_summary_report(results, job_data)
    
    # Overview metrics
    st.subheader("📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", summary_report['job_info']['total_candidates'])
    
    with col2:
        st.metric("Average Score", f"{summary_report['score_statistics']['average_score']:.1f}")
    
    with col3:
        st.metric("Highest Score", f"{summary_report['score_statistics']['highest_score']:.1f}")
    
    with col4:
        st.metric("Score Range", f"{summary_report['score_statistics']['highest_score'] - summary_report['score_statistics']['lowest_score']:.1f}")
    
    # Recommendation distribution
    st.subheader("🎯 Recommendation Overview")
    
    if charts:
        rec_fig = charts.create_recommendation_pie_chart(results)
        st.plotly_chart(rec_fig, use_container_width=True)
    else:
        # Fallback: Simple text summary
        recommendations = [r.get('overall_fit', {}).get('recommendation', 'UNKNOWN') for r in results]
        rec_counts = {}
        for rec in recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🟢 Strong Fit", rec_counts.get('STRONG_FIT', 0))
        with col2:
            st.metric("🟡 Good Fit", rec_counts.get('GOOD_FIT', 0))
        with col3:
            st.metric("🟠 Moderate Fit", rec_counts.get('MODERATE_FIT', 0))
        with col4:
            st.metric("🔴 Poor Fit", rec_counts.get('POOR_FIT', 0))
    
    # Score distribution chart
    st.subheader("📊 Score Distribution")
    
    if charts:
        dist_fig = charts.create_score_distribution_detailed(results)
        st.plotly_chart(dist_fig, use_container_width=True)
    else:
        # Fallback: Simple histogram
        scores = [r['weighted_score'] for r in results]
        fig = px.histogram(
            x=scores,
            nbins=10,
            title="Distribution of Candidate Scores",
            labels={'x': 'Weighted Score', 'y': 'Number of Candidates'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top candidates comparison
    st.subheader("🏆 Top Candidates Comparison")
    
    if charts:
        comp_fig = charts.create_skill_comparison_chart(results)
        st.plotly_chart(comp_fig, use_container_width=True)
    else:
        # Fallback: Bar chart comparison
        top_candidates = results[:5]
        comparison_data = []
        for candidate in top_candidates:
            comparison_data.extend([
                {
                    'Candidate': candidate['candidate_name'][:15],
                    'Metric': 'Skills Match',
                    'Score': candidate.get('skills_match', {}).get('score', 0)
                },
                {
                    'Candidate': candidate['candidate_name'][:15],
                    'Metric': 'Experience Match',
                    'Score': candidate.get('experience_match', {}).get('score', 0)
                },
                {
                    'Candidate': candidate['candidate_name'][:15],
                    'Metric': 'Education Match',
                    'Score': candidate.get('education_match', {}).get('score', 0)
                },
                {
                    'Candidate': candidate['candidate_name'][:15],
                    'Metric': 'Overall Score',
                    'Score': candidate.get('overall_score', 0)
                }
            ])
        
        df_comparison = pd.DataFrame(comparison_data)
        
        fig = px.bar(
            df_comparison,
            x='Metric',
            y='Score',
            color='Candidate',
            title="Top 5 Candidates - Skills Comparison",
            barmode='group'
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    # Score trends line chart
    st.subheader("📈 Score Trends")
    
    line_data = []
    for i, result in enumerate(results[:10]):
        line_data.append({
            'Rank': i + 1,
            'Candidate': result['candidate_name'][:15],
            'Weighted Score': result['weighted_score'],
            'Skills Score': result.get('skills_match', {}).get('score', 0),
            'Experience Score': result.get('experience_match', {}).get('score', 0)
        })
    
    df_line = pd.DataFrame(line_data)
    
    fig = px.line(
        df_line,
        x='Rank',
        y=['Weighted Score', 'Skills Score', 'Experience Score'],
        title="Score Trends Across Top 10 Candidates",
        markers=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Skill gap analysis
    st.subheader("🎯 Skill Gap Analysis")
    
    skill_analysis = summary_report.get('skill_analysis', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Most Common Missing Skills:**")
        missing_skills = skill_analysis.get('most_common_gaps', [])
        if missing_skills:
            missing_df = pd.DataFrame(missing_skills, columns=['Skill', 'Count'])
            missing_df['Percentage'] = (missing_df['Count'] / len(results)) * 100
            
            fig = px.bar(
                missing_df.head(10),
                x='Count',
                y='Skill',
                title="Top 10 Missing Skills",
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No missing skills data available")
    
    with col2:
        st.markdown("**Most Common Matched Skills:**")
        matched_skills = skill_analysis.get('most_common_matches', [])
        if matched_skills:
            matched_df = pd.DataFrame(matched_skills, columns=['Skill', 'Count'])
            matched_df['Percentage'] = (matched_df['Count'] / len(results)) * 100
            
            fig = px.bar(
                matched_df.head(10),
                x='Count',
                y='Skill',
                title="Top 10 Matched Skills",
                orientation='h'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No matched skills data available")
    
    # Detailed candidate analysis table
    st.subheader("📋 Detailed Candidate Analysis")
    
    # Create summary table
    table_data = []
    for result in results[:20]:  # Show top 20
        table_data.append({
            'Rank': result['rank'],
            'Name': result['candidate_name'][:25],
            'Overall Score': f"{result['overall_score']:.1f}",
            'Weighted Score': f"{result['weighted_score']:.1f}",
            'Skills': f"{result.get('skills_match', {}).get('score', 0):.1f}",
            'Experience': f"{result.get('experience_match', {}).get('score', 0):.1f}",
            'Education': f"{result.get('education_match', {}).get('score', 0):.1f}",
            'Recommendation': result.get('overall_fit', {}).get('recommendation', 'N/A'),
            'Top Strength': result.get('overall_fit', {}).get('strengths', ['N/A'])[0] if result.get('overall_fit', {}).get('strengths') else 'N/A'
        })
    
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True)
    
    # Recommendations
    st.subheader("💡 Hiring Recommendations")
    
    recommendations = summary_report.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Export options
    st.subheader("📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Full Results"):
            df = app.ranker.export_results_to_csv(results)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Results CSV",
                data=csv_data,
                file_name=f"full_candidate_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🏆 Export Top 10"):
            top_10_df = app.ranker.export_results_to_csv(results[:10])
            csv_data = top_10_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Top 10 CSV",
                data=csv_data,
                file_name=f"top_10_candidates_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("📋 Export Summary Report"):
            summary_json = json.dumps(summary_report, indent=2)
            st.download_button(
                label="📥 Download Summary JSON",
                data=summary_json,
                file_name=f"hiring_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )


if __name__ == "__main__":
    main()