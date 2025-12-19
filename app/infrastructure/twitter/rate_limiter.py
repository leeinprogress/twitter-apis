import asyncio
import time
from collections import defaultdict

from app.core.exceptions import TwitterRateLimitError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    LIMITS = {
        "search_tweets": (12, 60),
        "get_user": (20, 60),
        "user_timeline": (100, 60),
    }

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    def _get_limits(self, key: str) -> tuple[int, int]:
        return self.LIMITS.get(key, (100, 60))

    async def acquire(self, key: str = "default") -> None:
        requests_per_window, window_seconds = self._get_limits(key)

        async with self._lock:
            now = time.time()
            bucket = self._buckets[key]

            cutoff = now - window_seconds
            self._buckets[key] = [ts for ts in bucket if ts > cutoff]

            if len(self._buckets[key]) >= requests_per_window:
                oldest = min(self._buckets[key])
                reset_time = int(oldest + window_seconds)
                wait_time = reset_time - now

                logger.warning(
                    "Rate limit exceeded for '%s': %d/%d requests. Reset in %.1fs",
                    key,
                    len(self._buckets[key]),
                    requests_per_window,
                    wait_time
                )

                raise TwitterRateLimitError(
                    f"Rate limit exceeded. Try again in {int(wait_time)} seconds."
                )

            self._buckets[key].append(now)
            logger.debug(
                "Rate limit acquired for '%s': %d/%d requests used",
                key,
                len(self._buckets[key]),
                requests_per_window
            )
