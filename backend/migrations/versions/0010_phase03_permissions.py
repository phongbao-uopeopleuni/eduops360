"""Add Phase 03 permissions for academic_year, class, enrollment resources.

Revision ID: 0010_phase03_permissions
Revises: 0009_phase03_school_student
Create Date: 2026-11-19
"""

from alembic import op

revision = "0010_phase03_permissions"
down_revision = "0009_phase03_school_student"
branch_labels = None
depends_on = None

_PERMS = [
    ("academic_year:create", "academic_year", "create", False, "Tạo năm học"),
    ("academic_year:read", "academic_year", "read", False, "Xem năm học"),
    ("academic_year:update", "academic_year", "update", False, "Cập nhật năm học"),
    ("academic_year:activate", "academic_year", "activate", False, "Kích hoạt năm học"),
    ("academic_year:archive", "academic_year", "archive", False, "Lưu trữ năm học"),
    ("class:create", "class", "create", False, "Tạo lớp"),
    ("class:read", "class", "read", False, "Xem lớp"),
    ("class:update", "class", "update", False, "Cập nhật lớp"),
    ("enrollment:create", "enrollment", "create", False, "Ghi danh"),
    ("enrollment:read", "enrollment", "read", False, "Xem ghi danh"),
    ("enrollment:update", "enrollment", "update", False, "Cập nhật ghi danh"),
]


def upgrade():
    for code, res, act, appr, desc in _PERMS:
        appr_sql = "TRUE" if appr else "FALSE"
        op.execute(
            f"INSERT INTO permissions"
            f" (id, code, resource_type, action, requires_approval, description_vi)"
            f" VALUES (gen_random_uuid(),"
            f" '{code}', '{res}', '{act}', {appr_sql}, '{desc}')"
            f" ON CONFLICT (code) DO NOTHING"
        )
    op.execute(
        """
        INSERT INTO role_permissions (role_id, permission_id)
        SELECT r.id, p.id
        FROM roles r, permissions p
        WHERE r.code = 'dev_local_admin'
          AND p.resource_type IN ('academic_year', 'class', 'enrollment', 'student')
          AND NOT EXISTS (
              SELECT 1 FROM role_permissions rp
              WHERE rp.role_id = r.id AND rp.permission_id = p.id
          )
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM role_permissions
        WHERE permission_id IN (
            SELECT id FROM permissions
            WHERE resource_type IN ('academic_year', 'class', 'enrollment')
        )
        """
    )
    for code, _, _, _, _ in _PERMS:
        op.execute(
            f"DELETE FROM permissions WHERE code = '{code}'"
            f" AND NOT EXISTS ("
            f"   SELECT 1 FROM role_permissions WHERE permission_id = permissions.id"
            f" )"
        )
