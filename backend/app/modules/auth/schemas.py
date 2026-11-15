"""Pydantic schemas for authentication API.

Used for request/response validation and OpenAPI documentation.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from app.modules.auth.constants import UserStatus

# === User Schemas ===


class UserBase(BaseModel):
    """Base user fields."""

    email: EmailStr
    display_name: str = Field(min_length=1, max_length=100)


class UserRead(UserBase):
    """User response (no sensitive data)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: UserStatus
    mfa_enabled: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """Update user request."""

    display_name: str | None = Field(None, min_length=1, max_length=100)


class UserStatusUpdate(BaseModel):
    """Update user status (admin action)."""

    status: UserStatus
    reason: str | None = Field(None, max_length=500)


# === Password Schemas ===


class PasswordChange(BaseModel):
    """Change password request."""

    current_password: SecretStr
    new_password: SecretStr = Field(min_length=8, max_length=128)


class PasswordReset(BaseModel):
    """Admin password reset request."""

    new_password: SecretStr = Field(min_length=8, max_length=128)


class UserInvitationCreate(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=1, max_length=100)
    valid_hours: int = Field(default=24, ge=1, le=168)


class AccountTokenIssue(BaseModel):
    user: UserRead
    one_time_token: str
    expires_at: datetime


class InvitationAccept(BaseModel):
    token: SecretStr = Field(min_length=32, max_length=256)
    password: SecretStr = Field(min_length=8, max_length=128)


class InvitationReissue(BaseModel):
    valid_hours: int = Field(default=24, ge=1, le=168)


class PasswordResetIssue(BaseModel):
    valid_hours: int = Field(default=1, ge=1, le=24)


class PasswordResetAccept(BaseModel):
    token: SecretStr = Field(min_length=32, max_length=256)
    new_password: SecretStr = Field(min_length=8, max_length=128)


# === Login/Session Schemas ===


class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr
    password: SecretStr
    # MFA code if MFA is enabled
    mfa_code: str | None = Field(None, min_length=6, max_length=6)


class LoginResponse(BaseModel):
    """Login response.

    TẠM: P02-T03 spec yêu cầu cookie HttpOnly + CSRF.
    Kiểu phiên chính xác chờ Product Owner quyết định.
    Hiện chỉ trả thông tin user, session token sẽ được đặt
    trong cookie bởi endpoint (chưa implement).
    """

    user: UserRead
    expires_at: datetime


class SessionInfo(BaseModel):
    """Session information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_agent: str | None
    ip_address: str | None
    created_at: datetime
    expires_at: datetime
    last_activity_at: datetime


# === Role Schemas ===


class RoleRead(BaseModel):
    """Role response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name_vi: str
    description_vi: str | None
    is_system: bool


class PermissionRead(BaseModel):
    """Permission response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    resource_type: str
    action: str
    requires_approval: bool
    description_vi: str | None


# === User Role Assignment Schemas ===


class UserRoleAssign(BaseModel):
    """Assign role to user request.

    TẠM - scope dimensions pending OD-008.
    """

    role_id: UUID
    # Scope (TẠM, NULL = all)
    school_id: UUID | None = None
    academic_year_id: UUID | None = None
    grade_id: int | None = Field(None, ge=1, le=12)
    class_id: UUID | None = None
    subject_id: UUID | None = None
    # Validity
    valid_from: datetime | None = None
    valid_until: datetime | None = None


class UserRoleRevoke(BaseModel):
    """Revoke role from user request."""

    user_role_id: UUID
    reason: str = Field(min_length=1, max_length=500)


class UserRoleRead(BaseModel):
    """User role assignment response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    role: RoleRead
    # Scope
    school_id: UUID | None
    academic_year_id: UUID | None
    grade_id: int | None
    class_id: UUID | None
    subject_id: UUID | None
    # Validity
    valid_from: datetime
    valid_until: datetime | None
    is_active: bool
    # Audit
    granted_at: datetime
    granted_by: UUID | None
    revoked_at: datetime | None
    revoked_by: UUID | None
    revoke_reason: str | None


# === Error Schemas ===


class AuthError(BaseModel):
    """Authentication error response."""

    code: str
    message: str
    request_id: str | None = None
