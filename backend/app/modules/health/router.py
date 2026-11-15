from datetime import UTC, datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.db.connection import Database

router = APIRouter(prefix="/health", tags=["Health"])


class LivenessResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["eduops360-api"] = "eduops360-api"
    version: str = "0.1.0"
    checked_at: datetime


class ReadinessResponse(BaseModel):
    status: Literal["ready", "unavailable"]
    database: Literal["ok", "unavailable"]
    checked_at: datetime


def get_database(request: Request) -> Database:
    return request.app.state.database


@router.get("/live", operation_id="get_liveness", response_model=LivenessResponse)
async def liveness() -> LivenessResponse:
    return LivenessResponse(checked_at=datetime.now(UTC))


@router.get(
    "/ready",
    operation_id="get_readiness",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse, "description": "PostgreSQL unavailable"}},
)
async def readiness(database: Annotated[Database, Depends(get_database)]):
    available = await database.ping()
    result = ReadinessResponse(
        status="ready" if available else "unavailable",
        database="ok" if available else "unavailable",
        checked_at=datetime.now(UTC),
    )
    return JSONResponse(
        status_code=200 if available else 503, content=result.model_dump(mode="json")
    )
