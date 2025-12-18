from fastapi import FastAPI

from app import __version__
from app.presentation.api.v1 import hashtags, users
from app.presentation.schemas.common import HealthResponse


def setup_routes(app: FastAPI) -> None:
    app.include_router(hashtags.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health_check() -> HealthResponse:
        return HealthResponse(status="healthy", version=__version__)

    @app.get("/", tags=["root"])
    async def root() -> dict[str, str]:
        return {
            "message": "Twitter API Service",
            "version": __version__,
            "docs": "/docs",
            "health": "/health",
        }


