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


class NexusAnalysis(BaseModel):
    """Structured response model for nexus letter analysis."""
    
    # Connection Assessment
    nexus_strength: str = Field(..., description="Overall strength of nexus connection (Strong/Moderate/Weak/None)")
    probability_rating: str = Field(..., description="Medical probability rating (>50%, <50%, etc.)")
    
    # Key Components
    medical_opinion_present: bool = Field(..., description="Whether a clear medical opinion is stated")
    service_connection_stated: bool = Field(..., description="Whether service connection is explicitly stated")
    medical_rationale_provided: bool = Field(..., description="Whether medical reasoning is provided")
    
    # Analysis Details
    primary_condition: str = Field(..., description="Main condition being evaluated")
    service_connected_condition: str = Field(..., description="Service-connected condition mentioned")
    connection_theory: str = Field(..., description="Theory of connection (direct, secondary, aggravation)")
    
    # Legal Strengths and Weaknesses
    strengths: list[str] = Field(..., description="Legal/medical strengths of the letter")
    weaknesses: list[str] = Field(..., description="Potential weaknesses or missing elements")
    
    # Summary and Recommendations
    summary: str = Field(..., description="Brief summary of the nexus letter's effectiveness")
    recommendations: list[str] = Field(..., description="Suggestions for improvement if needed")


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
                messages=[{"role": "user", "content": "Test connection - respond with 'OK'"}],
                max_tokens=10
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
                    {"role": "system", "content": "You are an expert legal and medical analyst specializing in VA disability nexus letters. Provide thorough, professional analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            return self._parse_response(response_text)
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "error": True,
                "message": f"Analysis failed: {str(e)}",
                "details": None
            }
    
    def _build_prompt(self, letter_text: str) -> str:
        """
        Build the analysis prompt for OpenAI API.
        
        Args:
            letter_text: Raw nexus letter text
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
As a legal and medical expert, analyze this nexus letter for a VA disability claim. Evaluate the strength of the medical nexus connection and provide detailed feedback.

NEXUS LETTER TEXT:
{letter_text}

Please provide a comprehensive analysis in JSON format with the following structure:

{{
    "nexus_strength": "Strong/Moderate/Weak/None",
    "probability_rating": "The medical probability stated (e.g., '>50%', 'at least as likely as not')",
    "medical_opinion_present": true/false,
    "service_connection_stated": true/false,
    "medical_rationale_provided": true/false,
    "primary_condition": "Main condition being evaluated",
    "service_connected_condition": "Service-connected condition mentioned",
    "connection_theory": "direct/secondary/aggravation",
    "strengths": ["List of legal/medical strengths"],
    "weaknesses": ["List of potential weaknesses or missing elements"],
    "summary": "Brief summary of letter's effectiveness",
    "recommendations": ["Suggestions for improvement if needed"]
}}

Focus on:
1. Medical opinion clarity and strength
2. Service connection establishment
3. Medical rationale quality
4. Legal sufficiency for VA standards
5. Missing elements that could strengthen the claim

Provide only the JSON response, no additional text.
        """
        return prompt.strip()
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse OpenAI response into structured format.
        
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
            
            # Validate using Pydantic model
            analysis = NexusAnalysis(**parsed_data)
            
            return {
                "error": False,
                "message": "Analysis completed successfully",
                "analysis": analysis.dict()
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            return {
                "error": True,
                "message": "Failed to parse AI response",
                "details": f"JSON error: {str(e)}",
                "raw_response": response_text
            }
        except Exception as e:
            logger.error(f"Response parsing failed: {str(e)}")
            return {
                "error": True,
                "message": "Failed to process AI response",
                "details": str(e),
                "raw_response": response_text
            }


def create_analyzer() -> NexusLetterAnalyzer:
    """Create a new analyzer instance with current settings."""
    return NexusLetterAnalyzer()


# Quick test function for development
if __name__ == "__main__":
    analyzer = create_analyzer()
    success, message = analyzer.test_connection()
    print(f"Connection test: {'✓' if success else '✗'} {message}")