import logging
from typing import Any

SENSITIVE_PARTS = frozenset(
    {"authorization", "cookie", "password", "secret", "token", "api_key", "apikey"}
)
SENSITIVE_VALUE_PATTERNS = ("bearer ", "basic ", "sk-", "api_key=", "apikey:")


def _redact(value: Any, depth: int = 0) -> Any:
    if depth >= 20:
        return "[DEPTH_LIMIT]"
    if isinstance(value, dict):
        return {
            str(key): "[REDACTED]"
            if any(
                part in str(key).lower().replace("-", "_").replace(" ", "_")
                for part in SENSITIVE_PARTS
            )
            else _redact(item, depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(item, depth + 1) for item in value]
    if isinstance(value, str):
        lowered = value.lower()
        if any(pattern in lowered for pattern in SENSITIVE_VALUE_PATTERNS):
            return "[REDACTED]"
    return value


def redact_log_fields(value: dict[str, Any]) -> dict[str, Any]:
    return _redact(value)


def configure_redacting_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
