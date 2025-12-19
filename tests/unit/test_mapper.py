
from app.infrastructure.twitter.mapper import (
    _format_date,
    map_tweet,
)


class TestMapTweet:
    def test_map_tweet_success(self):
        tweet_data = {
            "id": "1234567890",
            "author_id": "987654321",
            "text": "This is a test tweet #python #testing",
            "created_at": "2018-03-07T12:57:00.000Z",
            "public_metrics": {
                "like_count": 42,
                "reply_count": 5,
                "retweet_count": 10,
            },
            "entities": {
                "hashtags": [
                    {"tag": "python"},
                    {"tag": "testing"}
                ]
            }
        }

        includes = {
            "users": [
                {
                    "id": "987654321",
                    "username": "testuser",
                    "name": "Test User"
                }
            ]
        }

        tweet = map_tweet(tweet_data, includes)

        assert tweet is not None
        assert tweet.text == "This is a test tweet #python #testing"
        assert tweet.likes == 42
        assert tweet.replies == 5
        assert tweet.retweets == 10
        assert tweet.hashtags == ["#python", "#testing"]
        assert tweet.account.fullname == "Test User"
        assert tweet.account.href == "/testuser"
        assert tweet.account.id == 987654321
        assert tweet.date == "12:57 PM - 7 Mar 2018"

    def test_map_tweet_missing_author_id(self):
        tweet_data = {
            "id": "1234567890",
            "text": "Tweet without author",
            "created_at": "2018-03-07T12:57:00.000Z",
        }

        includes = {"users": []}

        tweet = map_tweet(tweet_data, includes)

        assert tweet is None

    def test_map_tweet_user_not_found(self):
        tweet_data = {
            "id": "1234567890",
            "author_id": "999999999",
            "text": "Tweet with missing user",
            "created_at": "2018-03-07T12:57:00.000Z",
        }

        includes = {
            "users": [
                {
                    "id": "987654321",
                    "username": "testuser",
                    "name": "Test User"
                }
            ]
        }

        tweet = map_tweet(tweet_data, includes)

        assert tweet is None

    def test_map_tweet_missing_text(self):
        tweet_data = {
            "id": "1234567890",
            "author_id": "987654321",
            "created_at": "2018-03-07T12:57:00.000Z",
        }

        includes = {
            "users": [
                {
                    "id": "987654321",
                    "username": "testuser",
                    "name": "Test User"
                }
            ]
        }

        tweet = map_tweet(tweet_data, includes)

        assert tweet is not None
        assert tweet.text == ""

    def test_map_tweet_missing_metrics(self):
        tweet_data = {
            "id": "1234567890",
            "author_id": "987654321",
            "text": "Tweet without metrics",
            "created_at": "2018-03-07T12:57:00.000Z",
        }

        includes = {
            "users": [
                {
                    "id": "987654321",
                    "username": "testuser",
                    "name": "Test User"
                }
            ]
        }

        tweet = map_tweet(tweet_data, includes)

        assert tweet is not None
        assert tweet.likes == 0
        assert tweet.replies == 0
        assert tweet.retweets == 0

    def test_map_tweet_invalid_created_at(self):
        tweet_data = {
            "id": "1234567890",
            "author_id": "987654321",
            "text": "Tweet with invalid date",
            "created_at": "invalid-date-format",
        }

        includes = {
            "users": [
                {
                    "id": "987654321",
                    "username": "testuser",
                    "name": "Test User"
                }
            ]
        }

        tweet = map_tweet(tweet_data, includes)

        assert tweet is not None
        assert tweet.date == "invalid-date-format"

    def test_map_tweet_missing_created_at(self):
        tweet_data = {
            "id": "1234567890",
            "author_id": "987654321",
            "text": "Tweet without date",
        }

        includes = {
            "users": [
                {
                    "id": "987654321",
                    "username": "testuser",
                    "name": "Test User"
                }
            ]
        }

        tweet = map_tweet(tweet_data, includes)

        assert tweet is not None
        assert tweet.date == ""

    def test_map_tweet_empty_entities(self):
        tweet_data = {
            "id": "1234567890",
            "author_id": "987654321",
            "text": "Tweet without hashtags",
            "created_at": "2018-03-07T12:57:00.000Z",
            "entities": {}
        }

        includes = {
            "users": [
                {
                    "id": "987654321",
                    "username": "testuser",
                    "name": "Test User"
                }
            ]
        }

        tweet = map_tweet(tweet_data, includes)

        assert tweet is not None
        assert tweet.hashtags == []

    def test_map_tweet_no_entities(self):
        tweet_data = {
            "id": "1234567890",
            "author_id": "987654321",
            "text": "Tweet without entities field",
            "created_at": "2018-03-07T12:57:00.000Z",
        }

        includes = {
            "users": [
                {
                    "id": "987654321",
                    "username": "testuser",
                    "name": "Test User"
                }
            ]
        }

        tweet = map_tweet(tweet_data, includes)

        assert tweet is not None
        assert tweet.hashtags == []


class TestFormatDate:
    def test_format_date_success(self):
        iso_date = "2018-03-07T12:57:00.000Z"

        formatted = _format_date(iso_date)

        assert formatted == "12:57 PM - 7 Mar 2018"

    def test_format_date_with_leading_zero(self):
        iso_date = "2018-03-07T09:30:00.000Z"

        formatted = _format_date(iso_date)

        assert formatted == "9:30 AM - 7 Mar 2018"

    def test_format_date_invalid_format(self):
        iso_date = "invalid-date"

        formatted = _format_date(iso_date)

        assert formatted == "invalid-date"

    def test_format_date_empty_string(self):
        iso_date = ""

        formatted = _format_date(iso_date)

        assert formatted == ""

