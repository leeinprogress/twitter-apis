from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import TwitterAPIError
from app.presentation.schemas.common import ErrorResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def twitter_api_error_handler(request: Request, exc: TwitterAPIError) -> JSONResponse:
    logger.error(
        "twitter_api_error",
        path=request.url.path,
        error=exc.message,
        status_code=exc.status_code,
    )

    error_response = ErrorResponse(
        error=exc.__class__.__name__,
        status_code=exc.status_code,
        detail=exc.message,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_type=type(exc).__name__,
    )

    error_response = ErrorResponse(
        error="InternalServerError",
        status_code=500,
        detail="An unexpected error occurred",
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(),
    )

