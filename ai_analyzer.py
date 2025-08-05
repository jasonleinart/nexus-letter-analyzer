"""OpenAI GPT-4 integration for nexus letter analysis."""

import json
import logging
from typing import Dict, Optional, Any
from openai import OpenAI
from pydantic import BaseModel, Field
from config import get_settings, validate_openai_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class NexusLetterAnalyzer:
    """AI-powered analyzer for nexus letters using OpenAI GPT-4."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the analyzer with OpenAI API key.

        Args:
            api_key: Optional API key. If None, loads from settings.
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key

        # Validate API key
        is_valid, error_msg = validate_openai_key(self.api_key)
        if not is_valid:
            raise ValueError(f"Invalid OpenAI API key: {error_msg}")

        # Initialize OpenAI client without proxies argument
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.model = "gpt-4-turbo-preview"
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def test_connection(self) -> tuple[bool, str]:
        """
        Test the connection to OpenAI API.

        Returns:
            Tuple of (success, message)
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Test connection - respond with 'OK'"}
                ],
                max_tokens=10,
            )
            return True, "Connection successful"
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False, f"Connection failed: {str(e)}"

    def analyze_letter(self, letter_text: str) -> Dict[str, Any]:
        """
        Analyze a nexus letter using OpenAI GPT-4.

        Args:
            letter_text: The complete text of the nexus letter

        Returns:
            Dictionary containing structured analysis results
        """
        try:
            prompt = self._build_prompt(letter_text)

            response = self.client.chat.completions.create(
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
            )

            response_text = response.choices[0].message.content
            return self._parse_response(response_text)

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "error": True,
                "message": f"Analysis failed: {str(e)}",
                "details": None,
            }

    def _build_prompt(self, letter_text: str) -> str:
        """
        Build the enhanced component-based analysis prompt for OpenAI API.

        Args:
            letter_text: Raw nexus letter text

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

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse OpenAI response into structured format with validation and fallback handling.

        Args:
            response_text: Raw response from OpenAI

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

            return {
                "error": False,
                "message": "Analysis completed successfully",
                "analysis": analysis.dict(),
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            return self._create_fallback_response(
                response_text, f"JSON error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Response parsing failed: {str(e)}")
            return self._create_fallback_response(response_text, str(e))

    def _create_fallback_response(
        self, raw_response: str, error_details: str
    ) -> Dict[str, Any]:
        """
        Create a fallback response when parsing fails.

        Args:
            raw_response: The raw AI response text
            error_details: Details about the parsing error

        Returns:
            Fallback response dictionary
        """
        logger.warning(f"Creating fallback response due to: {error_details}")

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
        }


def create_analyzer() -> NexusLetterAnalyzer:
    """Create a new analyzer instance with current settings."""
    return NexusLetterAnalyzer()


# Quick test function for development
if __name__ == "__main__":
    analyzer = create_analyzer()
    success, message = analyzer.test_connection()
    print(f"Connection test: {'✓' if success else '✗'} {message}")
