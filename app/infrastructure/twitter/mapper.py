from datetime import datetime
from typing import Any

from app.core.entities import Account, Tweet
from app.utils.logger import get_logger

logger = get_logger(__name__)


def map_tweet(tweet_data: dict[str, Any], includes: dict[str, Any]) -> Tweet | None:
    try:
        author_id = tweet_data.get("author_id")
        user_data = _find_user(author_id, includes)

        if not user_data:
            logger.warning("User not found: author_id=%s", author_id)
            return None

        account = Account(
            fullname=user_data.get("name", "Unknown"),
            href=f"/{user_data.get('username', 'unknown')}",
            id=int(user_data.get("id", 0))
        )

        metrics = tweet_data.get("public_metrics", {})
        created_at = tweet_data.get("created_at", "")

        return Tweet(
            account=account,
            date=_format_date(created_at),
            hashtags=_extract_hashtags(tweet_data),
            likes=metrics.get("like_count", 0),
            replies=metrics.get("reply_count", 0),
            retweets=metrics.get("retweet_count", 0),
            text=tweet_data.get("text", "")
        )

    except (ValueError, KeyError, TypeError) as e:
        logger.error("Tweet mapping error: %s (tweet_id=%s)", str(e), tweet_data.get("id"))
        return None


def _find_user(user_id: str | None, includes: dict[str, Any]) -> dict[str, Any] | None:
    if not user_id:
        return None

    users = includes.get("users", [])
    for user in users:
        if str(user.get("id")) == str(user_id):
            return user
    return None


def _extract_hashtags(tweet_data: dict[str, Any]) -> list[str]:
    entities = tweet_data.get("entities", {})
    hashtag_entities = entities.get("hashtags", [])
    return [f"#{ht.get('tag', '')}" for ht in hashtag_entities if ht.get("tag")]


def _format_date(iso_date: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
        formatted = dt.strftime("%I:%M %p - %-d %b %Y")
        if formatted[0] == "0":
            formatted = formatted[1:]
        return formatted
    except (ValueError, AttributeError):
        return iso_date
