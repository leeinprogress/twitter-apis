"""Pytest configuration and fixtures."""

import os
from unittest.mock import AsyncMock, patch

import httpx
import pytest

# Set test environment variables before any app imports
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("TWITTER_BEARER_TOKEN", "test_bearer_token")
os.environ.setdefault("TWITTER_API_BASE_URL", "https://api.twitter.com/2")
os.environ.setdefault("CACHE_ENABLED", "false")
os.environ.setdefault("CACHE_TTL", "300")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("REDIS_ENABLED", "false")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("LOG_FORMAT", "json")

# Mock load_dotenv to prevent file access in tests
with patch('dotenv.load_dotenv', return_value=None):
    from app.application.services import TweetService
    from app.bootstrap.config import Settings
    from app.infrastructure.cache.cache_service import RedisCacheService
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
        cache_enabled=False,
        cache_ttl=300,
        redis_url="redis://localhost:6379",
        redis_enabled=False,
        log_level="INFO",
        log_format="json",
    )


@pytest.fixture
def mock_http_client() -> AsyncMock:
    """Create mock HTTP client."""
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def rate_limiter() -> RateLimiter:
    """Create rate limiter for tests."""
    return RateLimiter()


@pytest.fixture
def cache_service(test_settings: Settings) -> RedisCacheService:
    """Create cache service for tests."""
    return RedisCacheService(test_settings)


@pytest.fixture
def twitter_client(
    test_settings: Settings,
    mock_http_client: AsyncMock,
    rate_limiter: RateLimiter,
) -> TwitterClient:
    """Create Twitter API client for tests."""
    return TwitterClient(test_settings, mock_http_client, rate_limiter)


@pytest.fixture
def tweet_service(
    twitter_client: TwitterClient,
    cache_service: RedisCacheService,
    test_settings: Settings,
) -> TweetService:
    """Create tweet service for tests."""
    return TweetService(twitter_client, cache_service, test_settings)

