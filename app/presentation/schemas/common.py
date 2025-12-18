from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str


class ErrorResponse(BaseModel):
    error: str
    status_code: int
    detail: str | None = None

