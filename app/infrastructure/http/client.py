import httpx

from app.bootstrap.config import Settings


def create_http_client(settings: Settings) -> httpx.AsyncClient:
    limits = httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30.0,
    )

    timeout = httpx.Timeout(
        connect=5.0,
        read=settings.twitter_request_timeout,
        write=settings.twitter_request_timeout,
        pool=5.0,
    )

    return httpx.AsyncClient(
        limits=limits,
        timeout=timeout,
        follow_redirects=True,
    )

