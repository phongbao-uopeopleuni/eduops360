import re
from pathlib import Path
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="EDUOPS_", env_file=".env", extra="ignore", hide_input_in_errors=True
    )

    environment: Literal["local", "test", "staging"] = "local"
    database_url: SecretStr | None = None
    cors_origins: list[str] = ["http://127.0.0.1:5173", "http://localhost:5173"]
    session_cookie_name: str = "eduops_session"
    csrf_cookie_name: str = "eduops_csrf"
    session_cookie_secure: bool = True
    allowed_hosts: list[str] = []
    frontend_directory: Path | None = None
    preview_access_key: SecretStr | None = None
    login_rate_limit_attempts: int = 10
    # TẠM pending Security Owner: failed attempts across all identities from one peer.
    login_ip_rate_limit_attempts: int = 50
    login_rate_limit_window_seconds: int = 60
    # TẠM pending Security Owner: authenticated inactivity before session expiry.
    session_idle_timeout_minutes: int = 30

    @model_validator(mode="after")
    def validate_staging(self):
        if self.environment != "staging":
            return self
        if self.database_url is None or not self.session_cookie_secure:
            raise ValueError("Staging requires a database and secure session cookies")
        if make_url(self.database_url.get_secret_value()).username != "eduops_runtime":
            raise ValueError("Staging web must use the restricted eduops_runtime database role")
        if not self.allowed_hosts or any(
            not re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?", host) or "." not in host
            for host in self.allowed_hosts
        ):
            raise ValueError("Staging requires exact fully qualified allowed hosts")
        if any(not origin.startswith("https://") for origin in self.cors_origins):
            raise ValueError("Staging CORS origins must use HTTPS")
        if self.preview_access_key is None or len(self.preview_access_key.get_secret_value()) < 32:
            raise ValueError(
                "Staging requires a random preview access key of at least 32 characters"
            )
        return self

    @field_validator("cors_origins")
    @classmethod
    def reject_wildcard_cors(cls, value: list[str]) -> list[str]:
        if any(origin.strip() == "*" for origin in value):
            raise ValueError("Wildcard CORS is not allowed with credentialed sessions")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr | None) -> SecretStr | None:
        if value is None:
            return None
        try:
            url = make_url(value.get_secret_value())
            if url.drivername != "postgresql+psycopg" or not url.host or not url.database:
                raise ValueError
        except (ArgumentError, ValueError):
            raise ValueError(
                "Use a PostgreSQL psycopg connection URL with host and database"
            ) from None
        return value
