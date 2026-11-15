from app.modules.audit_logs.service import sanitize_audit_data


def test_audit_data_redacts_nested_credentials() -> None:
    value = {
        "email": "synthetic@example.com",
        "password_hash": "must-not-leak",
        "nested": {
            "csrf-token": "must-not-leak",
            "Authorization": "Bearer must-not-leak",
            "safe": ["value", {"mfa_secret": "must-not-leak"}],
        },
    }
    assert sanitize_audit_data(value) == {
        "email": "synthetic@example.com",
        "password_hash": "[REDACTED]",
        "nested": {
            "csrf-token": "[REDACTED]",
            "Authorization": "[REDACTED]",
            "safe": ["value", {"mfa_secret": "[REDACTED]"}],
        },
    }


def test_audit_data_bounds_collection_and_depth() -> None:
    assert len(sanitize_audit_data(list(range(200)))) == 100
    nested = {}
    current = nested
    for _ in range(9):
        current["level"] = {}
        current = current["level"]
    assert "[TRUNCATED]" in str(sanitize_audit_data(nested))
