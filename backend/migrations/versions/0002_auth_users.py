"""Auth schema: users, roles, permissions, sessions.

Revision ID: 0002_auth_users
Revises: 0001_foundation
Create Date: 2026-11-12

Phase 02 - IAM, security baseline, audit & roles.
TẠM values: OD-007 (approval actions), OD-008 (scope dimensions).
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_auth_users"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("mfa_secret", sa.String(255), nullable=True),
        sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'suspended', 'locked')",
            name="ck_users_status",
        ),
    )
    op.create_index("ix_users_status", "users", ["status"])

    # Roles table
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("name_vi", sa.String(100), nullable=False),
        sa.Column("description_vi", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Permissions table
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(100), unique=True, nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("description_vi", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_permissions_resource_action", "permissions", ["resource_type", "action"])

    # Role-Permission mapping
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "permission_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "granted_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )

    # User-Role assignment with scope
    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        # Scope dimensions (TẠM chờ OD-008)
        sa.Column("school_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("academic_year_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("grade_id", sa.Integer(), nullable=True),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Validity
        sa.Column(
            "valid_from",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        # Audit
        sa.Column(
            "granted_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "granted_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "revoked_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("revoke_reason", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "grade_id IS NULL OR (grade_id >= 1 AND grade_id <= 12)",
            name="ck_user_roles_grade",
        ),
    )
    op.create_index("ix_user_roles_user_active", "user_roles", ["user_id", "is_active"])

    # Sessions table
    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(255), unique=True, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('active', 'expired', 'revoked')",
            name="ck_sessions_status",
        ),
    )
    op.create_index("ix_sessions_user_status", "sessions", ["user_id", "status"])
    op.create_index("ix_sessions_expires", "sessions", ["expires_at"])

    # Seed system roles (TẠM chờ OD-008)
    op.execute("""
        INSERT INTO roles (id, code, name_vi, is_system) VALUES
        (gen_random_uuid(), 'system_admin', 'Quản trị viên hệ thống', TRUE),
        (gen_random_uuid(), 'school_admin', 'Quản trị viên trường', TRUE),
        (gen_random_uuid(), 'academic_admin', 'Quản lý học vụ', TRUE),
        (gen_random_uuid(), 'exam_admin', 'Quản lý khảo thí', TRUE),
        (gen_random_uuid(), 'grade_coordinator', 'Điều phối viên khối', FALSE),
        (gen_random_uuid(), 'class_teacher', 'Giáo viên chủ nhiệm', FALSE),
        (gen_random_uuid(), 'auditor', 'Kiểm toán viên', TRUE)
    """)

    # Seed permissions (TẠM chờ OD-007)
    # -- User management
    _perm = (
        "INSERT INTO permissions"
        " (id, code, resource_type, action, requires_approval, description_vi)"
        " VALUES (gen_random_uuid(), %s, %s, %s, %s, %s)"
    )
    _perms = [
        # user management
        ("'user:create'", "'user'", "'create'", "FALSE", "'Tạo tài khoản'"),
        ("'user:read'", "'user'", "'read'", "FALSE", "'Xem người dùng'"),
        ("'user:update'", "'user'", "'update'", "FALSE", "'Cập nhật người dùng'"),
        ("'user:suspend'", "'user'", "'suspend'", "FALSE", "'Khóa tài khoản'"),
        ("'user:grant_role'", "'user'", "'grant_role'", "FALSE", "'Cấp quyền'"),
        ("'user:revoke_role'", "'user'", "'revoke_role'", "FALSE", "'Thu hồi quyền'"),
        # audit (NO delete permission)
        ("'audit:read'", "'audit_log'", "'read'", "FALSE", "'Xem audit'"),
        # student (TẠM chờ OD-007)
        ("'student:create'", "'student'", "'create'", "FALSE", "'Tạo học sinh'"),
        ("'student:read'", "'student'", "'read'", "FALSE", "'Xem học sinh'"),
        ("'student:update'", "'student'", "'update'", "FALSE", "'Cập nhật HS'"),
        ("'student:import'", "'student'", "'import'", "FALSE", "'Nhập dữ liệu'"),
        # grade (TẠM chờ OD-007)
        ("'grade:read'", "'grade'", "'read'", "FALSE", "'Xem điểm'"),
        ("'grade:update'", "'grade'", "'update'", "FALSE", "'Cập nhật điểm'"),
        ("'grade:approve'", "'grade'", "'approve'", "TRUE", "'Phê duyệt điểm'"),
        ("'grade:lock'", "'grade'", "'lock'", "TRUE", "'Khóa điểm'"),
        # timetable (TẠM chờ OD-007)
        ("'timetable:read'", "'timetable'", "'read'", "FALSE", "'Xem TKB'"),
        ("'timetable:update'", "'timetable'", "'update'", "FALSE", "'Cập nhật TKB'"),
        ("'timetable:publish'", "'timetable'", "'publish'", "TRUE", "'Công bố TKB'"),
    ]
    for code, res, act, appr, desc in _perms:
        op.execute(
            f"INSERT INTO permissions"
            f" (id, code, resource_type, action,"
            f" requires_approval, description_vi)"
            f" VALUES (gen_random_uuid(),"
            f" {code}, {res}, {act}, {appr}, {desc})"
        )


def downgrade():
    op.drop_table("sessions")
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
