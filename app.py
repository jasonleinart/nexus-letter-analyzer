"""Streamlit web interface for the Nexus Letter AI Analyzer."""

import streamlit as st
import time
from typing import Dict, Any
from ai_analyzer import create_analyzer, NexusLetterAnalyzer
from text_processor import create_processor, TextProcessor
from config import get_settings, validate_openai_key


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


def display_analysis_results(results: Dict[str, Any]):
    """
    Display the analysis results in a professional format.
    
    Args:
        results: Analysis results from AI analyzer
    """
    if results.get('error'):
        st.error(f"**Analysis Error:** {results.get('message', 'Unknown error')}")
        if results.get('details'):
            st.code(results['details'])
        return
    
    analysis = results.get('analysis', {})
    
    # Main analysis summary
    st.subheader("📊 Analysis Summary")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        strength = analysis.get('nexus_strength', 'Unknown')
        color = {
            'Strong': 'green',
            'Moderate': 'orange', 
            'Weak': 'red',
            'None': 'red'
        }.get(strength, 'gray')
        st.markdown(f"**Nexus Strength**")
        st.markdown(f"<span style='color: {color}; font-size: 1.2em; font-weight: bold'>{strength}</span>", 
                   unsafe_allow_html=True)
    
    with col2:
        probability = analysis.get('probability_rating', 'Not stated')
        st.markdown(f"**Probability Rating**")
        st.markdown(f"**{probability}**")
    
    with col3:
        medical_opinion = analysis.get('medical_opinion_present', False)
        icon = "✅" if medical_opinion else "❌"
        st.markdown(f"**Medical Opinion**")
        st.markdown(f"{icon} {'Present' if medical_opinion else 'Missing'}")
    
    with col4:
        service_connection = analysis.get('service_connection_stated', False)
        icon = "✅" if service_connection else "❌"
        st.markdown(f"**Service Connection**")
        st.markdown(f"{icon} {'Stated' if service_connection else 'Missing'}")
    
    st.divider()
    
    # Detailed analysis sections
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Letter Components")
        
        # Primary conditions
        if analysis.get('primary_condition'):
            st.markdown(f"**Primary Condition:** {analysis['primary_condition']}")
        
        if analysis.get('service_connected_condition'):
            st.markdown(f"**Service-Connected Condition:** {analysis['service_connected_condition']}")
        
        if analysis.get('connection_theory'):
            st.markdown(f"**Connection Theory:** {analysis['connection_theory'].title()}")
        
        # Medical rationale indicator
        rationale = analysis.get('medical_rationale_provided', False)
        st.markdown(f"**Medical Rationale:** {'✅ Provided' if rationale else '❌ Missing'}")
        
        # Strengths
        st.subheader("💪 Strengths")
        strengths = analysis.get('strengths', [])
        if strengths:
            for strength in strengths:
                st.markdown(f"• {strength}")
        else:
            st.markdown("*No specific strengths identified*")
    
    with col2:
        # Weaknesses
        st.subheader("⚠️ Areas for Improvement")
        weaknesses = analysis.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                st.markdown(f"• {weakness}")
        else:
            st.markdown("*No major weaknesses identified*")
        
        # Recommendations
        st.subheader("📋 Recommendations")
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                st.markdown(f"• {rec}")
        else:
            st.markdown("*No specific recommendations*")
    
    # Summary section
    st.subheader("📝 Overall Assessment")
    summary = analysis.get('summary', 'No summary available')
    st.markdown(summary)
    
    # Export options
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📋 Copy to Clipboard", help="Copy analysis results to clipboard"):
            # Create formatted text for copying
            export_text = format_results_for_export(analysis)
            st.code(export_text, language=None)
    
    with col2:
        st.markdown("*Analysis results formatted for professional use*")


def format_results_for_export(analysis: Dict[str, Any]) -> str:
    """
    Format analysis results for export/copying.
    
    Args:
        analysis: Analysis results dictionary
        
    Returns:
        Formatted text string
    """
    lines = [
        "NEXUS LETTER ANALYSIS REPORT",
        "=" * 40,
        "",
        f"Nexus Strength: {analysis.get('nexus_strength', 'Unknown')}",
        f"Probability Rating: {analysis.get('probability_rating', 'Not stated')}",
        f"Medical Opinion Present: {'Yes' if analysis.get('medical_opinion_present') else 'No'}",
        f"Service Connection Stated: {'Yes' if analysis.get('service_connection_stated') else 'No'}",
        "",
        "COMPONENTS:",
        f"Primary Condition: {analysis.get('primary_condition', 'Not specified')}",
        f"Service-Connected Condition: {analysis.get('service_connected_condition', 'Not specified')}",
        f"Connection Theory: {analysis.get('connection_theory', 'Not specified')}",
        "",
        "STRENGTHS:",
    ]
    
    for strength in analysis.get('strengths', []):
        lines.append(f"• {strength}")
    
    lines.extend([
        "",
        "AREAS FOR IMPROVEMENT:",
    ])
    
    for weakness in analysis.get('weaknesses', []):
        lines.append(f"• {weakness}")
    
    lines.extend([
        "",
        "RECOMMENDATIONS:",
    ])
    
    for rec in analysis.get('recommendations', []):
        lines.append(f"• {rec}")
    
    lines.extend([
        "",
        "SUMMARY:",
        analysis.get('summary', 'No summary available'),
        "",
        f"Analysis generated by Nexus Letter AI Analyzer",
        f"Powered by OpenAI GPT-4"
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
            
            # Create analyzer and perform analysis
            try:
                analyzer = create_analyzer()
                
                # Test connection first
                success, msg = analyzer.test_connection()
                if not success:
                    st.error(f"**API Connection Failed:** {msg}")
                    return
                
                # Preprocess text
                processed_text = processor.preprocess_for_ai(letter_text)
                
                # Perform analysis
                results = analyzer.analyze_letter(processed_text)
                
                # Display results
                st.success("Analysis completed successfully!")
                display_analysis_results(results)
                
            except Exception as e:
                st.error(f"**Analysis Error:** {str(e)}")
                st.markdown("Please check your API key and try again.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Nexus Letter AI Analyzer v1.0 | Powered by OpenAI GPT-4<br>
        Developed for Disability Law Group - AI Systems & Technology Integration
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()