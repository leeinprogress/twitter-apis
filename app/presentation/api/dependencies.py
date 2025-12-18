from typing import Annotated, Any

from fastapi import Depends

from app.application.services import TweetService
from app.bootstrap.config import Settings, get_settings
from app.infrastructure.cache.cache_service import RedisCacheService
from app.infrastructure.http.client import create_http_client
from app.infrastructure.twitter.client import TwitterClient
from app.infrastructure.twitter.rate_limiter import RateLimiter

_http_client = None
_rate_limiter = None
_cache_service = None


def get_http_client(settings: Annotated[Settings, Depends(get_settings)]) -> Any:
    global _http_client
    if _http_client is None:
        _http_client = create_http_client(settings)
    return _http_client


def get_rate_limiter() -> RateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_cache_service(settings: Annotated[Settings, Depends(get_settings)]) -> RedisCacheService:
    global _cache_service
    if _cache_service is None:
        _cache_service = RedisCacheService(settings)
    return _cache_service


def get_twitter_client(
    settings: Annotated[Settings, Depends(get_settings)],
    http_client: Annotated[Any, Depends(get_http_client)],
    rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
) -> TwitterClient:
    return TwitterClient(settings, http_client, rate_limiter)


def get_tweet_service(
    twitter_client: Annotated[TwitterClient, Depends(get_twitter_client)],
    cache_service: Annotated[RedisCacheService, Depends(get_cache_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TweetService:
    return TweetService(twitter_client, cache_service, settings)


