from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.dependencies import get_db_session
from app.modules.audit_logs.service import write_audit_in_transaction
from app.modules.auth.constants import ActionType, ResourceType, SessionStatus, UserStatus
from app.modules.auth.guards import (
    AuthorizationContext,
    can_delegate_role,
    enforce_permission,
    get_csrf_authorization_context,
    grant_row_scope,
    load_unexpired_grant_permissions,
    principal_covers_target,
    require_permission,
)
from app.modules.auth.models import (
    AccountToken,
    Permission,
    Role,
    RolePermission,
    Session,
    User,
    UserRole,
)
from app.modules.auth.permissions import Scope
from app.modules.auth.schemas import (
    AccountTokenIssue,
    InvitationReissue,
    PasswordResetIssue,
    RoleRead,
    UserInvitationCreate,
    UserRead,
    UserRoleAssign,
    UserRoleRead,
    UserRoleRevoke,
    UserStatusUpdate,
)
from app.modules.auth.services import (
    generate_session_token,
    hash_password_async,
    hash_session_token,
)
from app.modules.auth.session import client_ip

router = APIRouter(prefix="/admin/users", tags=["User Administration"])
catalog_router = APIRouter(prefix="/admin", tags=["User Administration"])

CreateUserGuard = Annotated[
    AuthorizationContext,
    Depends(
        require_permission(
            ResourceType.USER,
            ActionType.CREATE,
            csrf_protected=True,
        )
    ),
]
ReadUserGuard = Annotated[
    AuthorizationContext,
    Depends(require_permission(ResourceType.USER, ActionType.READ)),
]
PasswordResetGuard = Annotated[
    AuthorizationContext,
    Depends(
        require_permission(
            ResourceType.USER,
            ActionType.PASSWORD_RESET,
            csrf_protected=True,
        )
    ),
]
AuthzContext = Annotated[
    AuthorizationContext,
    Depends(get_csrf_authorization_context),
]
DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


@catalog_router.get("/roles", response_model=list[RoleRead])
async def list_roles(
    _context: ReadUserGuard,
    db: DatabaseSession,
) -> list[RoleRead]:
    roles = (await db.execute(select(Role).order_by(Role.name_vi))).scalars().all()
    return [RoleRead.model_validate(role) for role in roles]


def _scope_from_assignment(payload: UserRoleAssign | UserRole) -> Scope:
    return Scope(
        school_id=payload.school_id,
        academic_year_id=payload.academic_year_id,
        grade_id=payload.grade_id,
        class_id=payload.class_id,
        subject_id=payload.subject_id,
    )


def _require_explicit_scope(payload: UserRoleAssign) -> None:
    if payload.school_id is None or payload.academic_year_id is None:
        raise AppError(
            409,
            "SCOPE_POLICY_UNRESOLVED",
            "Cấp vai trò cần school_id và academic_year_id cho đến khi OD-008 được chốt.",
        )


async def _get_user(db: AsyncSession, user_id: UUID, *, for_update: bool = False) -> User:
    statement = select(User).where(User.id == user_id)
    if for_update:
        statement = statement.with_for_update()
    user = (await db.execute(statement)).scalar_one_or_none()
    if user is None:
        raise AppError(404, "USER_NOT_FOUND", "Không tìm thấy người dùng.")
    return user


async def _role_permission_pairs(db: AsyncSession, role_id: UUID) -> list[tuple[str, str]]:
    rows = (
        await db.execute(
            select(Permission.resource_type, Permission.action)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
    ).all()
    return [(row.resource_type, row.action) for row in rows]


# A0102-F03: activation never replaces the invitation. A pending account can neither be
# activated nor parked in "suspended" and activated later.
_STATUS_CHANGE_SOURCES: dict[UserStatus, frozenset[UserStatus]] = {
    UserStatus.ACTIVE: frozenset({UserStatus.SUSPENDED, UserStatus.LOCKED}),
    UserStatus.SUSPENDED: frozenset({UserStatus.ACTIVE, UserStatus.LOCKED}),
}


async def _require_actor_covers_target(
    db: AsyncSession, context: AuthorizationContext, target_id: UUID
) -> None:
    """A0102-F01 — TẠM, chờ OD-008 / Security Owner xác nhận quy tắc.

    Reset, suspend and activate require the actor to hold every permission of every
    unexpired grant of the target (including grants not yet started) in a covering scope.
    """
    if not await principal_covers_target(db, context.principal, target_id):
        raise AppError(
            403,
            "TARGET_PRIVILEGE_EXCEEDS_ACTOR",
            "Không thể thao tác trên tài khoản có quyền vượt quá quyền hiện có.",
        )


async def _delegation_expiry(
    db: AsyncSession,
    actor_id: UUID,
    required: list[tuple[str, str]],
    scope: Scope,
) -> datetime | None:
    """A0102-F06 — TẠM, chờ OD-008: a delegated grant may not outlive the delegator.

    Returns the last instant at which the actor still holds every required permission in
    a covering scope, or None when each is held through at least one non-expiring grant.
    """
    rows = await load_unexpired_grant_permissions(db, actor_id, started_only=True)
    cap: datetime | None = None
    for resource_type, action in required:
        expiries = [
            row.valid_until
            for row in rows
            if row.resource_type == resource_type
            and row.action == action
            and grant_row_scope(row).covers(scope)
        ]
        if not expiries:
            raise AppError(
                403,
                "ROLE_ESCALATION_DENIED",
                "Không thể cấp vai trò chứa quyền vượt quá quyền hiện có.",
            )
        if None not in expiries:
            latest = max(expiries)
            cap = latest if cap is None else min(cap, latest)
    return cap


def _new_account_token(
    *,
    user_id: UUID,
    purpose: str,
    valid_hours: int,
    created_by: UUID,
) -> tuple[AccountToken, str]:
    raw_token = generate_session_token()
    expires_at = datetime.now(UTC) + timedelta(hours=valid_hours)
    return (
        AccountToken(
            user_id=user_id,
            purpose=purpose,
            token_hash=hash_session_token(raw_token),
            expires_at=expires_at,
            created_by=created_by,
        ),
        raw_token,
    )


@router.post("/invitations", response_model=AccountTokenIssue, status_code=201)
async def create_user_invitation(
    payload: UserInvitationCreate,
    request: Request,
    context: CreateUserGuard,
    db: DatabaseSession,
) -> AccountTokenIssue:
    """Create a pending account and disclose its invitation token once."""
    email = str(payload.email).strip().lower()
    existing = (
        await db.execute(select(User.id).where(func.lower(User.email) == email))
    ).scalar_one_or_none()
    if existing is not None:
        raise AppError(409, "EMAIL_EXISTS", "Email đã được sử dụng.")

    user = User(
        email=email,
        display_name=payload.display_name.strip(),
        password_hash=await hash_password_async(secrets.token_urlsafe(48)),
        status=UserStatus.PENDING,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "EMAIL_EXISTS", "Email đã được sử dụng.") from None
    invitation, raw_token = _new_account_token(
        user_id=user.id,
        purpose="invitation",
        valid_hours=payload.valid_hours,
        created_by=context.auth.user.id,
    )
    db.add(invitation)
    await write_audit_in_transaction(
        db,
        action="user:invite",
        resource_type="user",
        resource_id=str(user.id),
        actor_id=context.auth.user.id,
        actor_email=context.auth.user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        after_state={
            "email": user.email,
            "status": str(user.status),
            "invitation_expires_at": invitation.expires_at.isoformat(),
        },
        create_outbox=True,
    )
    await db.commit()
    return AccountTokenIssue(
        user=UserRead.model_validate(user),
        one_time_token=raw_token,
        expires_at=invitation.expires_at,
    )


@router.post("/{user_id}/invitation", response_model=AccountTokenIssue, status_code=201)
async def reissue_user_invitation(
    user_id: UUID,
    payload: InvitationReissue,
    request: Request,
    context: CreateUserGuard,
    db: DatabaseSession,
) -> AccountTokenIssue:
    """Replace every outstanding invitation token for a pending account."""
    user = await _get_user(db, user_id, for_update=True)
    if user.status != UserStatus.PENDING:
        raise AppError(409, "INVITATION_NOT_PENDING", "Tài khoản không còn chờ lời mời.")
    await _require_actor_covers_target(db, context, user.id)
    now = datetime.now(UTC)
    await db.execute(
        update(AccountToken)
        .where(
            AccountToken.user_id == user.id,
            AccountToken.purpose == "invitation",
            AccountToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    invitation, raw_token = _new_account_token(
        user_id=user.id,
        purpose="invitation",
        valid_hours=payload.valid_hours,
        created_by=context.auth.user.id,
    )
    db.add(invitation)
    await write_audit_in_transaction(
        db,
        action="user:invitation_reissue",
        resource_type="user",
        resource_id=str(user.id),
        actor_id=context.auth.user.id,
        actor_email=context.auth.user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        after_state={"status": str(user.status), "expires_at": invitation.expires_at.isoformat()},
        create_outbox=True,
    )
    await db.commit()
    return AccountTokenIssue(
        user=UserRead.model_validate(user),
        one_time_token=raw_token,
        expires_at=invitation.expires_at,
    )


@router.post("/{user_id}/invitation/cancel", status_code=204)
async def cancel_user_invitation(
    user_id: UUID,
    request: Request,
    context: AuthzContext,
    db: DatabaseSession,
) -> None:
    """Invalidate invitation capabilities while leaving the account pending."""
    enforce_permission(
        context,
        resource_type=ResourceType.USER,
        action=ActionType.SUSPEND,
        scope=Scope(),
    )
    user = await _get_user(db, user_id, for_update=True)
    if user.status != UserStatus.PENDING:
        raise AppError(409, "INVITATION_NOT_PENDING", "Tài khoản không còn chờ lời mời.")
    await _require_actor_covers_target(db, context, user.id)
    await db.execute(
        update(AccountToken)
        .where(
            AccountToken.user_id == user.id,
            AccountToken.purpose == "invitation",
            AccountToken.used_at.is_(None),
        )
        .values(used_at=datetime.now(UTC))
    )
    await write_audit_in_transaction(
        db,
        action="user:invitation_cancel",
        resource_type="user",
        resource_id=str(user.id),
        actor_id=context.auth.user.id,
        actor_email=context.auth.user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        after_state={"status": str(user.status), "active_invitation": False},
        create_outbox=True,
    )
    await db.commit()


@router.get("/{user_id}", response_model=UserRead)
async def read_user(
    user_id: UUID,
    _context: ReadUserGuard,
    db: DatabaseSession,
) -> UserRead:
    return UserRead.model_validate(await _get_user(db, user_id))


@router.post("/{user_id}/password-reset", response_model=AccountTokenIssue, status_code=201)
async def issue_password_reset(
    user_id: UUID,
    payload: PasswordResetIssue,
    request: Request,
    context: PasswordResetGuard,
    db: DatabaseSession,
) -> AccountTokenIssue:
    """Issue a single-use reset capability; the raw value is never persisted."""
    user = await _get_user(db, user_id, for_update=True)
    if user.status == UserStatus.PENDING:
        raise AppError(
            409,
            "INVITATION_REQUIRED",
            "Tài khoản đang chờ phải hoàn tất lời mời thay vì đặt lại mật khẩu.",
        )
    await _require_actor_covers_target(db, context, user.id)
    now = datetime.now(UTC)
    await db.execute(
        update(AccountToken)
        .where(
            AccountToken.user_id == user.id,
            AccountToken.purpose == "password_reset",
            AccountToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    reset_token, raw_token = _new_account_token(
        user_id=user.id,
        purpose="password_reset",
        valid_hours=payload.valid_hours,
        created_by=context.auth.user.id,
    )
    db.add(reset_token)
    await write_audit_in_transaction(
        db,
        action="user:password_reset_issue",
        resource_type="user",
        resource_id=str(user.id),
        actor_id=context.auth.user.id,
        actor_email=context.auth.user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        after_state={"reset_expires_at": reset_token.expires_at.isoformat()},
        create_outbox=True,
    )
    await db.commit()
    return AccountTokenIssue(
        user=UserRead.model_validate(user),
        one_time_token=raw_token,
        expires_at=reset_token.expires_at,
    )


@router.patch("/{user_id}/status", response_model=UserRead)
async def change_user_status(
    user_id: UUID,
    payload: UserStatusUpdate,
    request: Request,
    context: AuthzContext,
    db: DatabaseSession,
) -> UserRead:
    if payload.status not in {UserStatus.ACTIVE, UserStatus.SUSPENDED}:
        raise AppError(422, "INVALID_STATUS_CHANGE", "Chỉ hỗ trợ kích hoạt hoặc đình chỉ.")
    action = ActionType.SUSPEND if payload.status == UserStatus.SUSPENDED else ActionType.ACTIVATE
    enforce_permission(
        context,
        resource_type=ResourceType.USER,
        action=action,
        scope=Scope(),
    )
    if user_id == context.auth.user.id and payload.status == UserStatus.SUSPENDED:
        raise AppError(409, "SELF_SUSPEND_DENIED", "Không thể tự đình chỉ tài khoản.")

    user = await _get_user(db, user_id, for_update=True)
    before_status = user.status
    if before_status == UserStatus.PENDING:
        raise AppError(
            409,
            "INVITATION_REQUIRED",
            "Tài khoản đang chờ phải hoàn tất lời mời trước khi đổi trạng thái.",
        )
    if before_status not in _STATUS_CHANGE_SOURCES[payload.status]:
        raise AppError(
            409,
            "INVALID_STATUS_TRANSITION",
            "Không thể chuyển sang trạng thái này từ trạng thái hiện tại.",
        )
    await _require_actor_covers_target(db, context, user.id)
    user.status = payload.status
    if payload.status == UserStatus.ACTIVE:
        user.failed_login_count = 0
        user.locked_until = None
    if payload.status == UserStatus.SUSPENDED:
        await db.execute(
            update(Session)
            .where(Session.user_id == user.id, Session.status == SessionStatus.ACTIVE)
            .values(status=SessionStatus.REVOKED, revoked_at=datetime.now(UTC))
        )
    await write_audit_in_transaction(
        db,
        action=f"user:{action}",
        resource_type="user",
        resource_id=str(user.id),
        actor_id=context.auth.user.id,
        actor_email=context.auth.user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        before_state={"status": str(before_status)},
        after_state={"status": str(user.status)},
        reason=payload.reason,
        create_outbox=True,
    )
    await db.commit()
    return UserRead.model_validate(user)


@router.post("/{user_id}/roles", response_model=UserRoleRead, status_code=201)
async def grant_role(
    user_id: UUID,
    payload: UserRoleAssign,
    request: Request,
    context: AuthzContext,
    db: DatabaseSession,
) -> UserRoleRead:
    _require_explicit_scope(payload)
    scope = _scope_from_assignment(payload)
    enforce_permission(
        context,
        resource_type=ResourceType.USER,
        action=ActionType.GRANT_ROLE,
        scope=scope,
    )
    # A0102-F06 — TẠM, chờ OD-007/OD-008: no self-grant until a two-person flow exists.
    if user_id == context.auth.user.id:
        raise AppError(403, "SELF_GRANT_DENIED", "Không thể tự cấp vai trò cho chính mình.")
    await _get_user(db, user_id, for_update=True)
    role = (await db.execute(select(Role).where(Role.id == payload.role_id))).scalar_one_or_none()
    if role is None:
        raise AppError(404, "ROLE_NOT_FOUND", "Không tìm thấy vai trò.")
    permission_pairs = await _role_permission_pairs(db, role.id)
    if not can_delegate_role(context.principal, permission_pairs, scope):
        raise AppError(
            403,
            "ROLE_ESCALATION_DENIED",
            "Không thể cấp vai trò chứa quyền vượt quá quyền hiện có.",
        )

    valid_from = payload.valid_from or datetime.now(UTC)
    if valid_from.tzinfo is None or (
        payload.valid_until is not None and payload.valid_until.tzinfo is None
    ):
        raise AppError(422, "TIMEZONE_REQUIRED", "Thời điểm phân quyền phải có múi giờ.")
    valid_until = payload.valid_until
    delegation_expiry = await _delegation_expiry(
        db,
        context.auth.user.id,
        [*permission_pairs, (ResourceType.USER, ActionType.GRANT_ROLE)],
        scope,
    )
    if delegation_expiry is not None:
        if valid_until is None:
            valid_until = delegation_expiry
        elif valid_until > delegation_expiry:
            raise AppError(
                422,
                "ROLE_VALIDITY_EXCEEDS_DELEGATOR",
                "valid_until không được vượt quá hiệu lực quyền của người cấp.",
            )
    if valid_until is not None and valid_until <= valid_from:
        raise AppError(422, "INVALID_ROLE_VALIDITY", "valid_until phải sau valid_from.")

    duplicate = (
        await db.execute(
            select(UserRole.id).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role.id,
                UserRole.school_id == payload.school_id,
                UserRole.academic_year_id == payload.academic_year_id,
                UserRole.grade_id == payload.grade_id,
                UserRole.class_id == payload.class_id,
                UserRole.subject_id == payload.subject_id,
                UserRole.is_active.is_(True),
                UserRole.revoked_at.is_(None),
            )
        )
    ).scalar_one_or_none()
    if duplicate is not None:
        raise AppError(409, "ROLE_ALREADY_GRANTED", "Vai trò đã được cấp trong scope này.")

    assignment = UserRole(
        user_id=user_id,
        role=role,
        school_id=payload.school_id,
        academic_year_id=payload.academic_year_id,
        grade_id=payload.grade_id,
        class_id=payload.class_id,
        subject_id=payload.subject_id,
        valid_from=valid_from,
        valid_until=valid_until,
        granted_by=context.auth.user.id,
    )
    db.add(assignment)
    await db.flush()
    await write_audit_in_transaction(
        db,
        action="user:grant_role",
        resource_type="user_role",
        resource_id=str(assignment.id),
        actor_id=context.auth.user.id,
        actor_email=context.auth.user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        after_state={
            "user_id": str(user_id),
            "role_id": str(role.id),
            "school_id": str(payload.school_id),
            "academic_year_id": str(payload.academic_year_id),
            "grade_id": payload.grade_id,
            "class_id": str(payload.class_id) if payload.class_id else None,
            "subject_id": str(payload.subject_id) if payload.subject_id else None,
            "valid_from": valid_from.isoformat(),
            "valid_until": valid_until.isoformat() if valid_until else None,
        },
        create_outbox=True,
    )
    await db.commit()
    return UserRoleRead.model_validate(assignment)


@router.post("/{user_id}/roles/revoke", response_model=UserRoleRead)
async def revoke_role(
    user_id: UUID,
    payload: UserRoleRevoke,
    request: Request,
    context: AuthzContext,
    db: DatabaseSession,
) -> UserRoleRead:
    assignment = (
        await db.execute(
            select(UserRole)
            .where(UserRole.id == payload.user_role_id, UserRole.user_id == user_id)
            .with_for_update()
        )
    ).scalar_one_or_none()
    if assignment is None:
        raise AppError(404, "ROLE_GRANT_NOT_FOUND", "Không tìm thấy lần cấp vai trò.")
    if not assignment.is_active or assignment.revoked_at is not None:
        raise AppError(409, "ROLE_ALREADY_REVOKED", "Vai trò đã được thu hồi.")
    scope = _scope_from_assignment(assignment)
    enforce_permission(
        context,
        resource_type=ResourceType.USER,
        action=ActionType.REVOKE_ROLE,
        scope=scope,
    )
    permission_pairs = await _role_permission_pairs(db, assignment.role_id)
    if not can_delegate_role(context.principal, permission_pairs, scope):
        raise AppError(403, "ROLE_ESCALATION_DENIED", "Không được thu hồi vai trò cấp cao hơn.")

    assignment.is_active = False
    assignment.revoked_at = datetime.now(UTC)
    assignment.revoked_by = context.auth.user.id
    assignment.revoke_reason = payload.reason
    await write_audit_in_transaction(
        db,
        action="user:revoke_role",
        resource_type="user_role",
        resource_id=str(assignment.id),
        actor_id=context.auth.user.id,
        actor_email=context.auth.user.email,
        request_id=request.state.request_id,
        ip_address=client_ip(request),
        user_agent=request.headers.get("user-agent"),
        before_state={"is_active": True},
        after_state={"is_active": False},
        reason=payload.reason,
        create_outbox=True,
    )
    await db.commit()
    await db.refresh(assignment, attribute_names=["role"])
    return UserRoleRead.model_validate(assignment)
