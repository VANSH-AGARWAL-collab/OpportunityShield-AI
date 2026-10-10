"""
OpportunityShield AI - Configuration Module
Safely loads environment variables, manages secrets, and defines search parameters.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file if it exists
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


class Config:
    """Application configuration settings."""

    # Security: Read SECRET_KEY from environment. Never use a fixed production secret fallback.
    # Keep DEBUG disabled by default. If SECRET_KEY is not configured:
    # - In debug/dev mode: use a safe development-only key
    # - In production: generate an ephemeral cryptographically secure token
    DEBUG = os.getenv("FLASK_DEBUG", "0").lower() in ("true", "1", "yes")
    SECRET_KEY = os.getenv("SECRET_KEY") or ("dev-insecure-key-local-testing-only" if DEBUG else os.urandom(32).hex())
    PORT = int(os.getenv("PORT", 5000))
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1MB request body limit

    # SerpApi Settings (Never expose this key in API responses or frontend)
    SERPAPI_KEY = os.getenv("SERPAPI_KEY", "").strip()
    SERPAPI_BASE_URL = "https://serpapi.com/search"

    # Search Limits (to balance search depth with latency & credit usage)
    MAX_ORGANIC_RESULTS = int(os.getenv("SERPAPI_MAX_ORGANIC_RESULTS", 8))
    MAX_NEWS_RESULTS = int(os.getenv("SERPAPI_MAX_NEWS_RESULTS", 6))
    MAX_JOBS_RESULTS = int(os.getenv("SERPAPI_MAX_JOBS_RESULTS", 6))
    SEARCH_TIMEOUT = int(os.getenv("SERPAPI_TIMEOUT_SECONDS", 12))

    # Persistence
    DATABASE_PATH = BASE_DIR / "opportunity_shield.db"

    @classmethod
    def has_serpapi_key(cls) -> bool:
        """Returns True if a non-empty SerpApi key is configured."""
        return bool(cls.SERPAPI_KEY and len(cls.SERPAPI_KEY) > 5)

