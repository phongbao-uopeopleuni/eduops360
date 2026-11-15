"""Seed one synthetic real-auth browser fixture in an isolated migrated database.

Required environment:
    EDUOPS_TEST_MIGRATOR_DSN  Disposable PostgreSQL DSN with insert privileges.

The generated password is never printed and may only be written below `.local/`,
which is ignored. The caller is responsible for deleting the output and database.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
from pathlib import Path
from uuid import uuid4

import psycopg

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
LOCAL = ROOT / ".local"
DEFAULT_OUTPUT = LOCAL / "real-auth-e2e.json"


def _output_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(LOCAL.resolve())
    except ValueError as error:
        raise ValueError("fixture output must stay below .local/") from error
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    dsn = os.getenv("EDUOPS_TEST_MIGRATOR_DSN")
    if not dsn:
        parser.error("EDUOPS_TEST_MIGRATOR_DSN is required")
    try:
        output = _output_path(args.output)
    except ValueError as error:
        parser.error(str(error))

    sys.path.insert(0, str(BACKEND))
    from app.modules.auth.services import hash_password

    suffix = uuid4().hex
    user_id, role_id, grant_id = uuid4(), uuid4(), uuid4()
    # email-validator rejects special-use TLDs such as .invalid; example.com remains
    # reserved for documentation and cannot route to a real school mailbox.
    email = f"real-auth-{suffix[:16]}@example.com"
    password = "E2E-" + secrets.token_urlsafe(24)
    role_code = f"real_auth_{suffix[:24]}"

    with psycopg.connect(dsn) as connection:
        permission = connection.execute(
            "SELECT id FROM permissions WHERE code = 'user:read'"
        ).fetchone()
        if permission is None:
            raise RuntimeError("database is not migrated/seeded with user:read")
        connection.execute(
            "INSERT INTO users (id, email, password_hash, display_name, status) "
            "VALUES (%s, %s, %s, 'Synthetic real-auth E2E', 'active')",
            (user_id, email, hash_password(password)),
        )
        connection.execute(
            "INSERT INTO roles (id, code, name_vi, description_vi) "
            "VALUES (%s, %s, 'E2E chỉ đọc tổng hợp', 'Synthetic disposable fixture')",
            (role_id, role_code),
        )
        connection.execute(
            "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)",
            (role_id, permission[0]),
        )
        connection.execute(
            "INSERT INTO user_roles (id, user_id, role_id) VALUES (%s, %s, %s)",
            (grant_id, user_id, role_id),
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {"email": email, "password": password, "user_id": str(user_id)},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Seeded synthetic real-auth fixture; credentials written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
