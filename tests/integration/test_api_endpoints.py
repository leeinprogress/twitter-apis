from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import (
    TwitterAuthenticationError,
    TwitterRateLimitError,
    TwitterResourceNotFoundError,
    TwitterServiceUnavailableError,
)


@pytest.fixture
def client(setup_integration_env):
    from app.main import app
    return TestClient(app)


class TestRootEndpoint:
    def test_root(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Twitter API Service"
        assert data["version"] == "1.0.0"


class TestHashtagEndpoint:
    def test_get_tweets_by_hashtag_success(self, client, mock_tweets):
        with patch(
            "app.main.tweet_service.get_tweets_by_hashtag",
            new_callable=AsyncMock,
            return_value=mock_tweets,
        ):
            response = client.get("/hashtags/Python?limit=30")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["text"] == "Historically, bash filename pattern matching was known as globbing."
            assert data[0]["likes"] == 169
            assert data[0]["hashtags"] == ["#python"]
            assert data[0]["account"]["fullname"] == "Raymond Hettinger"
            assert data[0]["account"]["href"] == "/raymondh"
            assert data[0]["account"]["id"] == 14159138
    
    def test_get_tweets_by_hashtag_default_limit(self, client, mock_tweets):
        with patch(
            "app.main.tweet_service.get_tweets_by_hashtag",
            new_callable=AsyncMock,
            return_value=mock_tweets,
        ):
            response = client.get("/hashtags/Python")
            
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    def test_get_tweets_by_hashtag_custom_limit(self, client, mock_tweets):
        with patch(
            "app.main.tweet_service.get_tweets_by_hashtag",
            new_callable=AsyncMock,
            return_value=[mock_tweets[0]],
        ):
            response = client.get("/hashtags/Python?limit=1")
            
            assert response.status_code == 200
            assert len(response.json()) == 1
    
    def test_get_tweets_by_hashtag_empty_result(self, client):
        with patch(
            "app.main.tweet_service.get_tweets_by_hashtag",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = client.get("/hashtags/RareHashtag?limit=30")
            
            assert response.status_code == 200
            assert response.json() == []


class TestUserEndpoint:
    def test_get_tweets_by_user_success(self, client, mock_tweets):
        with patch(
            "app.main.tweet_service.get_tweets_by_user",
            new_callable=AsyncMock,
            return_value=mock_tweets,
        ):
            response = client.get("/users/twitter?limit=20")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["account"]["fullname"] == "Raymond Hettinger"
            assert data[1]["text"] == "Learning #Python is fun! #coding"
    
    def test_get_tweets_by_user_default_limit(self, client, mock_tweets):
        with patch(
            "app.main.tweet_service.get_tweets_by_user",
            new_callable=AsyncMock,
            return_value=mock_tweets,
        ):
            response = client.get("/users/twitter")
            
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    def test_get_tweets_by_user_with_at_symbol(self, client, mock_tweets):
        with patch(
            "app.main.tweet_service.get_tweets_by_user",
            new_callable=AsyncMock,
            return_value=mock_tweets,
        ):
            response = client.get("/users/@twitter?limit=10")
            
            assert response.status_code == 200
            assert len(response.json()) == 2
    
    def test_get_tweets_by_user_empty_result(self, client):
        with patch(
            "app.main.tweet_service.get_tweets_by_user",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = client.get("/users/unknown_user")
            
            assert response.status_code == 200
            assert response.json() == []


class TestErrorHandling:
    def test_authentication_error_401(self, client):
        with patch(
            "app.main.tweet_service.get_tweets_by_hashtag",
            side_effect=TwitterAuthenticationError("Invalid or expired bearer token"),
        ):
            response = client.get("/hashtags/Python")
            
            assert response.status_code == 401
            assert "Invalid or expired bearer token" in response.json()["detail"]
    
    def test_resource_not_found_404(self, client):
        with patch(
            "app.main.tweet_service.get_tweets_by_hashtag",
            side_effect=TwitterResourceNotFoundError("Resource not found"),
        ):
            response = client.get("/hashtags/NonexistentHashtag")
            
            assert response.status_code == 404
            assert "Resource not found" in response.json()["detail"]
    
    def test_rate_limit_error_429(self, client):
        with patch(
            "app.main.tweet_service.get_tweets_by_hashtag",
            side_effect=TwitterRateLimitError("Rate limit exceeded"),
        ):
            response = client.get("/hashtags/Python")
            
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.json()["detail"]
    
    def test_service_unavailable_503(self, client):
        with patch(
            "app.main.tweet_service.get_tweets_by_user",
            side_effect=TwitterServiceUnavailableError("Twitter service error"),
        ):
            response = client.get("/users/twitter")
            
            assert response.status_code == 503
            assert "Twitter service error" in response.json()["detail"]
