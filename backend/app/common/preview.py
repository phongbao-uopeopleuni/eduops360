"""Access gate for synthetic online previews; never a replacement for app IAM."""

import base64
import hashlib
import hmac

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.errors import error_response


class PreviewAccessMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, access_key: str):
        super().__init__(app)
        self.expected = hashlib.sha256(f"preview:{access_key}".encode()).digest()

    async def dispatch(self, request: Request, call_next):
        if request.method == "GET" and request.url.path in {
            "/api/v1/health/live",
            "/api/v1/health/ready",
        }:
            return await call_next(request)
        header = request.headers.get("authorization", "")
        try:
            scheme, encoded = header.split(" ", 1)
            if scheme.lower() != "basic" or len(encoded) > 1024:
                raise ValueError
            supplied = base64.b64decode(encoded, validate=True)
            allowed = hmac.compare_digest(hashlib.sha256(supplied).digest(), self.expected)
        except (ValueError, base64.binascii.Error):
            allowed = False
        if not allowed:
            return error_response(
                request,
                401,
                "PREVIEW_AUTH_REQUIRED",
                "Bản thử nghiệm yêu cầu quyền truy cập.",
                headers={
                    "WWW-Authenticate": 'Basic realm="EduOps synthetic preview", charset="UTF-8"'
                },
            )
        return await call_next(request)
