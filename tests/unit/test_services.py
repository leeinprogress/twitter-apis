from unittest.mock import AsyncMock

import pytest

from app.application.services import TweetService
from app.core.entities import Account, Tweet


class TestTweetService:
    @pytest.mark.asyncio
    async def test_get_tweets_by_hashtag_cache_miss(
        self, tweet_service: TweetService
    ):
        # Mock cache miss
        tweet_service.cache_service.get = AsyncMock(return_value=None)

        # Mock repository response
        mock_tweets = [
            Tweet(
                account=Account(fullname="Test", href="/test", id=123),
                date="1 Jan 2024",
                hashtags=["#test"],
                likes=10,
                replies=5,
                retweets=3,
                text="Test tweet",
            )
        ]
        tweet_service.tweet_repository.get_tweets_by_hashtag = AsyncMock(
            return_value=mock_tweets
        )
        tweet_service.cache_service.set = AsyncMock()

        result = await tweet_service.get_tweets_by_hashtag("test")

        assert result == mock_tweets
        tweet_service.tweet_repository.get_tweets_by_hashtag.assert_called_once_with("test", 30)
        tweet_service.cache_service.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tweets_by_hashtag_cache_hit(
        self, tweet_service: TweetService
    ):
        # Mock cache hit
        cached_tweets = [
            Tweet(
                account=Account(fullname="Cached", href="/cached", id=999),
                date="1 Jan 2024",
                hashtags=["#cached"],
                likes=100,
                replies=50,
                retweets=30,
                text="Cached tweet",
            )
        ]
        tweet_service.cache_service.get = AsyncMock(return_value=cached_tweets)
        tweet_service.tweet_repository.get_tweets_by_hashtag = AsyncMock()

        result = await tweet_service.get_tweets_by_hashtag("test")

        assert result == cached_tweets
        # Repository should not be called
        tweet_service.tweet_repository.get_tweets_by_hashtag.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_tweets_by_user(
        self, tweet_service: TweetService
    ):
        tweet_service.cache_service.get = AsyncMock(return_value=None)

        mock_tweets = [
            Tweet(
                account=Account(fullname="User", href="/user", id=456),
                date="2 Jan 2024",
                hashtags=["#user"],
                likes=20,
                replies=10,
                retweets=5,
                text="User tweet",
            )
        ]
        tweet_service.tweet_repository.get_tweets_by_user = AsyncMock(
            return_value=mock_tweets
        )
        tweet_service.cache_service.set = AsyncMock()

        result = await tweet_service.get_tweets_by_user("user")

        assert result == mock_tweets
        tweet_service.tweet_repository.get_tweets_by_user.assert_called_once_with("user", 30)

    @pytest.mark.asyncio
    async def test_normalize_limit_too_high(
        self, tweet_service: TweetService
    ):
        tweet_service.cache_service.get = AsyncMock(return_value=None)
        tweet_service.tweet_repository.get_tweets_by_hashtag = AsyncMock(return_value=[])

        await tweet_service.get_tweets_by_hashtag("test", limit=200)

        tweet_service.tweet_repository.get_tweets_by_hashtag.assert_called_once_with("test", 100)

    @pytest.mark.asyncio
    async def test_normalize_limit_too_low(
        self, tweet_service: TweetService
    ):
        tweet_service.cache_service.get = AsyncMock(return_value=None)
        tweet_service.tweet_repository.get_tweets_by_hashtag = AsyncMock(return_value=[])

        await tweet_service.get_tweets_by_hashtag("test", limit=0)

        # limit=0 is falsy, so default 30 is used
        tweet_service.tweet_repository.get_tweets_by_hashtag.assert_called_once_with("test", 30)

