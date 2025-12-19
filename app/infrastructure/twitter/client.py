from contextlib import suppress
from typing import Any

import httpx

from app.bootstrap.config import Settings
from app.core.entities import Tweet
from app.core.exceptions import (
    TwitterAPIError,
    TwitterAuthenticationError,
    TwitterRateLimitError,
    TwitterResourceNotFoundError,
    TwitterServiceUnavailableError,
)
from app.core.interfaces import TweetRepository
from app.infrastructure.twitter.auth import TwitterAuthenticator
from app.infrastructure.twitter.mapper import map_tweet
from app.infrastructure.twitter.rate_limiter import RateLimiter
from app.utils.decorators import measure_time, retry_on_exception
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TwitterClient(TweetRepository):
    def __init__(
        self,
        settings: Settings,
        http_client: httpx.AsyncClient,
        rate_limiter: RateLimiter | None = None
    ):
        self.settings = settings
        self.http_client = http_client
        self.authenticator = TwitterAuthenticator(settings)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.base_url = settings.twitter_api_base_url
    
    @measure_time
    async def get_tweets_by_hashtag(self, hashtag: str, limit: int = 30) -> list[Tweet]:
        """
        Get tweets by hashtag
        
        Args:
            hashtag: Hashtag to search (with or without #)
            limit: Number of tweets to retrieve (default: 30)
            
        Returns:
            List of Tweet entities
        """
        hashtag = hashtag.lstrip("#")
        limit = min(limit, self.settings.twitter_max_results)
        logger.info(f"Fetching tweets by hashtag: {hashtag}, limit: {limit}")
        
        query = f"#{hashtag}"
        tweets = await self._search_tweets(query, limit)
        
        logger.info(f"Tweets fetched for hashtag '{hashtag}': {len(tweets)} tweets")
        return tweets
    
    @measure_time
    async def get_tweets_by_user(self, username: str, limit: int = 30) -> list[Tweet]:
        """
        Get tweets from user's timeline
        
        Args:
            username: Twitter username (with or without @)
            limit: Number of tweets to retrieve (default: 30)
            
        Returns:
            List of Tweet entities
        """
        username = username.lstrip("@")
        limit = min(limit, self.settings.twitter_max_results)
        logger.info(f"Fetching tweets by user: {username}, limit: {limit}")
        
        user_id = await self._get_user_id(username)
        tweets = await self._get_user_timeline(user_id, limit)
        
        logger.info(f"Tweets fetched for user '{username}': {len(tweets)} tweets")
        return tweets
    
    @retry_on_exception(
        max_retries=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(httpx.HTTPError, TwitterServiceUnavailableError),
    )
    async def _search_tweets(self, query: str, limit: int) -> list[Tweet]:
        """Search tweets by query with retry logic."""
        await self.rate_limiter.acquire("search_tweets")
        
        url = f"{self.base_url}/tweets/search/recent"
        params = {
            "query": query,
            "max_results": limit,
            "tweet.fields": "created_at,public_metrics,entities,author_id",
            "expansions": "author_id",
            "user.fields": "id,name,username"
        }
        
        try:
            response = await self.http_client.get(
                url,
                params=params,
                headers=self.authenticator.get_headers(),
                timeout=self.settings.twitter_request_timeout,
            )
            
            self._handle_response_errors(response)
            
            data = response.json()
            return self._parse_tweets_response(data)
        
        except httpx.HTTPError as e:
            logger.error(f"Twitter API HTTP error for query '{query}': {e}")
            raise TwitterServiceUnavailableError(f"Twitter API request failed: {e}") from e
    
    @retry_on_exception(
        max_retries=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(httpx.HTTPError, TwitterServiceUnavailableError),
    )
    async def _get_user_id(self, username: str) -> str:
        """Get user ID by username with retry logic."""
        await self.rate_limiter.acquire("get_user")
        
        url = f"{self.base_url}/users/by/username/{username}"
        
        try:
            response = await self.http_client.get(
                url,
                params={"user.fields": "id,name,username"},
                headers=self.authenticator.get_headers(),
                timeout=self.settings.twitter_request_timeout,
            )
            
            self._handle_response_errors(response)
            
            data = response.json()
            user_data = data.get("data")
            
            if not user_data or "id" not in user_data:
                raise TwitterResourceNotFoundError(f"User @{username} not found")
            
            return str(user_data["id"])
        
        except httpx.HTTPError as e:
            logger.error(f"Twitter API HTTP error for username '{username}': {e}")
            raise TwitterServiceUnavailableError(f"Twitter API request failed: {e}") from e
    
    @retry_on_exception(
        max_retries=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(httpx.HTTPError, TwitterServiceUnavailableError),
    )
    async def _get_user_timeline(self, user_id: str, limit: int) -> list[Tweet]:
        """Get user timeline with retry logic."""
        await self.rate_limiter.acquire("user_timeline")
        
        url = f"{self.base_url}/users/{user_id}/tweets"
        params = {
            "max_results": limit,
            "tweet.fields": "created_at,author_id,public_metrics,entities",
            "expansions": "author_id",
            "user.fields": "id,name,username"
        }
        
        try:
            response = await self.http_client.get(
                url,
                params=params,
                headers=self.authenticator.get_headers(),
                timeout=self.settings.twitter_request_timeout,
            )
            
            self._handle_response_errors(response)
            
            data = response.json()
            return self._parse_tweets_response(data)
        
        except httpx.HTTPError as e:
            logger.error(f"Twitter API HTTP error for user_id '{user_id}': {e}")
            raise TwitterServiceUnavailableError(f"Twitter API request failed: {e}") from e
    
    def _handle_response_errors(self, response: httpx.Response) -> None:
        """Handle HTTP response errors"""
        if response.is_success:
            return
        
        status_code = response.status_code
        error_data = {}
        
        with suppress(Exception):
            error_data = response.json()
        
        error_message = error_data.get("detail", response.text)
        
        logger.error(
            f"Twitter API error: status={status_code}, url={response.url}, error={error_message}"
        )
        
        if status_code == 401:
            raise TwitterAuthenticationError("Invalid or expired Twitter API credentials")
        elif status_code == 403:
            raise TwitterAuthenticationError("Access forbidden. Check API permissions.")
        elif status_code == 404:
            raise TwitterResourceNotFoundError("Requested resource not found")
        elif status_code == 429:
            # Extract rate limit reset time if available
            reset_time = response.headers.get("x-rate-limit-reset")
            raise TwitterRateLimitError(
                "Twitter API rate limit exceeded",
                reset_time=int(reset_time) if reset_time else None,
            )
        elif status_code >= 500:
            raise TwitterServiceUnavailableError(f"Twitter API error: {error_message}")
        else:
            raise TwitterAPIError(f"Twitter API error: {error_message}", status_code)
    
    def _parse_tweets_response(self, data: dict[str, Any]) -> list[Tweet]:
        """Parse tweets from API response."""
        tweets_data = data.get("data", [])
        includes = data.get("includes", {})
        
        if not tweets_data:
            logger.warning("No tweets in response")
            return []
        
        tweets: list[Tweet] = []
        for tweet_data in tweets_data:
            tweet = map_tweet(tweet_data, includes)
            if tweet:
                tweets.append(tweet)
        
        return tweets
