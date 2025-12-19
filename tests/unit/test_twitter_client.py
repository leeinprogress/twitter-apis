from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.core.exceptions import (
    TwitterAuthenticationError,
    TwitterRateLimitError,
    TwitterResourceNotFoundError,
    TwitterServiceUnavailableError,
)
from app.infrastructure.twitter.client import TwitterClient
from tests.fixtures.twitter_responses import (
    MOCK_ERROR_RESPONSE_401,
    MOCK_ERROR_RESPONSE_404,
    MOCK_TWEET_SEARCH_RESPONSE,
    MOCK_USER_LOOKUP_RESPONSE,
    MOCK_USER_TIMELINE_RESPONSE,
)


class TestTwitterClient:
    @pytest.mark.asyncio
    async def test_get_tweets_by_hashtag_success(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_TWEET_SEARCH_RESPONSE
        mock_http_client.get.return_value = mock_response

        tweets = await twitter_client.get_tweets_by_hashtag("Python", limit=10)

        assert len(tweets) == 2
        assert tweets[0].text == "Check out this amazing #Python tutorial!"
        assert tweets[0].likes == 169
        assert tweets[0].hashtags == ["#Python"]
        assert tweets[1].text == "Learning #Python is fun! #coding"

    @pytest.mark.asyncio
    async def test_get_tweets_by_hashtag_removes_hash_symbol(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_TWEET_SEARCH_RESPONSE
        mock_http_client.get.return_value = mock_response

        await twitter_client.get_tweets_by_hashtag("#Python", limit=10)

        call_args = mock_http_client.get.call_args
        assert call_args.kwargs["params"]["query"] == "#Python"

    @pytest.mark.asyncio
    async def test_get_tweets_by_user_success(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        user_response = MagicMock(spec=httpx.Response)
        user_response.status_code = 200
        user_response.json.return_value = MOCK_USER_LOOKUP_RESPONSE

        timeline_response = MagicMock(spec=httpx.Response)
        timeline_response.status_code = 200
        timeline_response.json.return_value = MOCK_USER_TIMELINE_RESPONSE

        mock_http_client.get.side_effect = [user_response, timeline_response]

        tweets = await twitter_client.get_tweets_by_user("twitter", limit=10)

        assert len(tweets) == 1
        assert tweets[0].text == "Powerful voices. #InternationalWomensDay"
        assert tweets[0].likes == 287
        assert tweets[0].account.fullname == "Twitter"

    @pytest.mark.asyncio
    async def test_authentication_error_401(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 401
        mock_response.is_success = False
        mock_response.json.return_value = MOCK_ERROR_RESPONSE_401
        mock_response.text = "Unauthorized"
        mock_response.url = "https://api.twitter.com/2/tweets/search/recent"
        mock_response.headers = {}
        mock_http_client.get.return_value = mock_response

        with pytest.raises(TwitterAuthenticationError):
            await twitter_client.get_tweets_by_hashtag("Python", limit=10)

    @pytest.mark.asyncio
    async def test_resource_not_found_404(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.is_success = False
        mock_response.json.return_value = MOCK_ERROR_RESPONSE_404
        mock_response.text = "Not found"
        mock_response.url = "https://api.twitter.com/2/tweets/search/recent"
        mock_response.headers = {}
        mock_http_client.get.return_value = mock_response

        with pytest.raises(TwitterResourceNotFoundError):
            await twitter_client.get_tweets_by_hashtag("NonexistentHashtag", limit=10)

    @pytest.mark.asyncio
    async def test_rate_limit_error_429(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 429
        mock_response.is_success = False
        mock_response.json.return_value = {}
        mock_response.text = "Rate limit exceeded"
        mock_response.url = "https://api.twitter.com/2/tweets/search/recent"
        mock_response.headers = {"x-rate-limit-reset": "1234567890"}
        mock_http_client.get.return_value = mock_response

        with pytest.raises(TwitterRateLimitError) as exc_info:
            await twitter_client.get_tweets_by_hashtag("Python", limit=10)

        assert exc_info.value.reset_time == 1234567890

    @pytest.mark.asyncio
    async def test_limit_validation(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_TWEET_SEARCH_RESPONSE
        mock_http_client.get.return_value = mock_response

        await twitter_client.get_tweets_by_hashtag("Python", limit=200)

        call_args = mock_http_client.get.call_args
        assert call_args.kwargs["params"]["max_results"] == 100

    @pytest.mark.asyncio
    async def test_network_error(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_http_client.get.side_effect = httpx.RequestError("Connection timeout")

        with pytest.raises(TwitterServiceUnavailableError) as exc_info:
            await twitter_client.get_tweets_by_hashtag("Python", limit=10)

        assert "Twitter API request failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_server_error_500(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.is_success = False
        mock_response.json.return_value = {}
        mock_response.text = "Internal Server Error"
        mock_response.url = "https://api.twitter.com/2/tweets/search/recent"
        mock_response.headers = {}
        mock_http_client.get.return_value = mock_response

        with pytest.raises(TwitterServiceUnavailableError) as exc_info:
            await twitter_client.get_tweets_by_hashtag("Python", limit=10)

        assert "Twitter API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_empty_response_data(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [], "includes": {"users": []}}
        mock_http_client.get.return_value = mock_response

        tweets = await twitter_client.get_tweets_by_hashtag("RareHashtag", limit=10)

        assert tweets == []

    @pytest.mark.asyncio
    async def test_get_tweets_by_user_first_call_fails(
        self, twitter_client: TwitterClient, mock_http_client: AsyncMock
    ):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.json.return_value = MOCK_ERROR_RESPONSE_404
        mock_response.text = "User not found"
        mock_http_client.get.return_value = mock_response

        with pytest.raises(TwitterResourceNotFoundError):
            await twitter_client.get_tweets_by_user("nonexistent_user", limit=10)

