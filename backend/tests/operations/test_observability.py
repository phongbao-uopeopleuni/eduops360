from app.modules.operations.observability import redact_log_fields


def test_redaction_removes_credentials_and_preserves_correlation_fields():
    data = redact_log_fields(
        {
            "request_id": "req-1",
            "authorization": "Bearer secret",
            "password": "hidden",
            "event": "login",
        }
    )
    assert data["request_id"] == "req-1"
    assert data["authorization"] == "[REDACTED]"
    assert data["password"] == "[REDACTED]"
    assert data["event"] == "login"
