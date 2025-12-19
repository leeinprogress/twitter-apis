import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def load_environment() -> dict[str, Any]:
    env_file = Path(".env")

    if env_file.exists():
        load_dotenv(env_file)
        print("Environment loaded from .env")
    else:
        env_example = Path(".env.example")
        if env_example.exists():
            load_dotenv(env_example)
            print("No .env file - using .env.example")
        else:
            print("No .env files found - using defaults")

    bearer_token = os.getenv("TWITTER_BEARER_TOKEN", "")
    if not bearer_token or bearer_token == "your_bearer_token_here":
        print("\n WARNING: TWITTER_BEARER_TOKEN not configured!")
        if os.getenv("ENVIRONMENT") == "production":
            print("Cannot start in production without valid token")
            sys.exit(1)

    return {
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
        "twitter_bearer_token": bearer_token,
        "twitter_api_base_url": os.getenv(
            "TWITTER_API_BASE_URL",
            "https://api.twitter.com/2"
        ),
        "twitter_max_results": int(os.getenv("TWITTER_MAX_RESULTS", "100")),
        "twitter_request_timeout": int(os.getenv("TWITTER_REQUEST_TIMEOUT", "30")),
        "cache_enabled": os.getenv("CACHE_ENABLED", "false").lower() == "true",
        "cache_ttl": int(os.getenv("CACHE_TTL", "300")),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "redis_enabled": os.getenv("REDIS_ENABLED", "false").lower() == "true",
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "log_format": os.getenv("LOG_FORMAT", "json"),
        "cors_origins": os.getenv("CORS_ORIGINS", ""),
    }
