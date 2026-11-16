import json
import logging

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def app():
    return create_app(Settings(database_url=None, environment="test", _env_file=None))


def request_events(caplog):
    return [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "eduops.http" and record.message.startswith("{")
    ]


def test_request_log_correlates_response_without_recording_query_or_credentials(app, caplog):
    credential = "Bearer synthetic-private-value"
    with caplog.at_level(logging.INFO, logger="eduops.http"):
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/health/live?token=synthetic-private-value",
                headers={"Authorization": credential, "X-Request-ID": "untrusted-value"},
            )

    events = request_events(caplog)
    assert response.status_code == 200
    assert response.headers["x-request-id"] != "untrusted-value"
    assert events == [
        {
            "duration_ms": pytest.approx(events[0]["duration_ms"]),
            "event": "http_request_completed",
            "method": "GET",
            "request_id": response.headers["x-request-id"],
            "route": "/health/live",
            "status_code": 200,
        }
    ]
    serialized = json.dumps(events)
    assert "token=" not in serialized
    assert credential not in serialized
    assert "synthetic-private-value" not in serialized


def test_internal_error_is_logged_without_exception_details(app, caplog):
    @app.get("/test-observability-error", include_in_schema=False)
    async def fail():
        raise RuntimeError("private database connection detail")

    with caplog.at_level(logging.ERROR, logger="eduops.http"):
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/test-observability-error")

    events = request_events(caplog)
    assert response.status_code == 500
    assert events[0]["event"] == "http_request_completed"
    assert events[0]["status_code"] == 500
    assert events[0]["request_id"] == response.headers["x-request-id"]
    assert "private database connection detail" not in json.dumps(events)
