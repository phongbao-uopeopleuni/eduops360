"""One-shot staging migrator. Never run in the web service."""

import os
import subprocess
import sys

import psycopg
from psycopg import sql
from sqlalchemy.engine import make_url


def main():
    try:
        owner_url = make_url(os.environ["EDUOPS_DATABASE_URL"])
        if owner_url.drivername != "postgresql+psycopg":
            raise ValueError
        runtime_password = os.environ["STAGING_RUNTIME_PASSWORD"]
        audit_password = os.environ["STAGING_AUDIT_WORKER_PASSWORD"]
        if (
            min(len(runtime_password), len(audit_password)) < 32
            or runtime_password == audit_password
        ):
            raise ValueError
        dsn = owner_url.set(drivername="postgresql").render_as_string(hide_password=False)
        with psycopg.connect(dsn) as connection:
            for name, password in (
                ("eduops_runtime", runtime_password),
                ("eduops_audit_worker", audit_password),
            ):
                role = connection.execute(
                    "SELECT rolsuper, rolcreatedb, rolcreaterole, rolreplication, rolbypassrls, "
                    "rolinherit FROM pg_roles WHERE rolname = %s",
                    (name,),
                ).fetchone()
                if role is None:
                    connection.execute(
                        sql.SQL(
                            "CREATE ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE "
                            "NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD {}"
                        ).format(sql.Identifier(name), sql.Literal(password))
                    )
                elif any(role):
                    raise ValueError("Existing staging role is not least-privileged")
        # Do not rotate existing role passwords automatically.
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"], capture_output=True
        )
        if result.returncode:
            raise RuntimeError("Migration failed")
    except Exception:
        raise SystemExit(
            "Staging migration failed; inspect privately. No credentials are logged."
        ) from None
    print("Staging roles checked and migrations completed.")


if __name__ == "__main__":
    main()
