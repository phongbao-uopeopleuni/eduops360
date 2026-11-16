"""Local, privacy-preserving HTTP observability primitives.

The application intentionally emits only an allowlisted request-completion event.
Metrics exporters, trace exporters, alert delivery and worker health require their
own approved operational configuration and are not implemented here.
"""

import json
import logging
from time import perf_counter

from fastapi import Request

HTTP_LOGGER = logging.getLogger("eduops.http")


class _UvicornPrivacyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # The application completion event replaces raw URL/IP access logging.
        if record.name == "uvicorn.access":
            return False
        if record.levelno >= logging.WARNING:
            record.msg = "ASGI runtime failure; consult sanitized request completion events."
            record.args = ()
            record.exc_info = None
            record.exc_text = None
            record.stack_info = None
        return True


def configure_runtime_log_privacy() -> None:
    """Protect Uvicorn destinations even when launched through its CLI/factory."""
    for name in ("uvicorn.access", "uvicorn.error"):
        logger = logging.getLogger(name)
        if not any(isinstance(item, _UvicornPrivacyFilter) for item in logger.filters):
            logger.addFilter(_UvicornPrivacyFilter())


def configure_http_logger() -> None:
    """Provide one local JSON destination without relying on root logger defaults."""
    HTTP_LOGGER.setLevel(logging.INFO)
    HTTP_LOGGER.propagate = False
    if not HTTP_LOGGER.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        HTTP_LOGGER.addHandler(handler)


configure_http_logger()


def request_route_label(request: Request) -> str:
    """Return a route template, never the raw path/query supplied by a client."""
    route = request.scope.get("route")
    route_path = getattr(route, "path", None)
    return route_path if isinstance(route_path, str) and route_path.startswith("/") else "unmatched"


def log_request_completed(
    request: Request,
    *,
    status_code: int,
    started_at: float,
) -> None:
    """Emit a sanitized completion event without allowing logging failures to break HTTP."""
    event = {
        "duration_ms": round((perf_counter() - started_at) * 1000, 3),
        "event": "http_request_completed",
        "method": request.method,
        "request_id": request.state.request_id,
        "route": request_route_label(request),
        "status_code": status_code,
    }
    try:
        HTTP_LOGGER.log(
            logging.ERROR if status_code >= 500 else logging.INFO,
            json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        )
    except Exception:  # pragma: no cover - logging handlers are external infrastructure.
        pass
