import asyncio
import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.common.temporal import as_utc, parse_calendar_date
from app.core.config import Settings
from app.core.event_loop import create_event_loop
from app.main import create_app
from app.modules.health.router import get_database

ROOT = Path(__file__).resolve().parents[2]


class DatabaseStub:
    def __init__(self, available):
        self.available = available

    async def ping(self):
        return self.available


@pytest.fixture
def app():
    return create_app(Settings(database_url=None, environment="test", _env_file=None))


def test_liveness_is_independent_of_database(app):
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "eduops360-api"
    assert datetime.fromisoformat(response.json()["checked_at"]).utcoffset() == timedelta(0)
    assert response.headers["x-request-id"]
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "available,status,expected", [(True, 200, "ready"), (False, 503, "unavailable")]
)
def test_readiness_reports_actual_database_state(app, available, status, expected):
    app.dependency_overrides[get_database] = lambda: DatabaseStub(available)
    with TestClient(app) as client:
        response = client.get("/api/v1/health/ready")
    assert response.status_code == status
    assert response.json()["status"] == expected


def test_unconfigured_database_is_not_ready(app):
    with TestClient(app) as client:
        response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["database"] == "unavailable"


def test_database_failure_returns_safe_unavailable_result():
    from app.db.connection import Database

    database = Database(None)
    assert asyncio.run(database.ping()) is False


def test_unknown_route_has_localized_error_and_request_id(app):
    with TestClient(app) as client:
        response = client.get("/api/v1/students")
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert error["message"] == "Không tìm thấy tài nguyên."
    assert error["request_id"] == response.headers["x-request-id"]


def test_method_not_allowed_preserves_allow_header(app):
    with TestClient(app) as client:
        response = client.post("/api/v1/health/live")
    assert response.status_code == 405
    assert response.headers["allow"] == "GET"


@pytest.mark.parametrize(
    "status,headers", [(401, {"WWW-Authenticate": "Bearer"}), (429, {"Retry-After": "60"})]
)
def test_http_error_preserves_protocol_headers(app, status, headers):
    from fastapi import HTTPException

    @app.get("/test-http-error", include_in_schema=False)
    async def fail():
        raise HTTPException(status_code=status, headers=headers)

    with TestClient(app) as client:
        response = client.get("/test-http-error")
    assert response.status_code == status
    for name, value in headers.items():
        assert response.headers[name] == value
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_sensitive_database_url_is_hidden():
    settings = Settings(
        database_url="postgresql+psycopg://user:secret@localhost/db", _env_file=None
    )
    assert "secret" not in repr(settings)
    with pytest.raises(ValidationError) as error:
        Settings(database_url="sqlite:///secret.db", _env_file=None)
    assert "secret.db" not in str(error.value)


def test_unexpected_error_has_safe_response(app):
    @app.get("/test-error", include_in_schema=False)
    async def fail():
        raise RuntimeError("private connection details")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test-error")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "private connection" not in response.text


def test_cors_only_allows_configured_local_origins(app):
    with TestClient(app) as client:
        allowed = client.get("/api/v1/health/live", headers={"Origin": "http://127.0.0.1:5173"})
        denied = client.get("/api/v1/health/live", headers={"Origin": "https://external.invalid"})
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert "access-control-allow-origin" not in denied.headers


def test_credentialed_cors_rejects_wildcard_origin():
    with pytest.raises(ValidationError):
        Settings(cors_origins=["*"], _env_file=None)


def test_openapi_matches_checked_in_contract(app):
    expected = json.loads((ROOT / "contracts/openapi.json").read_text(encoding="utf-8"))
    assert app.openapi() == expected
    operation = expected["paths"]["/api/v1/health/ready"]["get"]
    assert {"200", "503"} <= operation["responses"].keys()


@pytest.mark.parametrize("value", ["2024-02-29", "2026-11-12"])
def test_calendar_date_roundtrip(value):
    assert parse_calendar_date(value).isoformat() == value


@pytest.mark.parametrize("value", ["2026-02-29", "20261112", "2026-11-12T00:00:00Z", ""])
def test_invalid_calendar_dates_rejected(value):
    with pytest.raises(ValueError):
        parse_calendar_date(value)


def test_utc_conversion_requires_offset_and_preserves_instant():
    local = datetime(2026, 11, 12, 0, 0, tzinfo=timezone(timedelta(hours=7)))
    assert as_utc(local) == datetime(2026, 11, 11, 17, 0, tzinfo=UTC)
    with pytest.raises(ValueError):
        as_utc(datetime(2026, 11, 12))


def test_native_event_loop_supports_psycopg_async():
    loop = create_event_loop()
    try:
        assert isinstance(loop, asyncio.SelectorEventLoop)
    finally:
        loop.close()
