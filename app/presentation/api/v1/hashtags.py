from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from app.application.services import TweetService
from app.presentation.api.dependencies import get_tweet_service
from app.presentation.schemas.tweet import TweetSchema

router = APIRouter(prefix="/hashtags", tags=["hashtags"])


@router.get("/{hashtag}", response_model=list[TweetSchema])
async def get_tweets_by_hashtag(
    hashtag: Annotated[str, Path(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=100)] = 30,
    tweet_service: TweetService = Depends(get_tweet_service),
) -> list[TweetSchema]:
    tweets = await tweet_service.get_tweets_by_hashtag(hashtag, limit)
    return [TweetSchema.from_entity(tweet) for tweet in tweets]


