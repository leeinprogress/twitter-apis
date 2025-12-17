"""Environment configuration"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def load_environment() -> dict[str, Any]:
    """Load environment variables from .env file"""
    env_file = Path(".env")
    
    if env_file.exists():
        load_dotenv(env_file)
        print("✓ Environment loaded from .env")
    else:
        env_example = Path(".env.example")
        if env_example.exists():
            load_dotenv(env_example)
            print("⚠ No .env file - using .env.example")
        else:
            print("⚠ No .env files found - using defaults")
    
    return {
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", "8000")),
        "twitter_bearer_token": os.getenv("TWITTER_BEARER_TOKEN", ""),
        "twitter_api_base_url": os.getenv(
            "TWITTER_API_BASE_URL", 
            "https://api.twitter.com/2"
        ),
    }
