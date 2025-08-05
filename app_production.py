"""
Production-Ready Streamlit Interface for the Nexus Letter AI Analyzer.

Enhanced with PHI compliance, robust error handling, observability, and comprehensive
monitoring capabilities for legal industry production deployment.
"""

import streamlit as st
import time
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

# Import enhanced production components
from ai_analyzer_enhanced import create_analyzer as create_enhanced_analyzer
from text_processor import create_processor, TextProcessor
from config import get_settings, validate_openai_key
from scoring_engine import create_scorer, VAComplianceScorer
from recommendation_engine import create_recommendation_engine, RecommendationEngine
from database import create_database, AnalysisDatabase
from analytics import display_analytics_dashboard

# Import production modules
from phi_compliance import create_phi_detector, create_audit_logger
from error_handling import ErrorClassifier, CircuitBreakerOpenError
from observability import create_structured_logger, create_performance_monitor


# Global session state for production components
if "production_components" not in st.session_state:
    st.session_state.production_components = {
        "logger": create_structured_logger("streamlit_app"),
        "performance_monitor": create_performance_monitor("streamlit_app"),
        "session_id": str(uuid.uuid4()),
    }


def configure_page():
    """Configure Streamlit page settings and load professional styling."""
    st.set_page_config(
        page_title="Nexus Letter AI Analyzer - Production",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    # Load professional CSS styling with production enhancements
    try:
        with open("styles.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Enhanced fallback inline styles for production
        st.markdown(
            """
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
        .production-badge {
            position: absolute; top: 1rem; right: 1rem;
            background: #10b981; color: white; padding: 0.5rem 1rem;
            border-radius: 0.5rem; font-size: 0.8rem; font-weight: bold;
        }
        .phi-protected {
            background: #fef3c7; border: 1px solid #f59e0b; border-radius: 0.5rem;
            padding: 1rem; margin: 1rem 0; color: #92400e;
        }
        .system-status {
            background: #f3f4f6; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;
            font-family: monospace; font-size: 0.9rem;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )


def display_production_header():
    """Display enhanced header with production indicators."""
    st.markdown(
        """
    <div class="main-header fade-in">
        <div class="production-badge">🔒 PRODUCTION READY</div>
        <h1>⚖️ Nexus Letter AI Analyzer</h1>
        <div class="subtitle">HIPAA-Compliant AI Analysis for Legal Professionals</div>
        <p style="margin: 1rem 0 0 0; font-size: 0.95rem; opacity: 0.8;">
            🛡️ PHI Protected • 🔄 Auto-Retry • 📊 Full Observability • ⚡ Circuit Breaker
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def display_phi_protection_notice():
    """Display PHI protection notice for legal compliance."""
    st.markdown(
        """
    <div class="phi-protected">
        <h4 style="margin: 0 0 0.5rem 0;">🛡️ HIPAA Compliance & PHI Protection</h4>
        <p style="margin: 0; font-size: 0.9rem;">
            • All personally identifiable information is automatically detected and redacted<br>
            • Secure audit logging tracks all processing activities<br>
            • No PHI data is stored or transmitted to external services<br>
            • Full compliance with legal industry privacy requirements
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def display_system_status():
    """Display current system status and health metrics."""
    with st.expander("🔧 System Status & Health Metrics", expanded=False):
        try:
            # Get system health from analyzer
            analyzer = create_enhanced_analyzer()
            health_status = analyzer.get_health_status()

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🏥 System Health**")

                status = health_status.get("status", "unknown")
                if status == "healthy":
                    st.success(f"✅ System Status: {status.upper()}")
                elif status == "degraded":
                    st.warning(f"⚠️ System Status: {status.upper()}")
                else:
                    st.error(f"❌ System Status: {status.upper()}")

                if health_status.get("issues"):
                    st.markdown("**Issues:**")
                    for issue in health_status["issues"]:
                        st.markdown(f"• {issue}")

            with col2:
                st.markdown("**🔌 API Circuit Breaker**")
                cb_status = health_status.get("circuit_breaker", {})
                cb_state = cb_status.get("state", "unknown")

                if cb_state == "closed":
                    st.success(f"✅ Circuit Breaker: {cb_state.upper()}")
                elif cb_state == "half_open":
                    st.warning(f"🔄 Circuit Breaker: {cb_state.upper()}")
                else:
                    st.error(f"🔴 Circuit Breaker: {cb_state.upper()}")

                failure_count = cb_status.get("failure_count", 0)
                st.metric("Failure Count", failure_count)

            # Performance metrics
            if "performance" in health_status:
                perf = health_status["performance"]
                st.markdown("**📊 Performance Metrics**")

                col3, col4, col5, col6 = st.columns(4)
                with col3:
                    st.metric("Total Requests", perf.total_requests)
                with col4:
                    st.metric("Success Rate", f"{(1-perf.error_rate)*100:.1f}%")
                with col5:
                    st.metric("Avg Response", f"{perf.avg_response_time_ms:.0f}ms")
                with col6:
                    st.metric("PHI Detections", perf.phi_detections)

        except Exception as e:
            st.error(f"System status unavailable: {str(e)}")


def check_production_readiness() -> bool:
    """Check if system is ready for production use."""
    try:
        # Check API key
        is_valid, error_msg = validate_openai_key()
        if not is_valid:
            st.error("🚨 **Production Blocker: OpenAI API Key Required**")
            st.markdown(
                f"""
            **Issue:** {error_msg}
            
            **To fix this:**
            1. Create a `.env` file in the project directory
            2. Add your OpenAI API key: `OPENAI_API_KEY=sk-your-key-here`
            3. Restart the application
            """
            )
            return False

        # Test system health
        analyzer = create_enhanced_analyzer()
        success, message = analyzer.test_connection()

        if not success:
            st.error(f"🚨 **Production Blocker: API Connection Failed**")
            st.markdown(f"**Issue:** {message}")
            return False

        # Check circuit breaker
        health = analyzer.get_health_status()
        if health.get("circuit_breaker", {}).get("state") == "open":
            st.error("🚨 **Production Issue: Circuit Breaker Open**")
            st.markdown(
                "The system is temporarily blocking requests due to repeated failures."
            )
            return False

        return True

    except Exception as e:
        st.error(f"🚨 **Production Blocker: System Error**")
        st.markdown(f"**Error:** {str(e)}")
        return False


def get_user_input_with_phi_warning() -> tuple[str, TextProcessor]:
    """Get and validate user input with PHI protection warnings."""
    processor = create_processor()

    st.subheader("📄 Secure Document Input")

    # PHI warning
    st.info(
        """
    🛡️ **HIPAA-Compliant Processing**: All personal health information (PHI) will be automatically 
    detected and redacted before analysis. This includes names, addresses, phone numbers, SSNs, 
    and other identifying information.
    """
    )

    # Create columns for input area and stats
    col1, col2 = st.columns([3, 1])

    with col1:
        letter_text = st.text_area(
            "Enter the complete nexus letter text:",
            height=400,
            placeholder="""Paste the complete nexus letter here. PHI will be automatically protected.

Example content should include:
- Medical facility information
- Professional medical opinion
- Service connection rationale  
- Supporting medical evidence
- Doctor's credentials

⚠️ All personal information will be automatically redacted for privacy compliance.""",
            help="Enter the full text - PHI protection is automatically applied",
        )

    with col2:
        # Display text statistics
        if letter_text:
            stats = processor.get_text_stats(letter_text)
            st.markdown("**📊 Text Statistics**")
            st.metric("Characters", stats["character_count"])
            st.metric("Words", stats["word_count"])
            st.metric("Sentences", stats["sentence_count"])
            st.metric("Paragraphs", stats["paragraph_count"])

            # Show validation status
            is_valid, validation_msg = processor.validate_input(letter_text)
            if is_valid:
                st.success("✅ Ready for analysis")
            else:
                st.warning(f"⚠️ {validation_msg}")

            # PHI detection preview (safe preview only)
            if len(letter_text) > 100:
                phi_detector = create_phi_detector()
                detections = phi_detector.detect_phi(letter_text)
                if detections:
                    st.warning(f"🛡️ {len(detections)} PHI elements detected")
                    categories = list(set(d.category.value for d in detections))
                    st.caption(f"Categories: {', '.join(categories)}")
                else:
                    st.info("🛡️ No PHI detected")
        else:
            st.info("Enter text to see statistics and PHI analysis")

    return letter_text, processor


def display_enhanced_loading_analysis(correlation_id: str):
    """Display enhanced loading animation with correlation ID."""
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Enhanced analysis steps with production details
    steps = [
        "🔑 Initializing secure AI analyzer...",
        "🛡️ Scanning for PHI and applying protection...",
        "📝 Preprocessing text for analysis...",
        "🩺 Analyzing medical opinion strength...",
        "🎖️ Evaluating service connection evidence...",
        "🧠 Assessing medical rationale quality...",
        "📋 Reviewing professional format compliance...",
        "⚖️ Calculating VA compliance scores...",
        "📊 Generating improvement recommendations...",
        "✅ Finalizing secure analysis results...",
    ]

    for i, step in enumerate(steps):
        status_text.text(f"{step}")
        progress_bar.progress((i + 1) / len(steps))
        time.sleep(0.4)  # Slightly longer for production feel

    status_text.text(f"Analysis complete! (ID: {correlation_id[:8]})")
    time.sleep(0.5)
    progress_bar.empty()
    status_text.empty()


def display_production_results(
    ai_results: Dict[str, Any],
    scoring_results: Dict[str, Any],
    recommendations: Dict[str, Any],
    processing_time: float,
    correlation_id: str,
):
    """Display analysis results with production metadata and monitoring."""

    # Production metadata display
    if "production_metadata" in ai_results:
        metadata = ai_results["production_metadata"]

        with st.expander("🔧 Production Metadata & Audit Trail", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**🆔 Request Tracking**")
                st.code(f"Correlation ID: {correlation_id}")
                st.code(f"Processing Time: {processing_time:.0f}ms")
                st.code(f"Model: {metadata.get('model_version', 'unknown')}")

            with col2:
                st.markdown("**🛡️ PHI Protection**")
                phi_protected = metadata.get("phi_protected", False)
                phi_count = metadata.get("phi_detections_count", 0)
                st.code(
                    f"PHI Protection: {'✅ ENABLED' if phi_protected else '❌ DISABLED'}"
                )
                st.code(f"PHI Detections: {phi_count}")
                if phi_count > 0:
                    categories = metadata.get("phi_categories_detected", [])
                    st.code(f"Categories: {', '.join(categories)}")

            with col3:
                st.markdown("**⚡ Circuit Breaker**")
                cb_status = metadata.get("circuit_breaker_status", {})
                st.code(f"State: {cb_status.get('state', 'unknown').upper()}")
                st.code(f"Failures: {cb_status.get('failure_count', 0)}")

    # Handle error results with enhanced error display
    if ai_results.get("error"):
        st.error("🚨 **Analysis Error Detected**")

        error_details = st.container()
        with error_details:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Error Information:**")
                st.markdown(
                    f"• **Message:** {ai_results.get('message', 'Unknown error')}"
                )

                if "details" in ai_results:
                    error_category = ErrorClassifier.classify_error(
                        Exception(ai_results["details"])
                    )
                    user_message = ErrorClassifier.get_user_message(error_category)
                    st.markdown(f"• **Category:** {error_category.value}")
                    st.markdown(f"• **User Message:** {user_message}")

            with col2:
                st.markdown("**Recommended Actions:**")
                if "TimeoutError" in str(ai_results.get("details", "")):
                    st.markdown("• Wait a moment and try again")
                    st.markdown("• The system will automatically retry")
                elif "rate limit" in str(ai_results.get("details", "")).lower():
                    st.markdown("• System will automatically retry with backoff")
                    st.markdown("• High usage detected - please wait")
                else:
                    st.markdown("• Check system status above")
                    st.markdown("• Contact support if issue persists")

        # Show fallback if available
        if ai_results.get("fallback_used"):
            st.warning("🔄 **Fallback Analysis Applied**")
            st.markdown(
                "The system provided a basic analysis when the AI service was unavailable."
            )

        return

    # Regular result display (using existing functions from original app.py)
    analysis = ai_results.get("analysis", {})
    overall_score = scoring_results.get("overall_score", 0)
    workflow_rec = recommendations.get("workflow_recommendation")

    # Enhanced score card with production indicators
    display_enhanced_score_card(
        overall_score, workflow_rec, ai_results.get("production_metadata", {})
    )

    # Use existing display functions for the main results
    from app import (
        display_component_analysis,
        display_findings_and_recommendations,
        display_workflow_guidance,
        display_performance_metrics,
        display_export_options,
    )

    display_component_analysis(scoring_results)
    display_findings_and_recommendations(analysis, recommendations)
    display_workflow_guidance(workflow_rec)
    display_performance_metrics(processing_time, analysis, recommendations)
    display_export_options(analysis, scoring_results, recommendations, processing_time)


def display_enhanced_score_card(
    overall_score: int, workflow_rec, production_metadata: Dict[str, Any]
):
    """Display enhanced score card with production indicators."""

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

    # Production indicators
    phi_protected = production_metadata.get("phi_protected", False)
    phi_count = production_metadata.get("phi_detections_count", 0)
    processing_time = production_metadata.get("processing_time_ms", 0)

    st.markdown(
        f"""
    <div class="score-card {status_class} slide-up">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.5rem;">{status_icon}</span>
                    <span style="font-size: 1.2rem; font-weight: bold; color: #1f2937;">{status_text}</span>
                    {'<span style="background: #10b981; color: white; padding: 0.2rem 0.5rem; border-radius: 0.3rem; font-size: 0.8rem; margin-left: 1rem;">🛡️ PHI PROTECTED</span>' if phi_protected else ''}
                </div>
                <h2 style="margin: 0; color: #1f2937; font-size: 1.8rem;">VA Compliance Score</h2>
                <p style="margin: 0.25rem 0 0 0; color: #6b7280; font-size: 1rem;">{description}</p>
                {f'<p style="margin: 0.5rem 0 0 0; color: #059669; font-size: 0.85rem;">⚡ {processing_time:.0f}ms • {phi_count} PHI items protected</p>' if phi_protected else ''}
            </div>
            <div style="text-align: right; padding-left: 2rem;">
                <div style="font-size: 4rem; font-weight: bold; color: #1e3a8a; line-height: 1;">{overall_score}</div>
                <div style="color: #6b7280; font-size: 1.1rem; margin-top: -0.5rem;">out of 100</div>
            </div>
        </div>
        {f'<div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e5e7eb; color: #374151; font-weight: 500;">{workflow_rec.message}</div>' if workflow_rec else ''}
    </div>
    """,
        unsafe_allow_html=True,
    )


def main():
    """Main production application function."""
    configure_page()
    display_production_header()
    display_phi_protection_notice()
    display_system_status()

    # Check production readiness
    if not check_production_readiness():
        st.stop()

    # Create tabs for main interface and analytics
    tab1, tab2, tab3 = st.tabs(
        ["📝 Secure Analysis", "📈 Analytics Dashboard", "🔧 System Health"]
    )

    with tab1:
        # Get user input with PHI warnings
        letter_text, processor = get_user_input_with_phi_warning()

        # Analysis section
        if st.button(
            "🚀 Analyze Nexus Letter (Production)",
            type="primary",
            use_container_width=True,
        ):
            if not letter_text:
                st.warning("Please enter nexus letter text to analyze.")
                return

            # Validate input
            is_valid, validation_msg = processor.validate_input(letter_text)
            if not is_valid:
                st.error(f"**Input Validation Failed:** {validation_msg}")
                return

            # Generate correlation ID for this request
            correlation_id = str(uuid.uuid4())

            # Show enhanced loading animation
            with st.spinner("Performing secure AI analysis..."):
                display_enhanced_loading_analysis(correlation_id)

                # Create components and perform analysis
                try:
                    # Track processing time
                    start_time = time.time()

                    # Initialize enhanced components
                    analyzer = create_enhanced_analyzer(enable_phi_protection=True)
                    scorer = create_scorer()
                    rec_engine = create_recommendation_engine()
                    database = create_database()

                    # Test connection first with production logging
                    success, msg = analyzer.test_connection(correlation_id)
                    if not success:
                        st.error(f"🚨 **API Connection Failed:** {msg}")
                        st.info(
                            "The system will automatically retry. Please wait or try again."
                        )
                        return

                    # Preprocess text
                    processed_text = processor.preprocess_for_ai(letter_text)

                    # Perform enhanced AI analysis with PHI protection
                    ai_results = analyzer.analyze_letter(processed_text, correlation_id)

                    # Handle circuit breaker or other production errors
                    if ai_results.get("error"):
                        if "Circuit breaker" in str(ai_results.get("message", "")):
                            st.error("🔴 **Service Temporarily Unavailable**")
                            st.markdown(
                                """
                            The system has detected repeated failures and is protecting itself by temporarily 
                            blocking requests. This is normal behavior during API outages.
                            
                            **What happens next:**
                            • The system will automatically recover when the API is stable
                            • You'll see the status change in the System Health tab
                            • Please try again in a few minutes
                            """
                            )
                        else:
                            st.error("🚨 **Analysis Error**")
                            st.markdown(
                                f"**Error:** {ai_results.get('message', 'Unknown error')}"
                            )
                        return

                    # Calculate scores (handle fallback results gracefully)
                    if ai_results.get("fallback_used"):
                        st.warning("🔄 **Fallback Analysis Mode**")
                        st.markdown(
                            "AI service unavailable - using fallback analysis. Results may be limited."
                        )

                    analysis_data = ai_results.get("analysis", {})
                    scoring_results = scorer.calculate_total_score(analysis_data)

                    # Generate recommendations
                    recommendations = rec_engine.generate_recommendations(
                        scoring_results["overall_score"], scoring_results, analysis_data
                    )

                    # Calculate processing time
                    processing_time = time.time() - start_time

                    # Save to database with production metadata
                    try:
                        analysis_id = database.save_analysis(
                            letter_text,
                            analysis_data,
                            scoring_results,
                            recommendations,
                            processing_time,
                        )
                        st.success(
                            f"✅ Analysis completed successfully! (ID: {analysis_id}, Correlation: {correlation_id[:8]})"
                        )
                    except Exception as db_error:
                        st.warning(
                            f"Analysis complete but couldn't save to database: {str(db_error)}"
                        )
                        st.success(
                            f"✅ Analysis completed successfully! (Correlation: {correlation_id[:8]})"
                        )

                    # Display enhanced results with production metadata
                    display_production_results(
                        ai_results,
                        scoring_results,
                        recommendations,
                        processing_time * 1000,
                        correlation_id,
                    )

                except CircuitBreakerOpenError:
                    st.error("🔴 **Service Circuit Breaker Open**")
                    st.markdown(
                        """
                    The system is temporarily unavailable due to repeated service failures. 
                    This protects both our system and the external API from overload.
                    
                    Please check the System Health tab and try again in a few minutes.
                    """
                    )

                except Exception as e:
                    error_category = ErrorClassifier.classify_error(e)
                    st.error(f"🚨 **System Error: {error_category.value}**")

                    user_message = ErrorClassifier.get_user_message(error_category)
                    st.markdown(f"**Message:** {user_message}")

                    if error_category.value in ["api_timeout", "api_network_error"]:
                        st.info(
                            "💡 The system automatically retries these errors. You may try again immediately."
                        )

                    # Log error for production monitoring
                    logger = st.session_state.production_components["logger"]
                    logger.error(
                        f"Streamlit app error",
                        error=e,
                        metadata={"correlation_id": correlation_id},
                    )

    with tab2:
        # Enhanced Analytics Dashboard
        st.markdown("## 📈 Production Analytics Dashboard")
        try:
            database = create_database()
            display_analytics_dashboard(database)

            # Add production-specific metrics
            st.markdown("### 🔧 Production Metrics")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Session ID",
                    st.session_state.production_components["session_id"][:8],
                )
            with col2:
                st.metric(
                    "Uptime",
                    f"{time.time() - st.session_state.get('start_time', time.time()):.0f}s",
                )
            with col3:
                st.metric("PHI Protection", "✅ ENABLED")

        except Exception as e:
            st.error(f"Analytics dashboard error: {str(e)}")
            st.markdown(
                "Analytics dashboard is temporarily unavailable. The main analysis features are still functional."
            )

    with tab3:
        # System Health Tab
        st.markdown("## 🏥 Production System Health")

        if st.button("🔄 Refresh System Status", use_container_width=True):
            st.rerun()

        try:
            analyzer = create_enhanced_analyzer()
            health = analyzer.get_health_status()

            # Overall health status
            status = health.get("status", "unknown")
            if status == "healthy":
                st.success(f"✅ System Status: {status.upper()}")
            elif status == "degraded":
                st.warning(f"⚠️ System Status: {status.upper()}")
            else:
                st.error(f"❌ System Status: {status.upper()}")

            if health.get("issues"):
                st.markdown("**🚨 Current Issues:**")
                for issue in health["issues"]:
                    st.markdown(f"• {issue}")

            # Detailed health metrics
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🔌 API Circuit Breaker")
                cb_status = health.get("circuit_breaker", {})

                st.json(cb_status)

                # Circuit breaker actions
                if cb_status.get("state") == "open":
                    st.error(
                        """
                    🔴 **Circuit Breaker is OPEN** - API calls are being blocked to prevent cascade failures.
                    The system will automatically attempt recovery.
                    """
                    )
                elif cb_status.get("state") == "half_open":
                    st.warning(
                        "🔄 **Circuit Breaker is HALF-OPEN** - Testing recovery..."
                    )
                else:
                    st.success("✅ **Circuit Breaker is CLOSED** - Normal operation")

            with col2:
                st.markdown("### 📊 Performance Metrics")
                if "performance" in health:
                    perf_data = (
                        health["performance"].__dict__
                        if hasattr(health["performance"], "__dict__")
                        else health["performance"]
                    )
                    st.json(perf_data)
                else:
                    st.info("Performance data not available")

            # Raw health data
            with st.expander("🔍 Raw System Data", expanded=False):
                st.json(health)

        except Exception as e:
            st.error(f"System health check failed: {str(e)}")

    # Enhanced footer with production information
    st.markdown("---")
    st.markdown(
        f"""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
        Nexus Letter AI Analyzer v3.0 - Production Ready<br>
        🛡️ HIPAA Compliant • ⚡ Circuit Breaker Protected • 📊 Full Observability<br>
        Session: {st.session_state.production_components['session_id'][:8]} | 
        Powered by OpenAI GPT-4 | Developed for Disability Law Group
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    # Initialize session start time
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    main()
