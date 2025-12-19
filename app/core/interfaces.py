from abc import ABC, abstractmethod

from app.core.entities import Tweet


class TweetRepository(ABC):
    @abstractmethod
    async def get_tweets_by_hashtag(self, hashtag: str, limit: int = 30) -> list[Tweet]:
        pass

    @abstractmethod
    async def get_tweets_by_user(self, username: str, limit: int = 30) -> list[Tweet]:
        pass


class CacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> list[Tweet] | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: list[Tweet], ttl: int) -> None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        pass

