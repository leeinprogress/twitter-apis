from fastapi import FastAPI

from app import __version__
from app.bootstrap.routes import setup_routes

# Create FastAPI app
app = FastAPI(
    title="Twitter API Service",
    version=__version__,
    description="RESTful API for fetching tweets by hashtag and user",
)

# Setup routes
setup_routes(app)

if __name__ == "__main__":
    import uvicorn

    from app.bootstrap.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
