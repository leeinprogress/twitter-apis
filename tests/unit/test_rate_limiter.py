import asyncio

import pytest

from app.core.exceptions import TwitterRateLimitError
from app.infrastructure.twitter.rate_limiter import RateLimiter


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_acquire_search_tweets_within_limit(self):
        limiter = RateLimiter()

        for _ in range(10):
            await limiter.acquire("search_tweets")

    @pytest.mark.asyncio
    async def test_acquire_exceeds_limit(self):
        limiter = RateLimiter()

        for _ in range(12):
            await limiter.acquire("search_tweets")

        with pytest.raises(TwitterRateLimitError):
            await limiter.acquire("search_tweets")

    @pytest.mark.asyncio
    async def test_rate_limit_resets_after_window(self):
        limiter = RateLimiter()

        await limiter.acquire("test")
        await limiter.acquire("test")

        # Wait for window to expire
        await asyncio.sleep(1.1)

        # Should be able to acquire again
        await limiter.acquire("test")

    @pytest.mark.asyncio
    async def test_different_keys_have_separate_limits(self):
        limiter = RateLimiter()

        for _ in range(12):
            await limiter.acquire("search_tweets")

        await limiter.acquire("get_user")
        await limiter.acquire("user_timeline")


