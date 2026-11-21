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


def test_redaction_is_recursive_depth_bounded_and_value_pattern_based():
    data = redact_log_fields(
        {
            "payload": {
                "nested": {
                    "authorization": "Basic abc",
                    "text": "Use Bearer secret-token",
                }
            },
            "trace": {"level": 1},
        }
    )
    assert data["payload"]["nested"]["authorization"] == "[REDACTED]"
    assert data["payload"]["nested"]["text"] == "[REDACTED]"


def test_redaction_hides_api_key_and_depth_limit():
    assert redact_log_fields({"api_key": "abc123"})["api_key"] == "[REDACTED]"
    assert redact_log_fields({"api-key": "abc123", "x-api-key": "def456"}) == {
        "api-key": "[REDACTED]",
        "x-api-key": "[REDACTED]",
    }
    nested = {"value": "visible"}
    for _ in range(22):
        nested = {"nested": nested}
    redacted = redact_log_fields(nested)
    for _ in range(20):
        redacted = redacted["nested"]
    assert "[DEPTH_LIMIT]" in str(redacted)
