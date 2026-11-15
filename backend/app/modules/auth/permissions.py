"""Permission checking logic.

Implements deny-by-default authorization model.
Backend authorizes all sensitive operations; frontend guards are UX only.

TẠM values: OD-007 (approval actions), OD-008 (scope dimensions)
"""

from dataclasses import dataclass
from uuid import UUID

from app.modules.auth.constants import (
    ActionType,
    ResourceType,
    requires_two_step_approval,
)


@dataclass(frozen=True)
class Scope:
    """Resource scope for permission checking.

    All dimensions are optional. NULL means "all" for that dimension.
    TẠM - dimensions pending OD-008.
    """

    school_id: UUID | None = None
    academic_year_id: UUID | None = None
    grade_id: int | None = None
    class_id: UUID | None = None
    subject_id: UUID | None = None

    def covers(self, other: "Scope") -> bool:
        """Check if this scope covers another scope.

        A scope covers another if all non-null dimensions match.
        NULL in self means "all" and covers any value in other.
        """
        if self.school_id is not None and self.school_id != other.school_id:
            return False
        if self.academic_year_id is not None and self.academic_year_id != other.academic_year_id:
            return False
        if self.grade_id is not None and self.grade_id != other.grade_id:
            return False
        if self.class_id is not None and self.class_id != other.class_id:
            return False
        if self.subject_id is not None and self.subject_id != other.subject_id:
            return False
        return True


@dataclass(frozen=True)
class Permission:
    """A permission grant."""

    resource_type: ResourceType
    action: ActionType
    scope: Scope


@dataclass(frozen=True)
class Principal:
    """The authenticated user making a request."""

    user_id: UUID
    permissions: frozenset[Permission]


@dataclass(frozen=True)
class AuthorizationRequest:
    """A request to perform an action on a resource."""

    action: ActionType
    resource_type: ResourceType
    resource_scope: Scope
    # For two-step approval
    submitter_id: UUID | None = None


type AuthorizationResult = tuple[bool, str]


def check_authorization(
    principal: Principal,
    request: AuthorizationRequest,
) -> AuthorizationResult:
    """Check if principal is authorized for the request.

    Returns (True, "") if authorized, (False, reason) if denied.

    DENY BY DEFAULT: If no matching permission is found, access is denied.
    """
    # Check two-step approval constraint
    if requires_two_step_approval(request.resource_type, request.action):
        # F07 fix: missing submitter_id → deny (caller must provide it)
        if request.submitter_id is None:
            return (
                False,
                "Thao tác cần phê duyệt hai bước nhưng thiếu thông tin người gửi",
            )
        if request.submitter_id == principal.user_id:
            return (
                False,
                "Người phê duyệt không được là người gửi yêu cầu",
            )

    # Find matching permission
    for perm in principal.permissions:
        if perm.resource_type != request.resource_type:
            continue
        if perm.action != request.action:
            continue
        if not perm.scope.covers(request.resource_scope):
            continue
        # Found matching permission
        return (True, "")

    # DENY BY DEFAULT
    return (False, "Không có quyền thực hiện thao tác này")


def can_access_audit_logs(principal: Principal, scope: Scope) -> bool:
    """Check if principal can read audit logs.

    Note: NO delete permission exists for audit_log.
    """
    for perm in principal.permissions:
        if perm.resource_type == ResourceType.AUDIT_LOG:
            if perm.action == ActionType.READ and perm.scope.covers(scope):
                return True
    return False


def can_modify_audit_logs(principal: Principal) -> bool:
    """Check if principal can modify audit logs.

    ALWAYS returns False. Audit logs are immutable.
    No role, including system_admin, can delete or modify audit records.
    """
    return False
