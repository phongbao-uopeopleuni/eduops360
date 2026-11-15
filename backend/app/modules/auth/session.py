from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.dependencies import get_db_session
from app.modules.auth.constants import SessionStatus, UserStatus
from app.modules.auth.models import Session, User
from app.modules.auth.services import hash_session_token


@dataclass(frozen=True)
class AuthContext:
    user: User
    session: Session


def client_ip(request: Request) -> str | None:
    """Use the direct peer only; proxy trust must be configured explicitly later."""
    return request.client.host if request.client is not None else None


def login_rate_key(request: Request, email: str) -> str:
    identity = f"{client_ip(request) or 'unknown'}\0{email.strip().lower()}"
    return hashlib.sha256(identity.encode()).hexdigest()


def login_ip_rate_key(request: Request) -> str:
    identity = f"ip\0{client_ip(request) or 'unknown'}"
    return hashlib.sha256(identity.encode()).hexdigest()


def matching_totp_step(secret: str, code: str, *, now: int | None = None) -> int | None:
    """Return the matching RFC 6238 step, or None, with one-step clock tolerance."""
    if len(code) != 6 or not code.isdigit():
        return None
    try:
        normalized = secret.strip().replace(" ", "").upper()
        padding = "=" * ((8 - len(normalized) % 8) % 8)
        key = base64.b32decode(normalized + padding, casefold=True)
    except (ValueError, base64.binascii.Error):
        return None
    current = int(time.time() if now is None else now) // 30
    for counter in range(current - 1, current + 2):
        digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
        offset = digest[-1] & 0x0F
        value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
        expected = f"{value % 1_000_000:06d}"
        if hmac.compare_digest(expected, code):
            return counter
    return None


def verify_totp(secret: str, code: str, *, now: int | None = None) -> bool:
    """Verify a six-digit RFC 6238 SHA-1 TOTP with one-step clock tolerance."""
    return matching_totp_step(secret, code, now=now) is not None


async def get_auth_context(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthContext:
    settings = request.app.state.settings
    raw_token = request.cookies.get(settings.session_cookie_name)
    if not raw_token:
        raise AppError(401, "AUTH_REQUIRED", "Cần đăng nhập để tiếp tục.")

    result = await db.execute(
        select(Session, User)
        .join(User, User.id == Session.user_id)
        .where(Session.token_hash == hash_session_token(raw_token))
    )
    row = result.first()
    if row is None:
        raise AppError(401, "INVALID_SESSION", "Phiên đăng nhập không hợp lệ.")
    session, user = row
    now = datetime.now(UTC)
    idle_cutoff = now - timedelta(minutes=settings.session_idle_timeout_minutes)
    if (
        session.status != SessionStatus.ACTIVE
        or session.expires_at <= now
        or session.last_activity_at <= idle_cutoff
    ):
        if session.status == SessionStatus.ACTIVE:
            session.status = SessionStatus.EXPIRED
            await db.commit()
        raise AppError(401, "INVALID_SESSION", "Phiên đăng nhập không hợp lệ.")
    # A0102-F05 — TẠM, chờ Security Owner chốt chính sách lockout: khóa do đăng nhập sai
    # chỉ chặn đăng nhập mới (kiểm ở /auth/login), không để người chưa đăng nhập chấm dứt
    # phiên hợp lệ đang có. Đình chỉ tự thu hồi phiên; tài khoản pending không có phiên.
    if user.status not in {UserStatus.ACTIVE, UserStatus.LOCKED}:
        raise AppError(401, "ACCOUNT_UNAVAILABLE", "Tài khoản không khả dụng.")

    session.last_activity_at = now
    await db.commit()
    return AuthContext(user=user, session=session)


async def require_csrf(
    request: Request,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
) -> AuthContext:
    settings = request.app.state.settings
    header_token = request.headers.get("X-CSRF-Token")
    cookie_token = request.cookies.get(settings.csrf_cookie_name)
    if not header_token or not cookie_token:
        raise AppError(403, "CSRF_REQUIRED", "Thiếu mã bảo vệ CSRF.")
    if not hmac.compare_digest(header_token, cookie_token):
        raise AppError(403, "CSRF_INVALID", "Mã bảo vệ CSRF không hợp lệ.")
    expected_hash = auth.session.csrf_token_hash
    if expected_hash is None or not hmac.compare_digest(
        hashlib.sha256(header_token.encode()).hexdigest(), expected_hash
    ):
        raise AppError(403, "CSRF_INVALID", "Mã bảo vệ CSRF không hợp lệ.")
    return auth
