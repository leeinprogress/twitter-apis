"""Twitter API Service - Main Application"""

from fastapi import FastAPI, HTTPException
import httpx

from app.bootstrap.config import get_settings

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Twitter API Service",
    description="RESTful API for fetching tweets from Twitter",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Twitter API Service",
        "version": "1.0.0"
    }


@app.get("/hashtags/{hashtag}")
async def get_tweets_by_hashtag(hashtag: str, limit: int = 30):
    """
    Get tweets by hashtag
    """
    # Clean hashtag
    hashtag = hashtag.lstrip("#")
    
    # Call Twitter API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.twitter_api_base_url}/tweets/search/recent",
                params={
                    "query": f"#{hashtag}",
                    "max_results": min(limit, 100),
                    "tweet.fields": "created_at,author_id,public_metrics,entities",
                    "expansions": "author_id",
                    "user.fields": "id,name,username"
                },
                headers={"Authorization": f"Bearer {settings.twitter_bearer_token}"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            elif response.status_code == 401:
                raise HTTPException(status_code=401, detail="Authentication failed")
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Twitter API error"
                )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Connection failed")


@app.get("/users/{username}")
async def get_user_tweets(username: str, limit: int = 30):
    """
    Get tweets from user's timeline
    """
    # Clean username
    username = username.lstrip("@")
    
    async with httpx.AsyncClient() as client:
        try:
            # Get user ID
            user_response = await client.get(
                f"{settings.twitter_api_base_url}/users/by/username/{username}",
                params={"user.fields": "id,name,username"},
                headers={"Authorization": f"Bearer {settings.twitter_bearer_token}"},
                timeout=30.0
            )
            
            if user_response.status_code != 200:
                raise HTTPException(status_code=404, detail="User not found")
            
            user_id = user_response.json()["data"]["id"]
            
            # Get user's tweets
            tweets_response = await client.get(
                f"{settings.twitter_api_base_url}/users/{user_id}/tweets",
                params={
                    "max_results": min(limit, 100),
                    "tweet.fields": "created_at,author_id,public_metrics,entities",
                    "expansions": "author_id",
                    "user.fields": "id,name,username"
                },
                headers={"Authorization": f"Bearer {settings.twitter_bearer_token}"},
                timeout=30.0
            )
            
            if tweets_response.status_code == 200:
                return tweets_response.json()
            elif tweets_response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            else:
                raise HTTPException(
                    status_code=tweets_response.status_code,
                    detail="Twitter API error"
                )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Connection failed")
