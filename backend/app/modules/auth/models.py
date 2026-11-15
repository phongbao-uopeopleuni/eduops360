"""SQLAlchemy models for authentication and authorization.

Phase 02 - IAM, RBAC, audit trail.
TẠM values pending OD-007/OD-008.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.auth.constants import SessionStatus, UserStatus


class User(Base):
    """User account for authentication.

    Stores identity, credentials, and account state.
    Does NOT store personal student data - that belongs in Student model (Phase 03).
    """

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    # Login credentials
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Display info
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Account state
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=UserStatus.PENDING)

    # Security
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mfa_last_used_step: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    password_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=func.now(),
    )

    # Relationships
    roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        foreign_keys="UserRole.user_id",
        lazy="selectin",
    )
    sessions: Mapped[list["Session"]] = relationship(back_populates="user", lazy="selectin")

    __table_args__ = (
        CheckConstraint(
            f"status IN ('{UserStatus.PENDING}', '{UserStatus.ACTIVE}', "
            f"'{UserStatus.SUSPENDED}', '{UserStatus.LOCKED}')",
            name="ck_users_status",
        ),
        Index("ix_users_status", "status"),
        Index("uq_users_email_lower", func.lower(email), unique=True),
    )


class Role(Base):
    """Role definition for RBAC.

    Roles are system-defined or custom.
    TẠM - role hierarchy pending OD-008.
    """

    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_vi: Mapped[str] = mapped_column(String(100), nullable=False)
    description_vi: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=func.now(),
    )

    # Relationships
    permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="role", lazy="selectin"
    )
    user_roles: Mapped[list["UserRole"]] = relationship(back_populates="role", lazy="selectin")


class Permission(Base):
    """Permission definition.

    Defines what actions can be performed on what resources.
    TẠM - requires_approval pending OD-007.
    """

    __tablename__ = "permissions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description_vi: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    # Relationships
    role_permissions: Mapped[list["RolePermission"]] = relationship(
        back_populates="permission", lazy="selectin"
    )

    __table_args__ = (Index("ix_permissions_resource_action", "resource_type", "action"),)


class RolePermission(Base):
    """Role-Permission mapping."""

    __tablename__ = "role_permissions"

    role_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    granted_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")


class UserRole(Base):
    """User-Role assignment with scope.

    TẠM - scope dimensions pending OD-008.
    """

    __tablename__ = "user_roles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    role_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )

    # Scope dimensions (TẠM chờ OD-008, NULL = all)
    school_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    academic_year_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    grade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    class_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    subject_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Validity
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Audit
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    granted_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
    )
    revoke_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="roles",
        foreign_keys=[user_id],
    )
    role: Mapped["Role"] = relationship(back_populates="user_roles")

    __table_args__ = (
        CheckConstraint(
            "grade_id IS NULL OR (grade_id >= 1 AND grade_id <= 12)",
            name="ck_user_roles_grade",
        ),
        Index("ix_user_roles_user_active", "user_id", "is_active"),
    )


class Session(Base):
    """User session for authentication."""

    __tablename__ = "sessions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    csrf_token_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default=SessionStatus.ACTIVE)

    # Metadata
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)  # IPv6 max

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sessions")

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'expired', 'revoked')",
            name="ck_sessions_status",
        ),
        Index("ix_sessions_user_status", "user_id", "status"),
        Index("ix_sessions_expires", "expires_at"),
    )


class AccountToken(Base):
    """Single-use hashed invitation or password-reset capability."""

    __tablename__ = "account_tokens"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    purpose: Mapped[str] = mapped_column(String(20), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )

    __table_args__ = (
        CheckConstraint(
            "purpose IN ('invitation', 'password_reset')",
            name="ck_account_tokens_purpose",
        ),
        Index("ix_account_tokens_user_purpose", "user_id", "purpose"),
        Index("ix_account_tokens_expires", "expires_at"),
    )
