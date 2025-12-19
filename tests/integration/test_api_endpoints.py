from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.entities import Account, Tweet
from app.main import app
from app.presentation.api.dependencies import get_tweet_service


@pytest.fixture
def mock_tweet_service():
    return AsyncMock()


@pytest.fixture
def client(mock_tweet_service):
    app.dependency_overrides[get_tweet_service] = lambda: mock_tweet_service

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture
def mock_tweets():
    return [
        Tweet(
            account=Account(
                fullname="Raymond Hettinger",
                href="/raymondh",
                id=14159138,
            ),
            date="12:57 PM - 7 Mar 2018",
            hashtags=["#python"],
            likes=169,
            replies=13,
            retweets=27,
            text="Historically, bash filename pattern matching was known as globbing.",
        )
    ]


class TestHashtagEndpoint:
    """Tests for /api/v1/hashtags/{hashtag} endpoint."""

    def test_get_tweets_by_hashtag_success(self, client, mock_tweet_service, mock_tweets):
        mock_tweet_service.get_tweets_by_hashtag.return_value = mock_tweets

        response = client.get("/api/v1/hashtags/Python?limit=30")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "Historically, bash filename pattern matching was known as globbing."
        assert data[0]["likes"] == 169
        assert data[0]["hashtags"] == ["#python"]
        mock_tweet_service.get_tweets_by_hashtag.assert_called_once_with("Python", 30)

    def test_get_tweets_by_hashtag_default_limit(self, client, mock_tweet_service, mock_tweets):
        mock_tweet_service.get_tweets_by_hashtag.return_value = mock_tweets

        response = client.get("/api/v1/hashtags/Python")

        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_tweet_service.get_tweets_by_hashtag.assert_called_once_with("Python", 30)

    def test_get_tweets_by_hashtag_invalid_limit(self, client):
        response = client.get("/api/v1/hashtags/Python?limit=0")

        assert response.status_code == 422  # Validation error

    def test_get_tweets_by_hashtag_empty_hashtag(self, client):
        response = client.get("/api/v1/hashtags/?limit=30")

        assert response.status_code == 404  # Not found


class TestUserEndpoint:
    """Tests for /api/v1/users/{username} endpoint."""

    def test_get_tweets_by_user_success(self, client, mock_tweet_service, mock_tweets):
        mock_tweet_service.get_tweets_by_user.return_value = mock_tweets

        response = client.get("/api/v1/users/twitter?limit=20")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["account"]["fullname"] == "Raymond Hettinger"
        mock_tweet_service.get_tweets_by_user.assert_called_once_with("twitter", 20)

    def test_get_tweets_by_user_default_limit(self, client, mock_tweet_service, mock_tweets):
        mock_tweet_service.get_tweets_by_user.return_value = mock_tweets

        response = client.get("/api/v1/users/twitter")

        assert response.status_code == 200
        assert len(response.json()) == 1
        mock_tweet_service.get_tweets_by_user.assert_called_once_with("twitter", 30)


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestRootEndpoint:
    def test_root(self, client):
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"

