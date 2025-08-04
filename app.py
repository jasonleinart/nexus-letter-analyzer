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
    """Configure Streamlit page settings and load professional styling."""
    st.set_page_config(
        page_title="Nexus Letter AI Analyzer",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load professional CSS styling
    try:
        with open('styles.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback inline styles if CSS file not found
        st.markdown("""
        <style>
        .main .block-container { padding-top: 2rem; max-width: 1200px; }
        .main-header { 
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white; padding: 2rem; margin: -1rem -1rem 2rem -1rem;
            border-radius: 0 0 0.75rem 0.75rem; text-align: center;
        }
        .score-card { 
            background: white; border-radius: 0.75rem; padding: 2rem; margin: 1.5rem 0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); border-left: 6px solid #3b82f6;
        }
        </style>
        """, unsafe_allow_html=True)


def display_header():
    """Display the professional application header."""
    st.markdown("""
    <div class="main-header fade-in">
        <h1>⚖️ Nexus Letter AI Analyzer</h1>
        <div class="subtitle">Professional AI-powered analysis of VA disability nexus letters</div>
        <p style="margin: 1rem 0 0 0; font-size: 0.95rem; opacity: 0.8;">
            Advanced GPT-4 analysis for legal strength, medical opinion quality, and VA compliance
        </p>
    </div>
    """, unsafe_allow_html=True)


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
    Display the professional analysis results with enhanced visual presentation.
    
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
    
    # Professional overall score card
    display_professional_score_card(overall_score, workflow_rec)
    
    # Component analysis with visual progress bars
    display_component_analysis(scoring_results)
    
    # Key findings and recommendations in professional cards
    display_findings_and_recommendations(analysis, recommendations)
    
    # Workflow guidance section
    display_workflow_guidance(workflow_rec)
    
    # Performance metrics dashboard
    display_performance_metrics(processing_time, analysis, recommendations)
    
    # Professional export section
    display_export_options(analysis, scoring_results, recommendations, processing_time)


def display_professional_score_card(overall_score: int, workflow_rec):
    """Display the main score card with professional styling."""
    
    # Determine score category and styling
    if overall_score >= 85:
        status_class = "score-excellent"
        status_text = "EXCELLENT"
        status_icon = "🏆"
        description = "Letter Exceeds VA Standards"
    elif overall_score >= 70:
        status_class = "score-good"
        status_text = "GOOD"
        status_icon = "📋"
        description = "Attorney Review Recommended"
    else:
        status_class = "score-poor"
        status_text = "NEEDS IMPROVEMENT"
        status_icon = "⚠️"
        description = "Revision Required"
    
    st.markdown(f"""
    <div class="score-card {status_class} slide-up">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem;">{status_icon}</span>
                    <span style="font-size: 1.2rem; font-weight: bold; color: #1f2937;">{status_text}</span>
                </div>
                <h2 style="margin: 0; color: #1f2937; font-size: 1.8rem;">VA Compliance Score</h2>
                <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 1rem;">{description}</p>
            </div>
            <div style="text-align: right; padding-left: 2rem;">
                <div style="font-size: 4rem; font-weight: bold; color: #1e3a8a; line-height: 1;">{overall_score}</div>
                <div style="color: #6b7280; font-size: 1.1rem; margin-top: -0.5rem;">out of 100</div>
            </div>
        </div>
        {f'<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; color: #374151; font-weight: 500;">{workflow_rec.message}</div>' if workflow_rec else ''}
    </div>
    """, unsafe_allow_html=True)


def display_component_analysis(scoring_results: Dict[str, Any]):
    """Display component analysis with professional progress bars."""
    
    st.markdown("## 📊 Component Analysis")
    st.markdown("*Detailed breakdown of nexus letter evaluation criteria*")
    
    components = [
        ("Medical Opinion", scoring_results.get('medical_opinion_breakdown'), "🩺"),
        ("Service Connection", scoring_results.get('service_connection_breakdown'), "🎖️"),
        ("Medical Rationale", scoring_results.get('medical_rationale_breakdown'), "🧠"),
        ("Professional Format", scoring_results.get('professional_format_breakdown'), "📝")
    ]
    
    # Create two-column layout for components
    col1, col2 = st.columns(2)
    
    for i, (name, breakdown, icon) in enumerate(components):
        col = col1 if i % 2 == 0 else col2
        
        with col:
            if breakdown and hasattr(breakdown, 'score'):
                score = breakdown.score
                max_score = breakdown.max_score
                progress = score / max_score if max_score > 0 else 0
                
                # Determine progress bar color
                if progress >= 0.8:
                    progress_class = "progress-excellent"
                elif progress >= 0.6:
                    progress_class = "progress-good"
                else:
                    progress_class = "progress-poor"
                
                st.markdown(f"""
                <div class="component-card fade-in">
                    <div class="component-header">
                        <div class="component-title">
                            <span style="font-size: 1.2rem;">{icon}</span>
                            {name}
                        </div>
                        <div class="component-score">{score}/{max_score}</div>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar {progress_class}" style="width: {progress * 100}%;"></div>
                    </div>
                    <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                        {int(progress * 100)}% Complete
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show detailed breakdown in expander
                with st.expander(f"View {name} Details"):
                    if hasattr(breakdown, 'criteria') and breakdown.criteria:
                        st.markdown("**Scoring Criteria:**")
                        for criterion, points in breakdown.criteria.items():
                            st.markdown(f"• **{criterion.replace('_', ' ').title()}:** {points} points")
                    if hasattr(breakdown, 'rationale'):
                        st.markdown("**Analysis:**")
                        st.markdown(f"*{breakdown.rationale}*")
            else:
                st.markdown(f"""
                <div class="component-card fade-in">
                    <div class="component-header">
                        <div class="component-title">
                            <span style="font-size: 1.2rem;">{icon}</span>
                            {name}
                        </div>
                        <div class="component-score">0/25</div>
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar progress-poor" style="width: 0%;"></div>
                    </div>
                    <div style="font-size: 0.9rem; color: #6b7280; margin-top: 0.5rem;">
                        0% Complete
                    </div>
                </div>
                """, unsafe_allow_html=True)


def display_findings_and_recommendations(analysis: Dict[str, Any], recommendations: Dict[str, Any]):
    """Display key findings and recommendations in professional cards."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("## 🔍 Key Findings")
        
        # Display key strengths using Streamlit native components
        if 'key_strengths' in analysis and analysis['key_strengths']:
            st.markdown("### ✅ Strengths")
            for strength in analysis['key_strengths'][:3]:
                st.success(f"✓ {strength}")
        
        # Display critical issues
        if 'critical_issues' in analysis and analysis['critical_issues']:
            st.markdown("### ⚠️ Critical Issues")
            for issue in analysis['critical_issues']:
                st.error(f"⚠ {issue}")
        
        # Key details
        if analysis.get('primary_condition') or analysis.get('probability_language'):
            st.markdown("### 📋 Key Details")
            if analysis.get('primary_condition'):
                st.info(f"**Primary Condition:** {analysis['primary_condition']}")
            if analysis.get('probability_language'):
                st.info(f"**Probability Language:** \"{analysis['probability_language']}\"")
    
    with col2:
        st.markdown("## 📋 Priority Improvements")
        
        improvements = recommendations.get('improvement_suggestions', [])
        critical_count = recommendations.get('critical_issues', 0)
        
        if critical_count > 0:
            st.error(f"🔴 **{critical_count} Critical Issues** require immediate attention")
        
        # Show top 5 improvements using native Streamlit components
        if improvements:
            for i, improvement in enumerate(improvements[:5]):
                # Handle both object and dictionary formats
                if hasattr(improvement, 'impact'):
                    # Object format
                    impact = improvement.impact
                    component = improvement.component
                    suggestion = improvement.suggestion
                    example = getattr(improvement, 'example', None)
                else:
                    # Dictionary format fallback
                    impact = improvement.get('impact', 'medium')
                    component = improvement.get('component', 'general')
                    suggestion = improvement.get('suggestion', 'No suggestion available')
                    example = improvement.get('example', None)
                
                # Format component name
                component_name = str(component).replace('_', ' ').title()
                
                # Choose appropriate Streamlit component based on impact
                if impact == 'critical':
                    st.error(f"🔴 **{component_name}**")
                    st.write(f"   {suggestion}")
                elif impact == 'high':
                    st.warning(f"🟡 **{component_name}**")
                    st.write(f"   {suggestion}")
                else:
                    st.info(f"🟢 **{component_name}**")
                    st.write(f"   {suggestion}")
                
                # Add example if available
                if example:
                    st.caption(f"Example: {example}")
        else:
            st.info("No specific improvements identified - letter meets basic standards.")


def display_workflow_guidance(workflow_rec):
    """Display workflow guidance and next steps."""
    
    if workflow_rec and hasattr(workflow_rec, 'next_steps'):
        st.markdown("## 🚀 Recommended Next Steps")
        
        # Use native Streamlit components for better display
        for i, step in enumerate(workflow_rec.next_steps, 1):
            st.info(f"**Step {i}:** {step}")
    elif workflow_rec and hasattr(workflow_rec, 'decision'):
        # If we have workflow recommendation but no next steps, show the decision
        st.markdown("## 🚀 Workflow Decision")
        decision = workflow_rec.decision.replace('_', ' ').title()
        if hasattr(workflow_rec, 'message'):
            st.info(f"**Decision:** {decision} - {workflow_rec.message}")
        else:
            st.info(f"**Decision:** {decision}")


def display_performance_metrics(processing_time: float, analysis: Dict[str, Any], recommendations: Dict[str, Any]):
    """Display performance metrics in professional cards."""
    
    st.markdown("## 📈 Analysis Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="kpi-icon">⚡</div>
            <div class="kpi-value">{processing_time:.1f}s</div>
            <div class="kpi-label">Processing Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        nexus_strength = analysis.get('nexus_strength', 'Unknown')
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="kpi-icon">🔗</div>
            <div class="kpi-value" style="font-size: 1.2rem;">{nexus_strength}</div>
            <div class="kpi-label">Nexus Strength</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_improvements = recommendations.get('total_improvements', 0)
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="kpi-icon">🔧</div>
            <div class="kpi-value">{total_improvements}</div>
            <div class="kpi-label">Improvements</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        confidence = analysis.get('confidence_level', 'High')
        st.markdown(f"""
        <div class="metric-card fade-in">
            <div class="kpi-icon">📊</div>
            <div class="kpi-value" style="font-size: 1.2rem;">{confidence}</div>
            <div class="kpi-label">AI Confidence</div>
        </div>
        """, unsafe_allow_html=True)


def display_export_options(analysis: Dict[str, Any], scoring_results: Dict[str, Any], 
                          recommendations: Dict[str, Any], processing_time: float):
    """Display professional export options."""
    
    st.markdown("## 💾 Export & Documentation")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("📋 Generate Full Report", 
                    help="Generate complete analysis report for documentation", 
                    use_container_width=True):
            export_text = format_enhanced_results_for_export(
                analysis, scoring_results, recommendations, processing_time
            )
            
            st.markdown("### 📄 Complete Analysis Report")
            st.code(export_text, language=None)
            
            # Show download instructions
            st.info("📥 **To save:** Copy the text above and paste into a document, or use your browser's save function.")
    
    with col2:
        st.markdown("""
        <div class="export-section">
            <h4 style="margin-top: 0; color: #1e3a8a;">📊 Report Contents</h4>
            <ul style="margin: 0; color: #374151;">
                <li><strong>Executive Summary</strong> - Overall score and recommendation</li>
                <li><strong>Component Analysis</strong> - Detailed scoring breakdown</li>
                <li><strong>Key Findings</strong> - Strengths and critical issues</li>
                <li><strong>Improvement Plan</strong> - Prioritized recommendations</li>
                <li><strong>Next Steps</strong> - Workflow guidance</li>
                <li><strong>Technical Metrics</strong> - Performance and confidence data</li>
            </ul>
            <p style="margin-bottom: 0; color: #6b7280; font-style: italic;">
                Professional format suitable for client communication and case documentation
            </p>
        </div>
        """, unsafe_allow_html=True)


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