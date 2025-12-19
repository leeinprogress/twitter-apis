class TwitterAPIError(Exception):
    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class TwitterAuthenticationError(TwitterAPIError):
    def __init__(self, message: str = "Twitter authentication failed") -> None:
        super().__init__(message, status_code=401)


class TwitterRateLimitError(TwitterAPIError):
    def __init__(
        self,
        message: str = "Twitter API rate limit exceeded",
        reset_time: int | None = None
    ) -> None:
        self.reset_time = reset_time
        super().__init__(message, status_code=429)


class TwitterResourceNotFoundError(TwitterAPIError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class TwitterServiceUnavailableError(TwitterAPIError):
    def __init__(self, message: str = "Twitter service unavailable") -> None:
        super().__init__(message, status_code=503)


class CacheError(Exception):
    pass
