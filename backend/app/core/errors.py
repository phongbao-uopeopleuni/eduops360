from collections.abc import Mapping
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class AppError(Exception):
    """Expected API failure with a stable, non-sensitive error envelope."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.headers = headers


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str
    details: list[dict[str, str]] = Field(default_factory=list)


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


def error_response(
    request: Request,
    status: int,
    code: str,
    message: str,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    body = ErrorEnvelope(error=ErrorDetail(code=code, message=message, request_id=request_id))
    response = JSONResponse(
        status_code=status,
        content=body.model_dump(),
        headers=headers,
    )
    response.headers.update({"X-Request-ID": request_id, "Cache-Control": "no-store"})
    return response
