from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.dependencies import get_db_session
from app.modules.auth.constants import ActionType, ResourceType
from app.modules.auth.models import Permission as PermissionModel
from app.modules.auth.models import RolePermission, UserRole
from app.modules.auth.permissions import (
    AuthorizationRequest,
    Permission,
    Principal,
    Scope,
    check_authorization,
)
from app.modules.auth.session import AuthContext, get_auth_context, require_csrf


@dataclass(frozen=True)
class AuthorizationContext:
    auth: AuthContext
    principal: Principal


async def load_principal(db: AsyncSession, user_id) -> Principal:
    rows = await load_unexpired_grant_permissions(db, user_id, started_only=True)

    permissions: set[Permission] = set()
    for row in rows:
        try:
            resource_type = ResourceType(row.resource_type)
            action = ActionType(row.action)
        except ValueError:
            continue
        permissions.add(
            Permission(
                resource_type=resource_type,
                action=action,
                scope=Scope(
                    school_id=row.school_id,
                    academic_year_id=row.academic_year_id,
                    grade_id=row.grade_id,
                    class_id=row.class_id,
                    subject_id=row.subject_id,
                ),
            )
        )
    return Principal(user_id=user_id, permissions=frozenset(permissions))


async def load_unexpired_grant_permissions(db: AsyncSession, user_id, *, started_only: bool):
    """Return permissions from active, unrevoked and unexpired role grants."""
    now = datetime.now(UTC)
    conditions = [
        UserRole.user_id == user_id,
        UserRole.is_active.is_(True),
        UserRole.revoked_at.is_(None),
        or_(UserRole.valid_until.is_(None), UserRole.valid_until > now),
    ]
    if started_only:
        conditions.append(UserRole.valid_from <= now)
    return (
        await db.execute(
            select(
                PermissionModel.resource_type,
                PermissionModel.action,
                UserRole.school_id,
                UserRole.academic_year_id,
                UserRole.grade_id,
                UserRole.class_id,
                UserRole.subject_id,
                UserRole.valid_until,
            )
            .join(RolePermission, RolePermission.permission_id == PermissionModel.id)
            .join(UserRole, UserRole.role_id == RolePermission.role_id)
            .where(*conditions)
        )
    ).all()


def grant_row_scope(row) -> Scope:
    return Scope(
        school_id=row.school_id,
        academic_year_id=row.academic_year_id,
        grade_id=row.grade_id,
        class_id=row.class_id,
        subject_id=row.subject_id,
    )


async def principal_covers_target(db: AsyncSession, principal: Principal, target_id) -> bool:
    """Check every unexpired target grant, including grants not started yet."""
    rows = await load_unexpired_grant_permissions(db, target_id, started_only=False)
    return all(
        can_delegate_role(
            principal,
            [(row.resource_type, row.action)],
            grant_row_scope(row),
        )
        for row in rows
    )


async def get_authorization_context(
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthorizationContext:
    return AuthorizationContext(
        auth=auth,
        principal=await load_principal(db, auth.user.id),
    )


async def get_csrf_authorization_context(
    auth: Annotated[AuthContext, Depends(require_csrf)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthorizationContext:
    return AuthorizationContext(
        auth=auth,
        principal=await load_principal(db, auth.user.id),
    )


def enforce_permission(
    context: AuthorizationContext,
    *,
    resource_type: ResourceType,
    action: ActionType,
    scope: Scope,
    submitter_id=None,
) -> None:
    allowed, reason = check_authorization(
        context.principal,
        AuthorizationRequest(
            action=action,
            resource_type=resource_type,
            resource_scope=scope,
            submitter_id=submitter_id,
        ),
    )
    if not allowed:
        raise AppError(403, "FORBIDDEN", reason)


def require_permission(
    resource_type: ResourceType,
    action: ActionType,
    *,
    csrf_protected: bool = False,
):
    async def checked_dependency(
        context: AuthorizationContext,
    ) -> AuthorizationContext:
        enforce_permission(
            context,
            resource_type=resource_type,
            action=action,
            scope=Scope(),
        )
        return context

    async def read_dependency(
        context: Annotated[
            AuthorizationContext,
            Depends(get_authorization_context),
        ],
    ) -> AuthorizationContext:
        return await checked_dependency(context)

    async def csrf_dependency(
        context: Annotated[
            AuthorizationContext,
            Depends(get_csrf_authorization_context),
        ],
    ) -> AuthorizationContext:
        return await checked_dependency(context)

    return csrf_dependency if csrf_protected else read_dependency


def can_delegate_role(
    principal: Principal,
    role_permissions: list[tuple[str, str]],
    scope: Scope,
) -> bool:
    if not role_permissions:
        return False
    for resource_value, action_value in role_permissions:
        try:
            resource_type = ResourceType(resource_value)
            action = ActionType(action_value)
        except ValueError:
            return False
        if not any(
            permission.resource_type == resource_type
            and permission.action == action
            and permission.scope.covers(scope)
            for permission in principal.permissions
        ):
            return False
    return True
