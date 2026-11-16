from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.common.frontend import FrontendFiles
from app.common.observability import configure_runtime_log_privacy, log_request_completed
from app.common.preview import PreviewAccessMiddleware
from app.core.config import Settings
from app.core.errors import AppError, ErrorEnvelope, error_response
from app.db.connection import Database
from app.modules.auth.admin_router import catalog_router as admin_catalog_router
from app.modules.auth.admin_router import router as admin_auth_router
from app.modules.auth.rate_limit import LoginRateLimiter
from app.modules.auth.router import router as auth_router
from app.modules.health.router import router as health_router


def create_app(settings: Settings | None = None) -> FastAPI:
    configure_runtime_log_privacy()
    config = settings if settings is not None else Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        database = Database(config.database_url)
        app.state.database = database
        try:
            yield
        finally:
            await database.close()

    app = FastAPI(
        title="EduOps 360 API",
        version="0.1.0",
        description="Nền tảng local EduOps 360 — Phase 01.",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        responses={404: {"model": ErrorEnvelope}, 500: {"model": ErrorEnvelope}},
    )
    app.state.settings = config
    app.state.login_rate_limiter = LoginRateLimiter(
        limit=config.login_rate_limit_attempts,
        window_seconds=config.login_rate_limit_window_seconds,
    )
    app.state.login_ip_rate_limiter = LoginRateLimiter(
        limit=config.login_ip_rate_limit_attempts,
        window_seconds=config.login_rate_limit_window_seconds,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Accept", "Content-Type", "X-CSRF-Token"],
        expose_headers=["X-Request-ID"],
    )
    if config.environment == "staging":
        app.add_middleware(
            PreviewAccessMiddleware, access_key=config.preview_access_key.get_secret_value()
        )
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.allowed_hosts)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = str(uuid4())
        started_at = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            log_request_completed(request, status_code=500, started_at=started_at)
            raise
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Cache-Control"] = "no-store"
        log_request_completed(request, status_code=response.status_code, started_at=started_at)
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        if exc.status_code == 404:
            return error_response(
                request, 404, "NOT_FOUND", "Không tìm thấy tài nguyên.", headers=exc.headers
            )
        return error_response(
            request, exc.status_code, "HTTP_ERROR", "Yêu cầu không hợp lệ.", headers=exc.headers
        )

    @app.exception_handler(AppError)
    async def application_error(request: Request, exc: AppError):
        return error_response(
            request,
            exc.status_code,
            exc.code,
            exc.message,
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, _exc: RequestValidationError):
        return error_response(request, 422, "VALIDATION_ERROR", "Dữ liệu yêu cầu không hợp lệ.")

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, _exc: Exception):
        return error_response(request, 500, "INTERNAL_ERROR", "Có lỗi hệ thống. Vui lòng thử lại.")

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(admin_catalog_router, prefix="/api/v1")
    app.include_router(admin_auth_router, prefix="/api/v1")
    if config.frontend_directory is not None:
        app.mount("/", FrontendFiles(directory=config.frontend_directory, html=True))
    return app
