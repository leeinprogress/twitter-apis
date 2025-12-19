from app.bootstrap.app_factory import create_app
from app.bootstrap.config import get_settings
from app.utils.logger import configure_logging

configure_logging()

app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
