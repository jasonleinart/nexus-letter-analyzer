"""Streamlit web interface for the Nexus Letter AI Analyzer."""

import streamlit as st
import time
from typing import Dict, Any
from ai_analyzer import create_analyzer, NexusLetterAnalyzer
from text_processor import create_processor, TextProcessor
from config import get_settings, validate_openai_key
from scoring_engine import create_scorer, VAComplianceScorer
from recommendation_engine import create_recommendation_engine, RecommendationEngine
from database import create_database, AnalysisDatabase
from analytics import display_analytics_dashboard


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Nexus Letter AI Analyzer",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )


def display_header():
    """Display the application header and description."""
    st.title("⚖️ Nexus Letter AI Analyzer")
    st.markdown("""
    **Professional AI-powered analysis of VA disability nexus letters**
    
    This tool uses OpenAI GPT-4 to analyze nexus letters for legal strength, medical opinion quality, 
    and compliance with VA disability claim requirements.
    """)
    
    # Add divider
    st.divider()


def display_sidebar_info():
    """Display information in the sidebar."""
    with st.sidebar:
        st.header("About This Tool")
        st.markdown("""
        **Nexus Letter AI Analyzer** helps disability law professionals evaluate 
        the strength and completeness of medical nexus letters for VA disability claims.
        
        **Key Features:**
        - Real-time GPT-4 analysis
        - Legal strength assessment
        - Medical opinion evaluation
        - Improvement recommendations
        
        **Requirements:**
        - Valid OpenAI API key
        - Nexus letter text (100+ chars)
        - Professional medical content
        """)
        
        st.markdown("---")
        st.markdown("**Developed for Disability Law Group**")
        st.markdown("*AI Systems & Technology Integration*")


def check_api_key_setup() -> bool:
    """
    Check if OpenAI API key is properly configured.
    
    Returns:
        True if API key is valid, False otherwise
    """
    is_valid, error_msg = validate_openai_key()
    
    if not is_valid:
        st.error("⚠️ **OpenAI API Key Required**")
        st.markdown(f"""
        **Issue:** {error_msg}
        
        **To fix this:**
        1. Create a `.env` file in the project directory
        2. Add your OpenAI API key: `OPENAI_API_KEY=sk-your-key-here`
        3. Restart the application
        
        **Alternative:** Set the environment variable directly:
        ```bash
        export OPENAI_API_KEY=sk-your-key-here
        ```
        """)
        return False
    
    return True


def get_user_input() -> tuple[str, TextProcessor]:
    """
    Get and validate user input.
    
    Returns:
        Tuple of (letter_text, processor_instance)
    """
    processor = create_processor()
    
    st.subheader("📄 Nexus Letter Input")
    
    # Create columns for input area and stats
    col1, col2 = st.columns([3, 1])
    
    with col1:
        letter_text = st.text_area(
            "Enter the complete nexus letter text:",
            height=400,
            placeholder="""Paste the complete nexus letter here, including:
- Header information (medical facility, date)
- Recipient information
- Medical opinion statement
- Service connection rationale
- Doctor's signature and credentials

Example start:
[Medical Facility Name]
[Address]
[Date]

RE: Nexus Letter for [Veteran Name]

To Whom It May Concern,

I am [Doctor Name], a licensed [specialty]...""",
            help="Enter the full text of the nexus letter to be analyzed"
        )
    
    with col2:
        # Display text statistics
        if letter_text:
            stats = processor.get_text_stats(letter_text)
            st.markdown("**Text Statistics**")
            st.metric("Characters", stats['character_count'])
            st.metric("Words", stats['word_count'])
            st.metric("Sentences", stats['sentence_count'])
            st.metric("Paragraphs", stats['paragraph_count'])
            
            # Show validation status
            is_valid, validation_msg = processor.validate_input(letter_text)
            if is_valid:
                st.success("✅ Ready for analysis")
            else:
                st.warning(f"⚠️ {validation_msg}")
        else:
            st.info("Enter text to see statistics")
    
    return letter_text, processor


def display_loading_analysis():
    """Display loading animation during analysis."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Simulate analysis progress
    steps = [
        "Initializing AI analyzer...",
        "Preprocessing text...",
        "Analyzing medical opinion...",
        "Evaluating service connection...",
        "Assessing legal strength...",
        "Generating recommendations...",
        "Finalizing analysis..."
    ]
    
    for i, step in enumerate(steps):
        status_text.text(step)
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(0.3)  # Small delay for visual effect
    
    status_text.text("Analysis complete!")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()


def display_analysis_results(ai_results: Dict[str, Any], scoring_results: Dict[str, Any], 
                           recommendations: Dict[str, Any], processing_time: float):
    """
    Display the enhanced analysis results with scoring and recommendations.
    
    Args:
        ai_results: Analysis results from AI analyzer
        scoring_results: Results from scoring engine
        recommendations: Results from recommendation engine
        processing_time: Time taken to process
    """
    if ai_results.get('error'):
        st.error(f"**Analysis Error:** {ai_results.get('message', 'Unknown error')}")
        if ai_results.get('details'):
            st.code(ai_results['details'])
        return
    
    analysis = ai_results.get('analysis', {})
    overall_score = scoring_results.get('overall_score', 0)
    workflow_rec = recommendations.get('workflow_recommendation')
    
    # Overall score header with color coding
    if overall_score >= 85:
        st.success(f"{workflow_rec.icon if workflow_rec else '🟢'} **Overall Score: {overall_score}/100**")
        if workflow_rec:
            st.success(workflow_rec.message)
    elif overall_score >= 70:
        st.warning(f"{workflow_rec.icon if workflow_rec else '🟡'} **Overall Score: {overall_score}/100**")
        if workflow_rec:
            st.warning(workflow_rec.message)
    else:
        st.error(f"{workflow_rec.icon if workflow_rec else '🔴'} **Overall Score: {overall_score}/100**")
        if workflow_rec:
            st.error(workflow_rec.message)
    
    # Component scores with progress visualization
    st.subheader("📊 Component Analysis")
    
    components = [
        ('Medical Opinion', scoring_results.get('medical_opinion_breakdown')),
        ('Service Connection', scoring_results.get('service_connection_breakdown')),
        ('Medical Rationale', scoring_results.get('medical_rationale_breakdown')),
        ('Professional Format', scoring_results.get('professional_format_breakdown'))
    ]
    
    # Display component scores in two columns
    col1, col2 = st.columns(2)
    
    for i, (name, breakdown) in enumerate(components):
        col = col1 if i % 2 == 0 else col2
        with col:
            if breakdown and hasattr(breakdown, 'score'):
                score = breakdown.score
                max_score = breakdown.max_score
                progress = score / max_score if max_score > 0 else 0
                
                # Color based on percentage
                if progress >= 0.8:
                    color = "green"
                elif progress >= 0.6:
                    color = "orange"
                else:
                    color = "red"
                
                st.markdown(f"**{name}**")
                st.progress(progress)
                st.markdown(f"<span style='color: {color}; font-weight: bold'>{score}/{max_score} points</span>", 
                           unsafe_allow_html=True)
                
                # Show breakdown in expander
                with st.expander(f"View {name} Details"):
                    if hasattr(breakdown, 'criteria') and breakdown.criteria:
                        for criterion, points in breakdown.criteria.items():
                            st.markdown(f"• **{criterion.replace('_', ' ').title()}:** {points} points")
                    if hasattr(breakdown, 'rationale'):
                        st.markdown(f"*{breakdown.rationale}*")
            else:
                st.markdown(f"**{name}**")
                st.progress(0)
                st.markdown("0/25 points")
    
    st.divider()
    
    # Key findings and recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Key Findings")
        
        # Display key strengths
        if 'key_strengths' in analysis and analysis['key_strengths']:
            st.markdown("**Strengths:**")
            for strength in analysis['key_strengths'][:3]:
                st.markdown(f"✅ {strength}")
        
        # Display critical issues
        if 'critical_issues' in analysis and analysis['critical_issues']:
            st.markdown("**Critical Issues:**")
            for issue in analysis['critical_issues']:
                st.markdown(f"⚠️ {issue}")
        
        # Primary conditions
        if analysis.get('primary_condition'):
            st.markdown(f"**Primary Condition:** {analysis['primary_condition']}")
        if analysis.get('probability_language'):
            st.markdown(f"**Probability Language:** \"{analysis['probability_language']}\"")
    
    with col2:
        st.subheader("📋 Priority Improvements")
        
        improvements = recommendations.get('improvement_suggestions', [])
        critical_count = recommendations.get('critical_issues', 0)
        
        if critical_count > 0:
            st.error(f"**{critical_count} Critical Issues** require immediate attention")
        
        # Show top 5 improvements
        for i, improvement in enumerate(improvements[:5]):
            if hasattr(improvement, 'impact'):
                impact_icon = {
                    'critical': '🔴',
                    'high': '🟡',
                    'medium': '🟢',
                    'low': '🔵'
                }.get(improvement.impact, '⚪')
                
                st.markdown(f"{impact_icon} **{improvement.component.replace('_', ' ').title()}**")
                st.markdown(f"   {improvement.suggestion}")
                if hasattr(improvement, 'example') and improvement.example:
                    st.info(f"Example: {improvement.example}")
    
    # Workflow next steps
    if workflow_rec and hasattr(workflow_rec, 'next_steps'):
        st.subheader("🚀 Next Steps")
        for i, step in enumerate(workflow_rec.next_steps, 1):
            st.markdown(f"{i}. {step}")
    
    # Client summary
    client_summary = recommendations.get('client_summary')
    if client_summary:
        st.subheader("📝 Client Summary")
        st.markdown(client_summary)
    
    # Attorney notes (if applicable)
    attorney_notes = recommendations.get('attorney_notes')
    if attorney_notes:
        with st.expander("⚖️ Attorney Review Notes"):
            st.markdown(attorney_notes)
    
    # Performance metrics
    st.divider()
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    
    with metrics_col1:
        st.metric("Processing Time", f"{processing_time:.1f}s")
    with metrics_col2:
        st.metric("Nexus Strength", analysis.get('nexus_strength', 'Unknown'))
    with metrics_col3:
        total_improvements = recommendations.get('total_improvements', 0)
        st.metric("Total Improvements", total_improvements)
    
    # Export options
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📋 Copy Full Report", help="Copy complete analysis report"):
            # Create formatted text for copying
            export_text = format_enhanced_results_for_export(
                analysis, scoring_results, recommendations, processing_time
            )
            st.code(export_text, language=None)
    
    with col2:
        st.markdown("*Complete analysis report with scoring and recommendations*")


def format_enhanced_results_for_export(analysis: Dict[str, Any], scoring_results: Dict[str, Any],
                                      recommendations: Dict[str, Any], processing_time: float) -> str:
    """
    Format enhanced analysis results for export/copying.
    
    Args:
        analysis: AI analysis results
        scoring_results: Scoring engine results  
        recommendations: Recommendation engine results
        processing_time: Processing time in seconds
        
    Returns:
        Formatted text string
    """
    lines = [
        "NEXUS LETTER ANALYSIS REPORT",
        "=" * 60,
        "",
        f"Overall Score: {scoring_results.get('overall_score', 0)}/100",
        f"Processing Time: {processing_time:.1f} seconds",
        "",
        "COMPONENT SCORES:",
        "-" * 40,
    ]
    
    # Add component scores
    components = [
        ('Medical Opinion', scoring_results.get('medical_opinion_breakdown')),
        ('Service Connection', scoring_results.get('service_connection_breakdown')),
        ('Medical Rationale', scoring_results.get('medical_rationale_breakdown')),
        ('Professional Format', scoring_results.get('professional_format_breakdown'))
    ]
    
    for name, breakdown in components:
        if breakdown and hasattr(breakdown, 'score'):
            lines.append(f"{name}: {breakdown.score}/{breakdown.max_score} points")
            if hasattr(breakdown, 'rationale'):
                lines.append(f"  - {breakdown.rationale}")
    
    lines.extend([
        "",
        "WORKFLOW RECOMMENDATION:",
        "-" * 40,
    ])
    
    workflow_rec = recommendations.get('workflow_recommendation')
    if workflow_rec:
        lines.append(f"Decision: {workflow_rec.decision.replace('_', ' ').upper()}")
        lines.append(f"Message: {workflow_rec.message}")
        lines.append("")
        lines.append("Next Steps:")
        for i, step in enumerate(workflow_rec.next_steps, 1):
            lines.append(f"  {i}. {step}")
    
    lines.extend([
        "",
        "KEY FINDINGS:",
        "-" * 40,
    ])
    
    lines.append(f"Nexus Strength: {analysis.get('nexus_strength', 'Unknown')}")
    lines.append(f"Primary Condition: {analysis.get('primary_condition', 'Not specified')}")
    if analysis.get('probability_language'):
        lines.append(f"Probability Language: \"{analysis['probability_language']}\"")
    
    if analysis.get('key_strengths'):
        lines.extend([
            "",
            "Strengths:",
        ])
        for strength in analysis['key_strengths']:
            lines.append(f"  • {strength}")
    
    if analysis.get('critical_issues'):
        lines.extend([
            "",
            "Critical Issues:",
        ])
        for issue in analysis['critical_issues']:
            lines.append(f"  • {issue}")
    
    improvements = recommendations.get('improvement_suggestions', [])
    if improvements:
        lines.extend([
            "",
            "PRIORITY IMPROVEMENTS:",
            "-" * 40,
        ])
        
        for i, imp in enumerate(improvements[:10], 1):
            if hasattr(imp, 'component'):
                lines.append(f"{i}. {imp.component.replace('_', ' ').title()} ({imp.impact})")
                lines.append(f"   Issue: {imp.issue}")
                lines.append(f"   Fix: {imp.suggestion}")
                if hasattr(imp, 'example') and imp.example:
                    lines.append(f"   Example: {imp.example}")
                lines.append("")
    
    client_summary = recommendations.get('client_summary')
    if client_summary:
        lines.extend([
            "",
            "CLIENT SUMMARY:",
            "-" * 40,
            client_summary
        ])
    
    lines.extend([
        "",
        f"Analysis generated by Nexus Letter AI Analyzer v2.0",
        f"Powered by OpenAI GPT-4 with VA Compliance Scoring",
        f"© Disability Law Group - AI Systems & Technology Integration"
    ])
    
    return "\n".join(lines)


def main():
    """Main application function."""
    configure_page()
    display_header()
    display_sidebar_info()
    
    # Check API key configuration first
    if not check_api_key_setup():
        st.stop()
    
    # Create tabs for main interface and analytics
    tab1, tab2 = st.tabs(["📝 Letter Analysis", "📈 Analytics Dashboard"])
    
    with tab1:
        # Get user input
        letter_text, processor = get_user_input()
        
        # Analysis section
        if st.button("🚀 Analyze Nexus Letter", type="primary", use_container_width=True):
            if not letter_text:
                st.warning("Please enter nexus letter text to analyze.")
                return
            
            # Validate input
            is_valid, validation_msg = processor.validate_input(letter_text)
            if not is_valid:
                st.error(f"**Input Validation Failed:** {validation_msg}")
                return
            
            # Show loading animation
            with st.spinner("Analyzing nexus letter..."):
                display_loading_analysis()
                
                # Create components and perform analysis
                try:
                    # Track processing time
                    start_time = time.time()
                    
                    # Initialize components
                    analyzer = create_analyzer()
                    scorer = create_scorer()
                    rec_engine = create_recommendation_engine()
                    database = create_database()
                    
                    # Test connection first
                    success, msg = analyzer.test_connection()
                    if not success:
                        st.error(f"**API Connection Failed:** {msg}")
                        return
                    
                    # Preprocess text
                    processed_text = processor.preprocess_for_ai(letter_text)
                    
                    # Perform AI analysis
                    ai_results = analyzer.analyze_letter(processed_text)
                    
                    if ai_results.get('error'):
                        st.error("AI analysis failed. Please try again.")
                        return
                    
                    # Calculate scores
                    scoring_results = scorer.calculate_total_score(ai_results['analysis'])
                    
                    # Generate recommendations
                    recommendations = rec_engine.generate_recommendations(
                        scoring_results['overall_score'],
                        scoring_results,
                        ai_results['analysis']
                    )
                    
                    # Calculate processing time
                    processing_time = time.time() - start_time
                    
                    # Save to database
                    try:
                        analysis_id = database.save_analysis(
                            letter_text,
                            ai_results['analysis'],
                            scoring_results,
                            recommendations,
                            processing_time
                        )
                        st.success(f"✅ Analysis completed successfully! (ID: {analysis_id})")
                    except Exception as db_error:
                        st.warning(f"Analysis complete but couldn't save to database: {str(db_error)}")
                        st.success("✅ Analysis completed successfully!")
                    
                    # Display enhanced results
                    display_analysis_results(ai_results, scoring_results, recommendations, processing_time)
                    
                except Exception as e:
                    st.error(f"**Analysis Error:** {str(e)}")
                    st.markdown("Please check your configuration and try again.")
    
    with tab2:
        # Analytics Dashboard
        try:
            database = create_database()
            display_analytics_dashboard(database)
        except Exception as e:
            st.error(f"Analytics dashboard error: {str(e)}")
            st.markdown("Analytics dashboard is temporarily unavailable. The main analysis features are still functional.")
    
    # Footer (outside tabs)
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Nexus Letter AI Analyzer v2.0 | Enhanced with Professional Scoring<br>
        Powered by OpenAI GPT-4 | Developed for Disability Law Group
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()