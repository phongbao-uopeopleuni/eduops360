"""Seed a disposable local admin account for the imported school dataset.

Required:
  EDUOPS_TEST_MIGRATOR_DSN: disposable PostgreSQL migrator DSN
  EDUOPS_LOCAL_ADMIN_PASSWORD: password for the local-only account

The password is never written to disk or printed.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from uuid import uuid4

import psycopg

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", default="admin@example.com")
    parser.add_argument("--school-code", default="DATA-2000")
    args = parser.parse_args()

    dsn = os.getenv("EDUOPS_TEST_MIGRATOR_DSN")
    password = os.getenv("EDUOPS_LOCAL_ADMIN_PASSWORD")
    if not dsn or not password:
        parser.error("EDUOPS_TEST_MIGRATOR_DSN and EDUOPS_LOCAL_ADMIN_PASSWORD are required")

    sys.path.insert(0, str(ROOT / "backend"))
    from app.modules.auth.services import hash_password

    with psycopg.connect(dsn) as connection:
        user_id = uuid4()
        connection.execute(
            """
            INSERT INTO users (id, email, password_hash, display_name, status)
            VALUES (%s, %s, %s, 'Quản trị viên dữ liệu 2000', 'active')
            ON CONFLICT (email) DO UPDATE
            SET password_hash = EXCLUDED.password_hash,
                display_name = EXCLUDED.display_name,
                status = 'active',
                updated_at = now()
            """,
            (user_id, args.email, hash_password(password)),
        )
        user_id = connection.execute(
            "SELECT id FROM users WHERE email = %s", (args.email,)
        ).fetchone()[0]
        school_id = connection.execute(
            "SELECT id FROM schools WHERE code = %s", (args.school_code,)
        ).fetchone()
        if school_id is None:
            parser.error(f"school code not found: {args.school_code}")
        role_id = connection.execute(
            "SELECT id FROM roles WHERE code = 'system_admin'"
        ).fetchone()[0]

        connection.execute(
            """
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT %s, id FROM permissions
            ON CONFLICT DO NOTHING
            """,
            (role_id,),
        )
        connection.execute(
            """
            INSERT INTO user_roles
                (id, user_id, role_id, is_active, school_id, academic_year_id,
                 grade_id, class_id, subject_id)
            SELECT %s, %s, %s, TRUE, NULL, NULL, NULL, NULL, NULL
            WHERE NOT EXISTS (
                SELECT 1 FROM user_roles
                WHERE user_id = %s AND role_id = %s AND is_active = TRUE
            )
            """,
            (uuid4(), user_id, role_id, user_id, role_id),
        )
        connection.execute(
            """
            UPDATE user_roles
            SET school_id = NULL,
                academic_year_id = NULL,
                grade_id = NULL,
                class_id = NULL,
                subject_id = NULL,
                valid_from = now(),
                valid_until = NULL,
                revoked_at = NULL,
                revoked_by = NULL,
                revoke_reason = NULL
            WHERE user_id = %s AND role_id = %s AND is_active = TRUE
            """,
            (user_id, role_id),
        )

    print(f"Seeded local admin account: {args.email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
