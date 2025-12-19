import logging
import sys

from app.bootstrap.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    if settings.log_format == "json":
        log_format = '{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'
    else:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        format=log_format,
        level=log_level,
        stream=sys.stdout,
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

