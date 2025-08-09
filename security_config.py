"""Security configuration for API key protection and abuse prevention."""

import os
from typing import Dict, Any

# Demo usage limits
DEMO_LIMITS = {
    "max_analyses_per_hour": 5,
    "max_text_length": 50000,  # Prevent huge requests
    "rate_limit_window": 3600,  # 1 hour in seconds
}

# Production limits (when users are authenticated)
PRODUCTION_LIMITS = {
    "max_analyses_per_hour": 50,
    "max_text_length": 100000,
    "rate_limit_window": 3600,
}

def get_usage_limits(is_authenticated: bool = False) -> Dict[str, Any]:
    """Get appropriate usage limits based on user authentication."""
    return PRODUCTION_LIMITS if is_authenticated else DEMO_LIMITS

def validate_api_key_usage():
    """Additional API key validation and monitoring."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return False, "API key not configured"
    
    if not api_key.startswith("sk-"):
        return False, "Invalid API key format"
    
    # In production, you could add:
    # - API key usage monitoring
    # - Cost tracking
    # - User attribution
    
    return True, "API key valid"

# Security headers for deployment
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY", 
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}
