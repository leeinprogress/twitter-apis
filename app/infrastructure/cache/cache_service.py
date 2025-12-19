from typing import Any
from urllib.parse import urlparse

from aiocache import Cache
from aiocache.serializers import JsonSerializer

from app.bootstrap.config import Settings
from app.core.entities import Account, Tweet
from app.core.exceptions import CacheError
from app.core.interfaces import CacheService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RedisCacheService(CacheService):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.enabled = settings.cache_enabled
        self.ttl = settings.cache_ttl

        if not self.enabled:
            logger.info("Cache disabled")
            self._cache: Cache | None = None
            return

        if settings.redis_enabled:
            try:
                parsed = urlparse(settings.redis_url)
                self._cache = Cache(
                    Cache.REDIS,
                    endpoint=parsed.hostname or "localhost",
                    port=parsed.port or 6379,
                    serializer=JsonSerializer(),
                    namespace="twitter_api",
                )
                logger.info("Cache initialized with Redis backend")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, falling back to memory cache")
                self._cache = Cache(Cache.MEMORY, serializer=JsonSerializer())
                logger.info("Cache initialized with memory backend")
        else:
            self._cache = Cache(Cache.MEMORY, serializer=JsonSerializer())
            logger.info("Cache initialized with memory backend")

    async def get(self, key: str) -> list[Tweet] | None:
        if not self.enabled or not self._cache:
            return None

        try:
            cached_data = await self._cache.get(key)
            if cached_data:
                logger.debug(f"Cache hit: {key}")
                return self._deserialize_tweets(cached_data)
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    async def set(self, key: str, value: list[Tweet], ttl: int) -> None:
        if not self.enabled or not self._cache:
            return

        try:
            serialized = self._serialize_tweets(value)
            await self._cache.set(key, serialized, ttl=ttl)
            logger.debug(f"Cache set: {key} (ttl={ttl}s, items={len(value)})")
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            raise CacheError(f"Failed to set cache: {e}") from e

    async def delete(self, key: str) -> None:
        if not self.enabled or not self._cache:
            return

        try:
            await self._cache.delete(key)
            logger.debug(f"Cache deleted: {key}")
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")

    def _serialize_tweets(self, tweets: list[Tweet]) -> list[dict[str, Any]]:
        return [
            {
                "account": {
                    "fullname": tweet.account.fullname,
                    "href": tweet.account.href,
                    "id": tweet.account.id,
                },
                "date": tweet.date,
                "hashtags": tweet.hashtags,
                "likes": tweet.likes,
                "replies": tweet.replies,
                "retweets": tweet.retweets,
                "text": tweet.text,
            }
            for tweet in tweets
        ]

    def _deserialize_tweets(self, data: list[dict[str, Any]]) -> list[Tweet]:
        tweets = []
        for item in data:
            try:
                account_data = item["account"]
                account = Account(
                    fullname=account_data["fullname"],
                    href=account_data["href"],
                    id=account_data["id"],
                )
                tweet = Tweet(
                    account=account,
                    date=item["date"],
                    hashtags=item["hashtags"],
                    likes=item["likes"],
                    replies=item["replies"],
                    retweets=item["retweets"],
                    text=item["text"],
                )
                tweets.append(tweet)
            except (KeyError, ValueError) as e:
                logger.warning(f"Tweet deserialization error: {e}")
                continue
        return tweets

    async def close(self) -> None:
        if self._cache:
            await self._cache.close()
            logger.info("Cache closed")

