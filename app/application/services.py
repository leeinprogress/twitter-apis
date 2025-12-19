from collections.abc import Awaitable, Callable
from typing import Any

from app.bootstrap.config import Settings
from app.core.entities import Tweet
from app.core.interfaces import CacheService, TweetRepository
from app.utils.decorators import measure_time
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TweetService:
    def __init__(
        self,
        tweet_repository: TweetRepository,
        cache_service: CacheService,
        settings: Settings,
    ) -> None:
        self.tweet_repository = tweet_repository
        self.cache_service = cache_service
        self.settings = settings

    def _normalize_limit(self, limit: int) -> int:
        return max(1, min(limit, 100)) if limit else 30

    async def _get_with_cache(
        self, cache_key: str, fetch_fn: Callable[..., Awaitable[list[Tweet]]], *args: Any
    ) -> list[Tweet]:
        cached = await self.cache_service.get(cache_key)
        if cached is not None:
            return cached

        tweets = await fetch_fn(*args)
        if tweets:
            await self.cache_service.set(cache_key, tweets, self.settings.cache_ttl)
        return tweets

    @measure_time
    async def get_tweets_by_hashtag(self, hashtag: str, limit: int = 30) -> list[Tweet]:
        hashtag = hashtag.lstrip("#").strip()
        limit = self._normalize_limit(limit)
        cache_key = f"hashtag:{hashtag}:limit:{limit}"
        return await self._get_with_cache(
            cache_key, self.tweet_repository.get_tweets_by_hashtag, hashtag, limit
        )

    @measure_time
    async def get_tweets_by_user(self, username: str, limit: int = 30) -> list[Tweet]:
        username = username.lstrip("@").strip()
        limit = self._normalize_limit(limit)
        cache_key = f"user:{username}:limit:{limit}"
        return await self._get_with_cache(
            cache_key, self.tweet_repository.get_tweets_by_user, username, limit
        )

