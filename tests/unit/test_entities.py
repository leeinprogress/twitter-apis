import pytest

from app.core.entities import Account, Tweet


class TestAccount:
    def test_create_account(self):
        account = Account(fullname="Test User", href="/testuser", id=123)

        assert account.fullname == "Test User"
        assert account.href == "/testuser"
        assert account.id == 123

    def test_account_is_immutable(self):
        account = Account(fullname="Test User", href="/testuser", id=123)

        with pytest.raises(AttributeError):
            account.fullname = "New Name"  # type: ignore


class TestTweet:
    def test_create_tweet(self):
        account = Account(fullname="Test User", href="/testuser", id=123)
        tweet = Tweet(
            account=account,
            date="12:00 PM - 1 Jan 2024",
            hashtags=["#test"],
            likes=10,
            replies=5,
            retweets=3,
            text="Test tweet",
        )

        assert tweet.account == account
        assert tweet.text == "Test tweet"
        assert tweet.likes == 10
        assert tweet.hashtags == ["#test"]

    def test_tweet_is_immutable(self):
        account = Account(fullname="Test User", href="/testuser", id=123)
        tweet = Tweet(
            account=account,
            date="12:00 PM - 1 Jan 2024",
            hashtags=["#test"],
            likes=10,
            replies=5,
            retweets=3,
            text="Test tweet",
        )

        with pytest.raises(AttributeError):
            tweet.text = "Modified"  # type: ignore

