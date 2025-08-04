"""Configuration management for Nexus Letter AI Analyzer."""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Application Configuration
    app_name: str = os.getenv("APP_NAME", "Nexus Letter AI Analyzer")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Analysis Configuration
    max_text_length: int = 50000  # Maximum characters for input text
    min_text_length: int = 100    # Minimum characters for meaningful analysis
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


def validate_openai_key(api_key: Optional[str] = None) -> tuple[bool, str]:
    """
    Validate OpenAI API key format and presence.
    
    Args:
        api_key: Optional API key to validate. If None, uses settings.
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if api_key is None:
        settings = get_settings()
        api_key = settings.openai_api_key
    
    if not api_key:
        return False, "OpenAI API key is required"
    
    if not api_key.startswith("sk-"):
        return False, "OpenAI API key must start with 'sk-'"
    
    if len(api_key) < 20:
        return False, "OpenAI API key appears to be too short"
    
    return True, "API key format is valid"