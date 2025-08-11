"""Advanced security features for production deployment."""

import hashlib
import time
from typing import Optional
import streamlit as st


class APIProtection:
    """Advanced API protection features."""

    @staticmethod
    def get_client_fingerprint() -> str:
        """Create a simple client fingerprint for rate limiting."""
        # In production, you might use IP + User-Agent
        # For demo, we'll use session-based tracking
        if "client_id" not in st.session_state:
            st.session_state.client_id = hashlib.md5(
                f"{time.time()}{id(st.session_state)}".encode()
            ).hexdigest()
        return st.session_state.client_id

    @staticmethod
    def check_honeypot() -> bool:
        """Simple honeypot to catch automated abuse."""
        # Add invisible form field that humans won't fill
        # If filled, likely a bot
        return True  # Simplified for demo

    @staticmethod
    def validate_input_safety(text: str) -> tuple[bool, str]:
        """Validate input for potential abuse patterns."""
        if len(text) > 100000:
            return False, "Text too long (max 100,000 characters)"

        # Check for potential prompt injection
        suspicious_patterns = [
            "ignore previous instructions",
            "system:",
            "assistant:",
            "\\n\\nHuman:",
            "\\n\\nAssistant:",
        ]

        text_lower = text.lower()
        for pattern in suspicious_patterns:
            if pattern in text_lower:
                return False, f"Suspicious content detected: {pattern}"

        return True, "Input validated"


# Usage cost tracking
class CostTracker:
    """Track estimated API costs."""

    # Rough GPT-4 pricing (update with current rates)
    COST_PER_1K_TOKENS = {
        "input": 0.03,  # $0.03 per 1K input tokens
        "output": 0.06,  # $0.06 per 1K output tokens
    }

    @classmethod
    def estimate_cost(cls, input_length: int) -> float:
        """Estimate cost for an analysis."""
        # Rough estimation: 1 token ≈ 4 characters
        input_tokens = input_length / 4
        output_tokens = 800  # Estimated output length

        input_cost = (input_tokens / 1000) * cls.COST_PER_1K_TOKENS["input"]
        output_cost = (output_tokens / 1000) * cls.COST_PER_1K_TOKENS["output"]

        return input_cost + output_cost
