"""
Production-Ready OpenAI GPT-4 integration for nexus letter analysis.

Enhanced with PHI compliance, error handling, observability, and reliability features
for production deployment in legal environments.
"""

import json
import time
import uuid
from typing import Dict, Optional, Any, Tuple
from openai import OpenAI
from pydantic import BaseModel, Field

from config import get_settings, validate_openai_key
from phi_compliance import (
    PHIDetectionEngine,
    SecureAuditLogger,
    phi_compliant_processing,
)
from error_handling import (
    with_error_handling,
    RetryConfig,
    CircuitBreakerConfig,
    CircuitBreaker,
    create_circuit_breaker,
    ErrorClassifier,
)
from observability import (
    observability_context,
    create_structured_logger,
    create_performance_monitor,
    StructuredLogger,
)


class ComponentScore(BaseModel):
    """Score breakdown for a specific component."""

    score: int = Field(..., ge=0, le=25, description="Component score (0-25)")
    confidence: int = Field(
        ..., ge=0, le=100, description="Confidence percentage (0-100)"
    )
    findings: list[str] = Field(
        ..., description="Specific text examples supporting the score"
    )
    issues: list[str] = Field(..., description="Missing or problematic elements")
    rationale: str = Field(..., description="Explanation for the score")


class NexusAnalysis(BaseModel):
    """Enhanced structured response model for nexus letter analysis with component scoring."""

    # Component-based analysis (25 points each)
    medical_opinion: ComponentScore = Field(
        ..., description="Medical opinion component analysis"
    )
    service_connection: ComponentScore = Field(
        ..., description="Service connection component analysis"
    )
    medical_rationale: ComponentScore = Field(
        ..., description="Medical rationale component analysis"
    )
    professional_format: ComponentScore = Field(
        ..., description="Professional format component analysis"
    )

    # Overall Assessment
    overall_score: int = Field(..., ge=0, le=100, description="Total score (0-100)")
    nexus_strength: str = Field(
        ..., description="Overall strength (Strong/Moderate/Weak/None)"
    )

    # Detailed Analysis
    primary_condition: str = Field(..., description="Main condition being evaluated")
    service_connected_condition: str = Field(
        ..., description="Service-connected condition mentioned"
    )
    connection_theory: str = Field(
        ..., description="Theory of connection (direct, secondary, aggravation)"
    )
    probability_language: Optional[str] = Field(
        None, description="Exact probability language used"
    )

    # Summary and Recommendations
    summary: str = Field(
        ..., description="Brief summary of the nexus letter's effectiveness"
    )
    key_strengths: list[str] = Field(..., description="Top 3 strengths of the letter")
    critical_issues: list[str] = Field(
        ..., description="Critical issues that must be addressed"
    )
    improvement_priorities: list[str] = Field(
        ..., description="Prioritized list of improvements"
    )


class ProductionNexusLetterAnalyzer:
    """
    Production-ready AI-powered analyzer for nexus letters.

    Features:
    - PHI detection and de-identification
    - Robust error handling with circuit breaker
    - Structured logging and observability
    - Secure audit trail
    - Graceful degradation
    """

    def __init__(
        self, api_key: Optional[str] = None, enable_phi_protection: bool = True
    ):
        """
        Initialize the production-ready analyzer.

        Args:
            api_key: Optional API key. If None, loads from settings.
            enable_phi_protection: Whether to enable PHI protection (should be True in production)
        """
        # Load settings
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.enable_phi_protection = enable_phi_protection

        # Validate API key
        is_valid, error_msg = validate_openai_key(self.api_key)
        if not is_valid:
            raise ValueError(f"Invalid OpenAI API key: {error_msg}")

        # Initialize components
        self.model = "gpt-4-turbo-preview"
        self._initialize_production_components()

        # Initialize OpenAI client
        try:
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client", error=e)
            raise

    def _initialize_production_components(self):
        """Initialize production components for observability and reliability."""
        # Structured logging
        self.logger = create_structured_logger("ai_analyzer", "ai_analyzer.log")

        # Performance monitoring
        self.performance_monitor = create_performance_monitor(
            "ai_analyzer", "ai_analyzer_metrics.log"
        )

        # PHI protection
        if self.enable_phi_protection:
            self.phi_detector = PHIDetectionEngine(strict_mode=True)
            self.audit_logger = SecureAuditLogger("audit.log")

        # Circuit breaker for API calls
        self.circuit_breaker = create_circuit_breaker("openai_api", failure_threshold=3)

        # Retry configuration
        self.retry_config = RetryConfig(
            max_attempts=3,
            base_delay_seconds=1.0,
            max_delay_seconds=30.0,
            exponential_multiplier=2.0,
            jitter=True,
        )

    def test_connection(self, correlation_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        Test the connection to OpenAI API with full production monitoring.

        Args:
            correlation_id: Optional correlation ID for request tracking

        Returns:
            Tuple of (success, message)
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        with observability_context("connection_test", correlation_id) as (
            logger,
            metrics,
            monitor,
            corr_id,
        ):
            try:
                # Test through circuit breaker
                def _test_api():
                    return self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "user",
                                "content": "Test connection - respond with 'OK'",
                            }
                        ],
                        max_tokens=10,
                        timeout=10.0,
                    )

                response = self.circuit_breaker.call(_test_api)

                logger.info("API connection test successful")
                monitor.record_circuit_breaker_event("openai_api", "success", corr_id)

                return True, "Connection successful"

            except Exception as e:
                error_category = ErrorClassifier.classify_error(e)
                logger.error(
                    f"API connection test failed: {error_category.value}", error=e
                )
                monitor.record_circuit_breaker_event("openai_api", "failure", corr_id)

                return False, f"Connection failed: {str(e)}"

    def analyze_letter(
        self, letter_text: str, correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a nexus letter with full production monitoring and protection.

        Args:
            letter_text: The complete text of the nexus letter
            correlation_id: Optional correlation ID for request tracking

        Returns:
            Dictionary containing structured analysis results with production metadata
        """
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())

        with observability_context("letter_analysis", correlation_id) as (
            logger,
            metrics,
            monitor,
            corr_id,
        ):
            start_time = time.time()

            try:
                # Step 1: PHI Protection
                cleaned_text, phi_detections = self._protect_phi(letter_text, corr_id)

                if phi_detections:
                    logger.warning(
                        f"PHI detected and redacted: {len(phi_detections)} instances"
                    )
                    monitor.record_phi_detection(len(phi_detections), corr_id)

                # Step 2: AI Analysis with error handling
                ai_result = self._perform_ai_analysis(cleaned_text, corr_id)

                # Step 3: Add production metadata
                processing_time = (time.time() - start_time) * 1000
                ai_result = self._enrich_with_production_metadata(
                    ai_result, phi_detections, processing_time, corr_id
                )

                logger.info(
                    "Letter analysis completed successfully",
                    duration_ms=processing_time,
                )
                return ai_result

            except Exception as e:
                processing_time = (time.time() - start_time) * 1000
                error_category = ErrorClassifier.classify_error(e)

                logger.error(
                    f"Letter analysis failed: {error_category.value}",
                    error=e,
                    duration_ms=processing_time,
                )

                # Record failure for circuit breaker
                monitor.record_circuit_breaker_event("openai_api", "failure", corr_id)

                # Return structured error response
                return {
                    "error": True,
                    "message": f"Analysis failed: {error_category.value}",
                    "details": str(e),
                    "correlation_id": corr_id,
                    "processing_time_ms": processing_time,
                    "phi_protected": self.enable_phi_protection,
                }

    def _protect_phi(self, letter_text: str, correlation_id: str) -> Tuple[str, list]:
        """
        Protect PHI in the letter text.

        Args:
            letter_text: Original letter text
            correlation_id: Correlation ID for audit logging

        Returns:
            Tuple of (cleaned_text, phi_detections)
        """
        if not self.enable_phi_protection:
            return letter_text, []

        with phi_compliant_processing(correlation_id) as (
            corr_id,
            phi_detector,
            audit_logger,
        ):
            # Audit the start of processing
            audit_logger.log_analysis_start(corr_id, len(letter_text))

            # Detect and de-identify PHI
            cleaned_text, detections = phi_detector.de_identify_text(
                letter_text, corr_id
            )

            # Audit PHI processing
            categories = list(set(d.category for d in detections))
            audit_logger.log_phi_processing(
                corr_id,
                len(detections) > 0,
                categories,
                0,  # Processing time tracked elsewhere
            )

            return cleaned_text, detections

    @with_error_handling(
        retry_config=RetryConfig(max_attempts=3, base_delay_seconds=1.0),
        enable_fallback=True,
    )
    def _perform_ai_analysis(
        self, letter_text: str, correlation_id: str
    ) -> Dict[str, Any]:
        """
        Perform AI analysis with retry logic and circuit breaker protection.

        Args:
            letter_text: Pre-processed letter text (PHI removed)
            correlation_id: Correlation ID for tracking

        Returns:
            Analysis results from OpenAI API
        """
        start_time = time.time()

        try:
            # Build prompt
            prompt = self._build_prompt(letter_text)

            # Execute through circuit breaker
            def _api_call():
                return self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert legal and medical analyst specializing in VA disability nexus letters. Provide thorough, professional analysis.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=2000,
                    temperature=0.3,
                    timeout=30.0,  # 30 second timeout
                )

            response = self.circuit_breaker.call(_api_call)

            # Record API metrics
            processing_time = (time.time() - start_time) * 1000

            if self.enable_phi_protection:
                self.audit_logger.log_ai_request(
                    correlation_id,
                    self.model,
                    len(prompt.split()),  # Approximate token count
                    len(response.choices[0].message.content.split()),
                    processing_time,
                )

            # Parse response
            response_text = response.choices[0].message.content
            return self._parse_response(response_text, correlation_id)

        except Exception as e:
            # Log error through audit system
            if self.enable_phi_protection:
                error_category = ErrorClassifier.classify_error(e)
                self.audit_logger.log_error(
                    correlation_id, error_category.value, str(e)
                )

            raise  # Re-raise for error handling decorator

    def _build_prompt(self, letter_text: str) -> str:
        """
        Build the enhanced component-based analysis prompt for OpenAI API.

        Args:
            letter_text: Pre-processed nexus letter text (PHI removed)

        Returns:
            Formatted prompt string
        """
        prompt = f"""
As a VA disability claims expert, analyze this nexus letter using the VA's standards for medical evidence. Evaluate each component separately and provide detailed scoring.

NEXUS LETTER TEXT:
{letter_text}

Analyze this nexus letter for VA compliance in these specific areas and provide a JSON response:

1. MEDICAL OPINION (25 points max):
   - Look for probability language ("at least as likely as not", ">50%", "more likely than not")
   - Assess opinion certainty (definitive vs speculative language)
   - Check for clear medical conclusion about the nexus
   - Identify any hedging or equivocal language

2. SERVICE CONNECTION (25 points max):
   - Verify explicit linkage between condition and military service
   - Look for specific service events, exposures, or incidents mentioned
   - Check temporal relationship (when condition started relative to service)
   - Assess clarity of the service-connection statement

3. MEDICAL RATIONALE (25 points max):
   - Evaluate scientific/clinical explanation provided
   - Look for medical literature references or clinical guidelines
   - Assess logical reasoning from service event to current condition
   - Check for explanation of causation or aggravation mechanism

4. PROFESSIONAL FORMAT (25 points max):
   - Verify physician credentials are clearly stated
   - Check for professional letterhead or contact information
   - Assess overall letter structure and organization
   - Look for proper medical terminology usage

For each component, provide:
- score: 0-25 points based on VA standards
- confidence: 0-100% indicating your assessment confidence
- findings: array of specific text examples supporting the score
- issues: array of missing or problematic elements
- rationale: explanation for the score given

JSON Response Format:
{{
    "medical_opinion": {{
        "score": 0-25,
        "confidence": 0-100,
        "findings": ["specific positive examples from text"],
        "issues": ["missing or problematic elements"],
        "rationale": "explanation for score"
    }},
    "service_connection": {{
        "score": 0-25,
        "confidence": 0-100,
        "findings": ["specific positive examples from text"],
        "issues": ["missing or problematic elements"],
        "rationale": "explanation for score"
    }},
    "medical_rationale": {{
        "score": 0-25,
        "confidence": 0-100,
        "findings": ["specific positive examples from text"],
        "issues": ["missing or problematic elements"],
        "rationale": "explanation for score"
    }},
    "professional_format": {{
        "score": 0-25,
        "confidence": 0-100,
        "findings": ["specific positive examples from text"],
        "issues": ["missing or problematic elements"],
        "rationale": "explanation for score"
    }},
    "overall_score": sum of all component scores,
    "nexus_strength": "Strong/Moderate/Weak/None",
    "primary_condition": "main condition being evaluated",
    "service_connected_condition": "service-connected condition mentioned",
    "connection_theory": "direct/secondary/aggravation",
    "probability_language": "exact probability language used if any",
    "summary": "brief effectiveness summary",
    "key_strengths": ["top 3 strengths"],
    "critical_issues": ["must-fix issues"],
    "improvement_priorities": ["prioritized improvements"]
}}

Provide ONLY the JSON response, no additional text or formatting.
        """
        return prompt.strip()

    def _parse_response(
        self, response_text: str, correlation_id: str
    ) -> Dict[str, Any]:
        """
        Parse OpenAI response with enhanced error handling and validation.

        Args:
            response_text: Raw response from OpenAI
            correlation_id: Correlation ID for logging

        Returns:
            Parsed response dictionary
        """
        try:
            # Extract JSON from response if wrapped in text
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:-3].strip()
            elif response_text.startswith("```"):
                response_text = response_text[3:-3].strip()

            # Parse JSON
            parsed_data = json.loads(response_text)

            # Ensure overall_score is calculated if missing
            if (
                "overall_score" not in parsed_data
                or parsed_data["overall_score"] is None
            ):
                component_scores = [
                    parsed_data.get("medical_opinion", {}).get("score", 0),
                    parsed_data.get("service_connection", {}).get("score", 0),
                    parsed_data.get("medical_rationale", {}).get("score", 0),
                    parsed_data.get("professional_format", {}).get("score", 0),
                ]
                parsed_data["overall_score"] = sum(component_scores)

            # Validate component scores are within bounds
            for component in [
                "medical_opinion",
                "service_connection",
                "medical_rationale",
                "professional_format",
            ]:
                if component in parsed_data and "score" in parsed_data[component]:
                    score = parsed_data[component]["score"]
                    if score < 0 or score > 25:
                        parsed_data[component]["score"] = max(0, min(25, score))

            # Validate using Pydantic model
            analysis = NexusAnalysis(**parsed_data)

            self.logger.info(
                "AI response parsed successfully",
                metadata={"correlation_id": correlation_id},
            )

            return {
                "error": False,
                "message": "Analysis completed successfully",
                "analysis": analysis.dict(),
                "correlation_id": correlation_id,
            }

        except json.JSONDecodeError as e:
            self.logger.error(
                f"JSON parsing failed",
                error=e,
                metadata={"correlation_id": correlation_id},
            )
            return self._create_fallback_response(
                response_text, f"JSON error: {str(e)}", correlation_id
            )
        except Exception as e:
            self.logger.error(
                f"Response parsing failed",
                error=e,
                metadata={"correlation_id": correlation_id},
            )
            return self._create_fallback_response(response_text, str(e), correlation_id)

    def _create_fallback_response(
        self, raw_response: str, error_details: str, correlation_id: str
    ) -> Dict[str, Any]:
        """
        Create a fallback response when parsing fails.

        Args:
            raw_response: The raw AI response text
            error_details: Details about the parsing error
            correlation_id: Correlation ID for tracking

        Returns:
            Fallback response dictionary
        """
        self.logger.warning(
            f"Creating fallback response due to: {error_details}",
            metadata={"correlation_id": correlation_id},
        )

        # Record fallback usage
        self.performance_monitor.record_fallback_response(correlation_id)

        # Try to extract basic information from the response
        fallback_analysis = {
            "medical_opinion": {
                "score": 10,
                "confidence": 50,
                "findings": ["Unable to fully parse AI response"],
                "issues": ["Analysis parsing error occurred"],
                "rationale": "Fallback scoring applied due to parsing error",
            },
            "service_connection": {
                "score": 10,
                "confidence": 50,
                "findings": ["Unable to fully parse AI response"],
                "issues": ["Analysis parsing error occurred"],
                "rationale": "Fallback scoring applied due to parsing error",
            },
            "medical_rationale": {
                "score": 10,
                "confidence": 50,
                "findings": ["Unable to fully parse AI response"],
                "issues": ["Analysis parsing error occurred"],
                "rationale": "Fallback scoring applied due to parsing error",
            },
            "professional_format": {
                "score": 10,
                "confidence": 50,
                "findings": ["Unable to fully parse AI response"],
                "issues": ["Analysis parsing error occurred"],
                "rationale": "Fallback scoring applied due to parsing error",
            },
            "overall_score": 40,
            "nexus_strength": "Moderate",
            "primary_condition": "Unable to determine",
            "service_connected_condition": "Unable to determine",
            "connection_theory": "Unable to determine",
            "probability_language": None,
            "summary": "Analysis completed with parsing errors. Manual review recommended.",
            "key_strengths": ["Letter was submitted for analysis"],
            "critical_issues": ["AI response parsing failed - manual review needed"],
            "improvement_priorities": [
                "Resubmit letter for analysis",
                "Consider manual review",
            ],
        }

        return {
            "error": False,
            "message": "Analysis completed with fallback processing",
            "analysis": fallback_analysis,
            "warning": f"Parsing error occurred: {error_details}",
            "raw_response": (
                raw_response[:500] + "..." if len(raw_response) > 500 else raw_response
            ),
            "correlation_id": correlation_id,
            "fallback_used": True,
        }

    def _enrich_with_production_metadata(
        self,
        ai_result: Dict[str, Any],
        phi_detections: list,
        processing_time: float,
        correlation_id: str,
    ) -> Dict[str, Any]:
        """
        Enrich AI result with production metadata.

        Args:
            ai_result: Original AI analysis result
            phi_detections: List of PHI detections
            processing_time: Processing time in milliseconds
            correlation_id: Correlation ID

        Returns:
            Enriched result with production metadata
        """
        # Add production metadata
        ai_result["production_metadata"] = {
            "correlation_id": correlation_id,
            "processing_time_ms": processing_time,
            "phi_protected": self.enable_phi_protection,
            "phi_detections_count": len(phi_detections) if phi_detections else 0,
            "circuit_breaker_status": self.circuit_breaker.get_status(),
            "model_version": self.model,
            "timestamp": time.time(),
        }

        # Add PHI protection summary if enabled
        if self.enable_phi_protection and phi_detections:
            categories = list(set(d.category.value for d in phi_detections))
            ai_result["production_metadata"]["phi_categories_detected"] = categories

            # Log completion for audit
            self.audit_logger.log_analysis_complete(
                correlation_id,
                ai_result.get("analysis", {}).get("overall_score", 0),
                processing_time,
                not ai_result.get("error", False),
            )

        return ai_result

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of the analyzer.

        Returns:
            Health status including circuit breaker and performance metrics
        """
        health_data = {
            "timestamp": time.time(),
            "circuit_breaker": self.circuit_breaker.get_status(),
            "performance": self.performance_monitor.get_performance_snapshot(),
            "phi_protection_enabled": self.enable_phi_protection,
        }

        # Determine overall health
        cb_status = health_data["circuit_breaker"]["state"]
        if cb_status == "open":
            health_data["status"] = "unhealthy"
            health_data["issues"] = ["Circuit breaker is open - API unavailable"]
        elif cb_status == "half_open":
            health_data["status"] = "degraded"
            health_data["issues"] = ["Circuit breaker is testing recovery"]
        else:
            health_data["status"] = "healthy"
            health_data["issues"] = []

        return health_data


def create_analyzer(
    enable_phi_protection: bool = True,
) -> ProductionNexusLetterAnalyzer:
    """Create a new production-ready analyzer instance."""
    return ProductionNexusLetterAnalyzer(enable_phi_protection=enable_phi_protection)


# Quick test function for development
if __name__ == "__main__":
    analyzer = create_analyzer()
    success, message = analyzer.test_connection()
    print(f"Connection test: {'✓' if success else '✗'} {message}")

    # Test health status
    health = analyzer.get_health_status()
    print(f"Health status: {health['status']}")

    if health["issues"]:
        print(f"Issues: {health['issues']}")
