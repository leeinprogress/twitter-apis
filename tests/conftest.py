import os
from unittest.mock import AsyncMock

import httpx
import pytest

from app.bootstrap.config import Settings
from app.core.entities import Account, Tweet
from app.infrastructure.twitter.client import TwitterClient
from app.infrastructure.twitter.rate_limiter import RateLimiter


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        debug=True,
        host="0.0.0.0",
        port=8000,
        twitter_bearer_token="test_bearer_token",
        twitter_api_base_url="https://api.twitter.com/2",
        log_level="INFO",
        log_format="json",
    )


@pytest.fixture(scope="module")
def setup_integration_env():
    original_env = {}
    env_keys = [
        "DEBUG", "HOST", "PORT", "TWITTER_BEARER_TOKEN",
        "TWITTER_API_BASE_URL", "LOG_LEVEL", "LOG_FORMAT"
    ]
    
    for key in env_keys:
        original_env[key] = os.environ.get(key)
    
    os.environ["DEBUG"] = "true"
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PORT"] = "8000"
    os.environ["TWITTER_BEARER_TOKEN"] = "test_bearer_token"
    os.environ["TWITTER_API_BASE_URL"] = "https://api.twitter.com/2"
    os.environ["LOG_LEVEL"] = "INFO"
    os.environ["LOG_FORMAT"] = "json"
    
    yield
    
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def mock_http_client() -> AsyncMock:
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def rate_limiter() -> RateLimiter:
    return RateLimiter()


@pytest.fixture
def twitter_client(
    test_settings: Settings,
    mock_http_client: AsyncMock,
    rate_limiter: RateLimiter,
) -> TwitterClient:
    return TwitterClient(test_settings, mock_http_client, rate_limiter)


@pytest.fixture
def mock_tweets():
    return [
        Tweet(
            account=Account(
                fullname="Raymond Hettinger",
                href="/raymondh",
                id=14159138,
            ),
            date="12:57 PM - 7 Mar 2018",
            hashtags=["#python"],
            likes=169,
            replies=13,
            retweets=27,
            text="Historically, bash filename pattern matching was known as globbing.",
        ),
        Tweet(
            account=Account(
                fullname="Jane Doe",
                href="/janedoe",
                id=98765432,
            ),
            date="1:30 PM - 8 Mar 2024",
            hashtags=["#python", "#coding"],
            likes=42,
            replies=5,
            retweets=10,
            text="Learning #Python is fun! #coding",
        ),
    ]

