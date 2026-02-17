from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app import __version__
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_lifespan() -> Any:
    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
        logger.info(f"Application starting (version: {__version__})")
        yield
        logger.info("Application shutting down")

        global _http_client, _cache_service

        if _http_client:
            await _http_client.aclose()
            logger.info("HTTP client closed")

        if _cache_service:
            await _cache_service.close()
            logger.info("Cache service closed")

    return lifespan

