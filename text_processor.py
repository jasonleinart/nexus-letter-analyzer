"""Text processing pipeline for nexus letter analysis."""

import re
import logging
from typing import Tuple, Optional, Dict, Any
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextProcessor:
    """Handles text cleaning, validation, and preprocessing for nexus letters."""

    def __init__(self):
        """Initialize text processor with configuration."""
        self.settings = get_settings()
        self.max_length = self.settings.max_text_length
        self.min_length = self.settings.min_text_length

    def clean_text(self, raw_text: str) -> str:
        """
        Clean and normalize text while preserving medical/legal terminology.

        Args:
            raw_text: Raw input text from user

        Returns:
            Cleaned and normalized text
        """
        if not raw_text:
            return ""

        # Remove excessive whitespace while preserving paragraph structure
        text = re.sub(r"\r\n", "\n", raw_text)  # Normalize line endings
        text = re.sub(r"\n{3,}", "\n\n", text)  # Limit consecutive newlines
        text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces to single space
        text = re.sub(r" +\n", "\n", text)  # Remove trailing spaces
        text = re.sub(r"\n +", "\n", text)  # Remove leading spaces on new lines

        # Remove common OCR/formatting artifacts
        text = re.sub(r"[^\S\n]+", " ", text)  # Non-breaking spaces to regular spaces
        text = re.sub(
            r"[\u00A0\u2000-\u200B\u2028\u2029]", " ", text
        )  # Various unicode spaces

        # Fix common punctuation issues
        text = re.sub(
            r"([.!?])\s*([A-Z])", r"\1 \2", text
        )  # Ensure space after sentence endings
        text = re.sub(
            r"([a-z])([A-Z])", r"\1 \2", text
        )  # Fix merged words (basic case)

        # Clean up but preserve medical terminology structure
        text = text.strip()

        return text

    def validate_input(self, text: str) -> Tuple[bool, str]:
        """
        Validate text meets requirements for analysis.

        Args:
            text: Text to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Please enter text to analyze"

        text = text.strip()

        # Check length constraints
        if len(text) < self.min_length:
            return (
                False,
                f"Text is too short. Please enter at least {self.min_length} characters (currently {len(text)})",
            )

        if len(text) > self.max_length:
            return (
                False,
                f"Text is too long. Maximum {self.max_length} characters allowed (currently {len(text)})",
            )

        # Check for meaningful content
        if not self._has_meaningful_content(text):
            return (
                False,
                "Text appears to lack meaningful medical or legal content for analysis",
            )

        # Check for potential nexus letter indicators
        if not self._appears_to_be_nexus_letter(text):
            return (
                False,
                "Text does not appear to be a nexus letter. Please ensure it contains medical opinions about service connection.",
            )

        return True, "Text validation passed"

    def _has_meaningful_content(self, text: str) -> bool:
        """
        Check if text contains meaningful content for analysis.

        Args:
            text: Text to check

        Returns:
            True if text has meaningful content
        """
        # Check for minimum word count
        words = text.split()
        if len(words) < 20:
            return False

        # Check for letters (not just numbers/symbols)
        if not re.search(r"[a-zA-Z]", text):
            return False

        # Check for sentence structure
        if not re.search(r"[.!?]", text):
            return False

        return True

    def _appears_to_be_nexus_letter(self, text: str) -> bool:
        """
        Check if text appears to be a nexus letter based on common indicators.

        Args:
            text: Text to check

        Returns:
            True if text appears to be a nexus letter
        """
        text_lower = text.lower()

        # Medical opinion indicators
        medical_indicators = [
            "medical opinion",
            "professional opinion",
            "clinical opinion",
            "medical assessment",
            "diagnosis",
            "condition",
            "treatment",
            "medical history",
            "symptoms",
            "medical records",
        ]

        # Service connection indicators
        service_indicators = [
            "service connect",
            "military service",
            "veteran",
            "va ",
            "disability",
            "service-related",
            "service related",
            "likely as not",
            "probability",
            "nexus",
            "secondary to",
        ]

        # Probability language indicators
        probability_indicators = [
            "likely as not",
            "probability",
            "probable",
            "possible",
            "medical certainty",
            "reasonable",
            "opinion",
            "at least as likely",
            "more likely than not",
        ]

        # Check for presence of indicators from each category
        has_medical = any(indicator in text_lower for indicator in medical_indicators)
        has_service = any(indicator in text_lower for indicator in service_indicators)
        has_probability = any(
            indicator in text_lower for indicator in probability_indicators
        )

        # Need at least 2 out of 3 categories
        indicator_count = sum([has_medical, has_service, has_probability])
        return indicator_count >= 2

    def preprocess_for_ai(self, text: str) -> str:
        """
        Final preprocessing step before sending to AI analysis.

        Args:
            text: Cleaned and validated text

        Returns:
            Text optimized for AI processing
        """
        # Start with cleaned text
        processed_text = self.clean_text(text)

        # Ensure proper sentence separation for AI processing
        processed_text = re.sub(r"([.!?])\s*([A-Z])", r"\1\n\n\2", processed_text)

        # Add structure markers if they appear to be missing
        if not re.search(r"(Dear|To Whom|RE:|Subject:)", processed_text, re.IGNORECASE):
            # This might be just the letter body, add a note
            processed_text = "[Letter Body]\n\n" + processed_text

        return processed_text.strip()

    def extract_letter_components(self, text: str) -> Dict[str, Optional[str]]:
        """
        Extract key components from the nexus letter structure.

        Args:
            text: Full letter text

        Returns:
            Dictionary with extracted components
        """
        components = {
            "header": None,
            "recipient": None,
            "subject": None,
            "body": None,
            "signature": None,
            "credentials": None,
        }

        lines = text.split("\n")

        # Extract header (typically first few lines with address/date)
        header_lines = []
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            if line.strip() and not line.strip().lower().startswith(
                ("dear", "to whom")
            ):
                header_lines.append(line.strip())
            else:
                break

        if header_lines:
            components["header"] = "\n".join(header_lines)

        # Extract recipient (Dear/To Whom lines)
        for line in lines:
            line_clean = line.strip()
            if line_clean.lower().startswith(("dear", "to whom")):
                components["recipient"] = line_clean
                break

        # Extract subject/RE line
        for line in lines:
            line_clean = line.strip()
            if line_clean.lower().startswith(("re:", "subject:", "regarding:")):
                components["subject"] = line_clean
                break

        # Extract main body (everything between recipient and signature)
        body_lines = []
        in_body = False

        for line in lines:
            line_clean = line.strip()

            # Start body after recipient
            if not in_body and line_clean.lower().startswith(("dear", "to whom")):
                in_body = True
                continue

            # End body before signature
            if in_body and (
                line_clean.lower().startswith(("sincerely", "respectfully", "regards"))
                or re.search(r"(M\.?D\.?|Ph\.?D\.?|D\.?O\.?)", line_clean)
            ):
                break

            if in_body and line_clean:
                body_lines.append(line)

        if body_lines:
            components["body"] = "\n".join(body_lines).strip()

        return components

    def get_text_stats(self, text: str) -> Dict[str, Any]:
        """
        Get statistics about the text for display to user.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with text statistics
        """
        if not text:
            return {
                "character_count": 0,
                "word_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
            }

        words = text.split()
        sentences = re.split(r"[.!?]+", text)
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        return {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "paragraph_count": len(paragraphs),
        }


def create_processor() -> TextProcessor:
    """Create a new text processor instance."""
    return TextProcessor()


# Quick test function for development
if __name__ == "__main__":
    processor = create_processor()

    # Test with sample text
    sample = """
    This is a test nexus letter regarding veteran disability service connection.
    In my medical opinion, the condition is at least as likely as not related to military service.
    """

    cleaned = processor.clean_text(sample)
    is_valid, message = processor.validate_input(cleaned)
    stats = processor.get_text_stats(cleaned)

    print(f"Validation: {'✓' if is_valid else '✗'} {message}")
    print(f"Stats: {stats}")
