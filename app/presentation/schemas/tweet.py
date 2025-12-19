from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.core.entities import Tweet


class AccountSchema(BaseModel):
    fullname: str
    href: str
    id: int


class TweetSchema(BaseModel):
    account: AccountSchema
    date: str
    hashtags: list[str]
    likes: int = Field(ge=0)
    replies: int = Field(ge=0)
    retweets: int = Field(ge=0)
    text: str

    @classmethod
    def from_entity(cls, tweet: Tweet) -> TweetSchema:
        return cls(
            account=AccountSchema(
                fullname=tweet.account.fullname,
                href=tweet.account.href,
                id=tweet.account.id,
            ),
            date=tweet.date,
            hashtags=tweet.hashtags,
            likes=tweet.likes,
            replies=tweet.replies,
            retweets=tweet.retweets,
            text=tweet.text,
        )
