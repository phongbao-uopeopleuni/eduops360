"""Task-local verification against disposable PostgreSQL; no .env files used."""

import json
import os
import secrets
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
NAME = "eduops-edu0068-audit-pg"
LABEL = "eduops.audit=EDU-0068"


def main():
    if subprocess.run(["docker", "container", "inspect", NAME], capture_output=True).returncode == 0:
        raise SystemExit("Refusing to reuse an existing verification container")
    env = os.environ.copy()
    passwords = {key: secrets.token_urlsafe(24) for key in (
        "POSTGRES_PASSWORD", "EDUOPS_RUNTIME_PASSWORD", "EDUOPS_AUDIT_WORKER_PASSWORD"
    )}
    env.update(passwords, POSTGRES_DB="eduops360", POSTGRES_USER="eduops_migrator")

    def run(command, *, cwd=ROOT, check=True):
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
        output = result.stdout + result.stderr
        for value in passwords.values():
            output = output.replace(value, "[REDACTED]")
        if check and result.returncode:
            print(output)
            raise RuntimeError(f"Verification command failed: {command[0]}, exit {result.returncode}")
        return result, output

    created = False
    try:
        run([
            "docker", "run", "-d", "--name", NAME, "--label", LABEL,
            "-p", "127.0.0.1::5432", "--tmpfs", "/var/lib/postgresql",
            "-e", "POSTGRES_PASSWORD", "-e", "POSTGRES_DB", "-e", "POSTGRES_USER",
            "-e", "EDUOPS_RUNTIME_PASSWORD", "-e", "EDUOPS_AUDIT_WORKER_PASSWORD",
            "--mount", f"type=bind,source={ROOT / 'infra/postgres/init'},target=/docker-entrypoint-initdb.d,readonly",
            "postgres:18",
        ])
        created = True
        for _ in range(100):
            result, _ = run([
                "docker", "exec", NAME, "pg_isready", "-h", "127.0.0.1",
                "-U", "eduops_migrator", "-d", "eduops360",
            ], check=False)
            if result.returncode == 0:
                break
            time.sleep(0.2)
        else:
            raise RuntimeError("Disposable PostgreSQL did not become ready")
        result, _ = run(["docker", "inspect", "--format", "{{json .NetworkSettings.Ports}}", NAME])
        port = json.loads(result.stdout)["5432/tcp"][0]["HostPort"]
        for key, role, password_key in (
            ("EDUOPS_TEST_MIGRATOR_DSN", "eduops_migrator", "POSTGRES_PASSWORD"),
            ("EDUOPS_TEST_RUNTIME_DSN", "eduops_runtime", "EDUOPS_RUNTIME_PASSWORD"),
            ("EDUOPS_TEST_AUDIT_WORKER_DSN", "eduops_audit_worker", "EDUOPS_AUDIT_WORKER_PASSWORD"),
        ):
            env[key] = f"postgresql://{role}:{passwords[password_key]}@127.0.0.1:{port}/eduops360"
        env["EDUOPS_DATABASE_URL"] = env["EDUOPS_TEST_MIGRATOR_DSN"].replace(
            "postgresql://", "postgresql+psycopg://", 1
        )
        for command in (
            [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"],
            [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "check"],
            [sys.executable, "-m", "pytest", "backend/tests", "-q"],
        ):
            result, output = run(command)
            print(output.strip())
            print(f"step exit={result.returncode}")
    finally:
        if created:
            result, _ = run([
                "docker", "inspect", "--format", '{{index .Config.Labels "eduops.audit"}}', NAME
            ])
            if result.stdout.strip() != "EDU-0068":
                raise RuntimeError("Container cleanup label mismatch")
            run(["docker", "rm", "-f", "-v", NAME])
            print("Disposable task container and storage removed")


if __name__ == "__main__":
    main()
