import logging
from typing import Any

SENSITIVE_PARTS = frozenset({"authorization", "cookie", "password", "secret", "token"})


def redact_log_fields(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: "[REDACTED]" if any(part in key.lower() for part in SENSITIVE_PARTS) else item
        for key, item in value.items()
    }


def configure_redacting_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
