"""FastAPI application factory."""

from fastapi import FastAPI

from app import __version__
from app.bootstrap.lifecycle import create_lifespan
from app.bootstrap.middleware import setup_middleware
from app.bootstrap.routes import setup_routes


def create_app() -> FastAPI:
    app = FastAPI(
        title="Twitter API Service",
        version=__version__,
        description="RESTful API for fetching tweets by hashtag and user",
        lifespan=create_lifespan(),
    )

    setup_middleware(app)
    setup_routes(app)

    return app

