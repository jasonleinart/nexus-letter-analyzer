"""Minimal test version of the Streamlit app to diagnose issues."""

import streamlit as st
import time
from typing import Dict, Any

# Basic imports only
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
    st.title("⚖️ Nexus Letter AI Analyzer - Milestone 2")
    st.markdown("""
    **Professional AI-powered analysis of VA disability nexus letters**
    
    This tool now includes enhanced scoring, recommendations, and analytics.
    """)
    st.divider()

def check_api_key_setup() -> bool:
    """Check if OpenAI API key is properly configured."""
    is_valid, error_msg = validate_openai_key()
    
    if not is_valid:
        st.error("⚠️ **OpenAI API Key Required**")
        st.markdown(f"""
        **Issue:** {error_msg}
        
        **To fix this:**
        1. Create a `.env` file in the project directory
        2. Add your OpenAI API key: `OPENAI_API_KEY=sk-your-key-here`
        3. Restart the application
        """)
        return False
    
    return True

def test_enhanced_components():
    """Test if enhanced components can be imported."""
    try:
        from ai_analyzer import create_analyzer
        from scoring_engine import create_scorer
        from recommendation_engine import create_recommendation_engine
        from database import create_database
        
        st.success("✅ All enhanced components imported successfully!")
        
        # Test component creation
        processor = create_processor()
        analyzer = create_analyzer()
        scorer = create_scorer()
        rec_engine = create_recommendation_engine()
        database = create_database("test.db")
        
        st.success("✅ All components created successfully!")
        return True
        
    except Exception as e:
        st.error(f"❌ Component import/creation failed: {str(e)}")
        return False

def main():
    """Main application function."""
    configure_page()
    display_header()
    
    # Check API key configuration first
    if not check_api_key_setup():
        st.stop()
    
    # Test enhanced components
    st.subheader("🔧 Component Status Check")
    components_ok = test_enhanced_components()
    
    if components_ok:
        st.subheader("🎉 Milestone 2 Features Available")
        st.markdown("""
        **New capabilities now available:**
        - ✅ Enhanced AI Analysis with component scoring
        - ✅ VA Compliance Scoring Engine (0-100 points)
        - ✅ Professional Recommendations Engine
        - ✅ Database Integration for analysis tracking
        - ✅ Analytics Dashboard with ROI metrics
        """)
        
        # Simple test input
        st.subheader("📝 Quick Test")
        test_input = st.text_area("Enter a short test to verify functionality:", 
                                 placeholder="Type anything here to test...")
        
        if st.button("Test Enhanced Analysis"):
            if test_input:
                with st.spinner("Testing enhanced pipeline..."):
                    try:
                        from ai_analyzer import create_analyzer
                        from scoring_engine import create_scorer
                        from recommendation_engine import create_recommendation_engine
                        
                        # Create mock analysis for testing UI
                        mock_analysis = {
                            'medical_opinion': {'score': 20, 'confidence': 85, 'findings': ['Test finding'], 'issues': [], 'rationale': 'Test rationale'},
                            'service_connection': {'score': 18, 'confidence': 80, 'findings': ['Connection found'], 'issues': [], 'rationale': 'Good connection'},
                            'medical_rationale': {'score': 15, 'confidence': 75, 'findings': ['Some rationale'], 'issues': ['Could be stronger'], 'rationale': 'Moderate rationale'},
                            'professional_format': {'score': 22, 'confidence': 90, 'findings': ['Professional'], 'issues': [], 'rationale': 'Well formatted'},
                            'overall_score': 75,
                            'nexus_strength': 'Moderate',
                            'primary_condition': 'Test Condition'
                        }
                        
                        scorer = create_scorer()
                        scoring_results = scorer.calculate_total_score(mock_analysis)
                        
                        st.success(f"✅ Enhanced analysis complete! Score: {scoring_results['overall_score']}/100")
                        st.json({"status": "success", "score": scoring_results['overall_score']})
                        
                    except Exception as e:
                        st.error(f"❌ Enhanced analysis failed: {str(e)}")
            else:
                st.warning("Please enter some test text")
    else:
        st.error("❌ Enhanced components not available. Check error messages above.")
    
    # Footer
    st.markdown("---")
    st.markdown("**Status**: Testing Milestone 2 Enhanced Features")

if __name__ == "__main__":
    main()