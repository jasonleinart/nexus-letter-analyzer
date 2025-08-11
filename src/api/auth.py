"""
Authentication and rate limiting for the Nexus Letter Analysis API.
"""

import time
import hashlib
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta

import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.limits = {
            "development": {"requests": 100, "window": 3600},  # 100/hour
            "production": {"requests": 1000, "window": 3600},  # 1000/hour
            "internal": {"requests": 10000, "window": 3600},  # 10000/hour
        }

    def is_allowed(self, api_key: str, environment: str) -> Tuple[bool, Dict[str, int]]:
        """Check if request is allowed under rate limit."""
        now = time.time()
        limit_config = self.limits.get(environment, self.limits["development"])

        # Clean old requests
        key_requests = self.requests[api_key]
        while key_requests and key_requests[0] < now - limit_config["window"]:
            key_requests.popleft()

        # Check limit
        current_requests = len(key_requests)
        remaining = limit_config["requests"] - current_requests

        if remaining <= 0:
            return False, {
                "requests_remaining": 0,
                "reset_at": int(now + limit_config["window"]),
                "limit": limit_config["requests"],
            }

        # Record this request
        key_requests.append(now)

        return True, {
            "requests_remaining": remaining - 1,
            "reset_at": int(now + limit_config["window"]),
            "limit": limit_config["requests"],
        }


class APIKeyManager:
    """Manage API keys and permissions."""

    def __init__(self):
        # In production, these would be in a database
        self.api_keys = {
            "dev-key-12345": {
                "environment": "development",
                "name": "Development Key",
                "created_at": "2024-01-01T00:00:00Z",
                "permissions": ["read", "write", "analyze"],
            },
            "prod-key-67890": {
                "environment": "production",
                "name": "Production Key",
                "created_at": "2024-01-01T00:00:00Z",
                "permissions": ["read", "write", "analyze", "batch"],
            },
            "internal-key-abcde": {
                "environment": "internal",
                "name": "Internal Systems Key",
                "created_at": "2024-01-01T00:00:00Z",
                "permissions": ["read", "write", "analyze", "batch", "admin"],
            },
        }

    def validate_key(self, api_key: str) -> Optional[Dict]:
        """Validate API key and return key info."""
        return self.api_keys.get(api_key)

    def has_permission(self, api_key: str, permission: str) -> bool:
        """Check if API key has specific permission."""
        key_info = self.validate_key(api_key)
        if not key_info:
            return False
        return permission in key_info.get("permissions", [])

    def generate_key(self, environment: str, name: str) -> str:
        """Generate new API key (for admin use)."""
        timestamp = str(int(time.time()))
        raw_key = f"{environment}-{name}-{timestamp}"
        return hashlib.sha256(raw_key.encode()).hexdigest()[:32]


# Global instances
rate_limiter = RateLimiter()
key_manager = APIKeyManager()


def check_rate_limit(api_key: str, environment: str) -> Dict[str, int]:
    """Check rate limit and raise exception if exceeded."""
    allowed, rate_info = rate_limiter.is_allowed(api_key, environment)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "limit": rate_info["limit"],
                "reset_at": rate_info["reset_at"],
            },
            headers={
                "X-RateLimit-Limit": str(rate_info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(rate_info["reset_at"]),
            },
        )

    return rate_info


def validate_permission(api_key: str, permission: str):
    """Validate API key has required permission."""
    if not key_manager.has_permission(api_key, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key does not have '{permission}' permission",
        )
