from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.dependencies import get_db_session
from app.modules.audit_logs.service import bound_user_agent, write_audit_in_transaction
from app.modules.auth.constants import ActionType, ResourceType, SessionStatus, UserStatus
from app.modules.auth.guards import (
    can_delegate_role,
    load_principal,
    principal_covers_target,
)
from app.modules.auth.models import AccountToken, Session, User
from app.modules.auth.permissions import Scope
from app.modules.auth.schemas import (
    InvitationAccept,
    LoginRequest,
    LoginResponse,
    PasswordResetAccept,
    UserRead,
)
from app.modules.auth.services import (
    calculate_lockout_until,
    calculate_session_expiry,
    generate_session_token,
    hash_password,
    hash_password_async,
    hash_session_token,
    needs_rehash,
    should_lock_account,
    verify_password_async,
)
from app.modules.auth.session import (
    AuthContext,
    client_ip,
    get_auth_context,
    login_ip_rate_key,
    login_rate_key,
    matching_totp_step,
    require_csrf,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
_DUMMY_PASSWORD_HASH = hash_password("eduops-invalid-login-placeholder")


def _account_token_rate_key(request: Request) -> str:
    return login_rate_key(request, "account-token")


async def _consume_account_token(
    *,
    db: AsyncSession,
    raw_token: str,
    purpose: str,
    request: Request,
) -> tuple[AccountToken, User]:
    limiter = request.app.state.login_rate_limiter
    rate_key = _account_token_rate_key(request)
    retry_after = limiter.check(rate_key)
    if retry_after is not None:
        raise AppError(
            429,
            "ACCOUNT_TOKEN_RATE_LIMITED",
            "Quá nhiều lần thử mã tài khoản.",
            headers={"Retry-After": str(retry_after)},
        )

    token = (
        await db.execute(
            select(AccountToken).where(
                AccountToken.token_hash == hash_session_token(raw_token),
                AccountToken.purpose == purpose,
            )
        )
    ).scalar_one_or_none()
    now = datetime.now(UTC)
    if token is None or token.used_at is not None or token.expires_at <= now:
        limiter.record_failure(rate_key)
        raise AppError(400, "ACCOUNT_TOKEN_INVALID", "Mã tài khoản không hợp lệ.")
    user = (
        await db.execute(select(User).where(User.id == token.user_id).with_for_update())
    ).scalar_one_or_none()
    if user is None:
        limiter.record_failure(rate_key)
        raise AppError(400, "ACCOUNT_TOKEN_INVALID", "Mã tài khoản không hợp lệ.")
    # populate_existing: the unlocked read above cached this row in the identity map;
    # without a refresh, a concurrent consumer's committed used_at would be ignored.
    locked_token = (
        await db.execute(
            select(AccountToken)
            .where(AccountToken.id == token.id, AccountToken.purpose == purpose)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()
    now = datetime.now(UTC)
    if locked_token is None or locked_token.used_at is not None or locked_token.expires_at <= now:
        limiter.record_failure(rate_key)
        raise AppError(400, "ACCOUNT_TOKEN_INVALID", "Mã tài khoản không hợp lệ.")
    issue_action = {
        "invitation": ActionType.CREATE,
        "password_reset": ActionType.PASSWORD_RESET,
    }.get(purpose)
    issuer = await load_principal(db, locked_token.created_by)
    issuer_can_issue = issue_action is not None and can_delegate_role(
        issuer,
        [(ResourceType.USER, issue_action)],
        Scope(),
    )
    if not issuer_can_issue or not await principal_covers_target(db, issuer, user.id):
        limiter.record_failure(rate_key)
        raise AppError(400, "ACCOUNT_TOKEN_INVALID", "Mã tài khoản không hợp lệ.")
    return locked_token, user


def _set_session_cookies(
    response: Response,
    request: Request,
    session_token: str,
    csrf_token: str,
) -> None:
    settings = request.app.state.settings
    common = {
        "secure": settings.session_cookie_secure,
        "samesite": "strict",
        "path": "/",
        "max_age": 24 * 60 * 60,
    }
    response.set_cookie(
        settings.session_cookie_name,
        session_token,
        httponly=True,
        **common,
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        httponly=False,
        **common,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    email = str(payload.email).strip().lower()
    limiter = request.app.state.login_rate_limiter
    ip_limiter = request.app.state.login_ip_rate_limiter
    rate_key = login_rate_key(request, email)
    ip_rate_key = login_ip_rate_key(request)
    retry_after_values = [limiter.check(rate_key), ip_limiter.check(ip_rate_key)]
    retry_after = max((value for value in retry_after_values if value is not None), default=None)
    if retry_after is not None:
        raise AppError(
            429,
            "LOGIN_RATE_LIMITED",
            "Quá nhiều lần thử đăng nhập.",
            headers={"Retry-After": str(retry_after)},
        )

    result = await db.execute(select(User).where(func.lower(User.email) == email).with_for_update())
    user = result.scalar_one_or_none()
    password_ok = await verify_password_async(
        payload.password.get_secret_value(),
        user.password_hash if user is not None else _DUMMY_PASSWORD_HASH,
    )

    locked = user is None or user.status in {
        UserStatus.PENDING,
        UserStatus.SUSPENDED,
    }
    if user is not None and user.status == UserStatus.LOCKED:
        now = datetime.now(UTC)
        if user.locked_until is None or user.locked_until > now:
            locked = True
        else:
            user.status = UserStatus.ACTIVE
            user.locked_until = None
            user.failed_login_count = 0

    mfa_ok = True
    mfa_step: int | None = None
    if user is not None and user.mfa_enabled:
        if user.mfa_secret and payload.mfa_code:
            mfa_step = matching_totp_step(user.mfa_secret, payload.mfa_code)
        mfa_ok = mfa_step is not None and (
            user.mfa_last_used_step is None or mfa_step > user.mfa_last_used_step
        )

    if user is None or locked or not password_ok or not mfa_ok:
        limiter.record_failure(rate_key)
        ip_limiter.record_failure(ip_rate_key)
        if user is not None and not locked:
            user.failed_login_count += 1
            if should_lock_account(user.failed_login_count):
                user.status = UserStatus.LOCKED
                user.locked_until = calculate_lockout_until()
        await write_audit_in_transaction(
            db,
            action="session:login_failed",
            resource_type="session",
            actor_id=user.id if user is not None else None,
            actor_email=email,
            request_id=request.state.request_id,
            ip_address=client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
        await db.commit()
        raise AppError(401, "LOGIN_FAILED", "Thông tin đăng nhập không hợp lệ.")

    if needs_rehash(user.password_hash):
        user.password_hash = await hash_password_async(payload.password.get_secret_value())
    user.failed_login_count = 0
    user.locked_until = None
    if mfa_step is not None:
        user.mfa_last_used_step = mfa_step

    session_token = generate_session_token()
    csrf_token = secrets.token_urlsafe(32)
    expires_at = calculate_session_expiry()
    session = Session(
        user_id=user.id,
        token_hash=hash_session_token(session_token),
        csrf_token_hash=hashlib.sha256(csrf_token.encode()).hexdigest(),
        status=SessionStatus.ACTIVE,
        expires_at=expires_at,
        user_agent=bound_user_agent(request.headers.get("user-agent")),
        ip_address=client_ip(request),
    )
    db.add(session)
    await db.flush()
    await write_audit_in_transaction(
        db,
        action="session:login",
        resource_type="session",
        resource_id=str(session.id),
        actor_id=user.id,
        actor_email=user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        create_outbox=True,
    )
    await db.commit()
    limiter.reset(rate_key)
    _set_session_cookies(response, request, session_token, csrf_token)
    return LoginResponse(user=UserRead.model_validate(user), expires_at=expires_at)


@router.post("/invitations/accept", status_code=204)
async def accept_invitation(
    payload: InvitationAccept,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    raw_token = payload.token.get_secret_value()
    token, user = await _consume_account_token(
        db=db,
        raw_token=raw_token,
        purpose="invitation",
        request=request,
    )
    if user.status != UserStatus.PENDING:
        request.app.state.login_rate_limiter.record_failure(_account_token_rate_key(request))
        raise AppError(400, "ACCOUNT_TOKEN_INVALID", "Mã tài khoản không hợp lệ.")
    now = datetime.now(UTC)
    user.password_hash = await hash_password_async(payload.password.get_secret_value())
    user.password_changed_at = now
    user.status = UserStatus.ACTIVE
    user.failed_login_count = 0
    user.locked_until = None
    await db.execute(
        update(AccountToken)
        .where(
            AccountToken.user_id == user.id,
            AccountToken.purpose == "invitation",
            AccountToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    await write_audit_in_transaction(
        db,
        action="user:invitation_accept",
        resource_type="user",
        resource_id=str(user.id),
        actor_id=user.id,
        actor_email=user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        before_state={"status": str(UserStatus.PENDING)},
        after_state={"status": str(UserStatus.ACTIVE)},
        extra_data={"issued_by": str(token.created_by)},
        create_outbox=True,
    )
    await db.commit()
    request.app.state.login_rate_limiter.reset(_account_token_rate_key(request))


@router.post("/password-reset/accept", status_code=204)
async def accept_password_reset(
    payload: PasswordResetAccept,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    raw_token = payload.token.get_secret_value()
    token, user = await _consume_account_token(
        db=db,
        raw_token=raw_token,
        purpose="password_reset",
        request=request,
    )
    if user.status == UserStatus.PENDING:
        request.app.state.login_rate_limiter.record_failure(_account_token_rate_key(request))
        raise AppError(400, "ACCOUNT_TOKEN_INVALID", "Mã tài khoản không hợp lệ.")
    now = datetime.now(UTC)
    before_status = user.status
    user.password_hash = await hash_password_async(payload.new_password.get_secret_value())
    user.password_changed_at = now
    user.failed_login_count = 0
    user.locked_until = None
    if user.status == UserStatus.LOCKED:
        user.status = UserStatus.ACTIVE
    await db.execute(
        update(AccountToken)
        .where(
            AccountToken.user_id == user.id,
            AccountToken.purpose == "password_reset",
            AccountToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    await db.execute(
        update(Session)
        .where(Session.user_id == user.id, Session.status == SessionStatus.ACTIVE)
        .values(status=SessionStatus.REVOKED, revoked_at=now)
    )
    await write_audit_in_transaction(
        db,
        action="user:password_reset_accept",
        resource_type="user",
        resource_id=str(user.id),
        actor_id=user.id,
        actor_email=user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        before_state={"status": str(before_status)},
        after_state={"status": str(user.status), "sessions_revoked": True},
        # The holder of the reset capability is not authenticated; record who issued it.
        extra_data={"issued_by": str(token.created_by)},
        create_outbox=True,
    )
    await db.commit()
    request.app.state.login_rate_limiter.reset(_account_token_rate_key(request))


@router.get("/me", response_model=UserRead)
async def get_current_user(
    auth: Annotated[AuthContext, Depends(get_auth_context)],
) -> UserRead:
    return UserRead.model_validate(auth.user)


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    auth: Annotated[AuthContext, Depends(require_csrf)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    auth.session.status = SessionStatus.REVOKED
    auth.session.revoked_at = datetime.now(UTC)
    await write_audit_in_transaction(
        db,
        action="session:logout",
        resource_type="session",
        resource_id=str(auth.session.id),
        actor_id=auth.user.id,
        actor_email=auth.user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        create_outbox=True,
    )
    await db.commit()
    settings = request.app.state.settings
    response.delete_cookie(
        settings.session_cookie_name,
        path="/",
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="strict",
    )
    response.delete_cookie(
        settings.csrf_cookie_name,
        path="/",
        secure=settings.session_cookie_secure,
        httponly=False,
        samesite="strict",
    )
