"""Verify the Railway image against task-owned disposable Docker resources."""

import base64
import json
import os
import secrets
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PREFIX = "eduops-edu0069-smoke"
IMAGE = "eduops360-online:edu0069"


def main():
    env = os.environ.copy()
    env.update({
        "POSTGRES_PASSWORD": secrets.token_urlsafe(32),
        "STAGING_RUNTIME_PASSWORD": secrets.token_urlsafe(32),
        "STAGING_AUDIT_WORKER_PASSWORD": secrets.token_urlsafe(32),
        "EDUOPS_PREVIEW_ACCESS_KEY": secrets.token_urlsafe(32),
        "POSTGRES_USER": "eduops_migrator", "POSTGRES_DB": "eduops360",
    })
    created = []

    def run(args):
        result = subprocess.run(["docker", *args], env=env, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"Docker verification step failed ({args[0]}); output withheld")
        return result.stdout.strip()

    for kind, name in (("network", PREFIX), ("container", PREFIX + "-db"), ("container", PREFIX + "-web")):
        if subprocess.run(["docker", kind, "inspect", name], capture_output=True).returncode == 0:
            raise RuntimeError("Refusing to reuse existing task resource")
    network_created = False
    try:
        run(["network", "create", "--label", "eduops.audit=EDU-0069", PREFIX])
        network_created = True
        run(["run", "-d", "--name", PREFIX + "-db", "--label", "eduops.audit=EDU-0069",
             "--network", PREFIX, "--tmpfs", "/var/lib/postgresql", "-e", "POSTGRES_PASSWORD",
             "-e", "POSTGRES_USER", "-e", "POSTGRES_DB", "postgres:18"])
        created.append(PREFIX + "-db")
        for _ in range(100):
            check = subprocess.run(["docker", "exec", PREFIX + "-db", "pg_isready", "-h", "127.0.0.1",
                                    "-U", "eduops_migrator", "-d", "eduops360"], capture_output=True)
            if check.returncode == 0:
                break
            time.sleep(0.2)
        else:
            raise RuntimeError("Synthetic PostgreSQL not ready")
        host = PREFIX + "-db"
        env["EDUOPS_DATABASE_URL"] = f"postgresql+psycopg://eduops_migrator:{env['POSTGRES_PASSWORD']}@{host}/eduops360"
        migrate = ["run", "--rm", "--network", PREFIX, "-e", "EDUOPS_DATABASE_URL",
                   "-e", "STAGING_RUNTIME_PASSWORD", "-e", "STAGING_AUDIT_WORKER_PASSWORD",
                   IMAGE, "python", "-m", "app.staging_migrate"]
        run(migrate)
        run(migrate)  # Existing roles: check, do not recreate or rotate them.
        env["EDUOPS_DATABASE_URL"] = f"postgresql+psycopg://eduops_runtime:{env['STAGING_RUNTIME_PASSWORD']}@{host}/eduops360"
        env.update(EDUOPS_ENVIRONMENT="staging", EDUOPS_CORS_ORIGINS="[]",
                   EDUOPS_ALLOWED_HOSTS='["preview.example.test","healthcheck.railway.app"]', PORT="8765")
        run(["run", "-d", "--name", PREFIX + "-web", "--label", "eduops.audit=EDU-0069",
             "--network", PREFIX, "-p", "127.0.0.1::8765", "-e", "EDUOPS_DATABASE_URL",
             "-e", "EDUOPS_ENVIRONMENT", "-e", "EDUOPS_CORS_ORIGINS", "-e", "EDUOPS_ALLOWED_HOSTS",
             "-e", "EDUOPS_PREVIEW_ACCESS_KEY", "-e", "PORT", IMAGE])
        created.append(PREFIX + "-web")
        ports = json.loads(run(["inspect", "--format", "{{json .NetworkSettings.Ports}}", PREFIX + "-web"]))
        port = ports["8765/tcp"][0]["HostPort"]

        def request(path, *, authenticated=False, host="preview.example.test"):
            headers = {"Host": host}
            if authenticated:
                headers["Authorization"] = "Basic " + base64.b64encode(
                    f"preview:{env['EDUOPS_PREVIEW_ACCESS_KEY']}".encode()).decode()
            try:
                response = urllib.request.urlopen(urllib.request.Request(
                    f"http://127.0.0.1:{port}{path}", headers=headers), timeout=3)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                return response.status, response.read().decode()

        for _ in range(100):
            try:
                if request("/api/v1/health/ready", host="healthcheck.railway.app")[0] == 200:
                    break
            except (OSError, urllib.error.URLError):
                pass
            time.sleep(0.2)
        else:
            raise RuntimeError("Image readiness failed")
        assert request("/")[0] == 401
        status, html = request("/", authenticated=True)
        assert status == 200 and '<div id="root">' in html
        assert request("/users", authenticated=True)[0] == 200
        assert request("/api/v1/missing", authenticated=True)[0] == 404
        assert request("/api/v1/health/live", host="attacker.invalid")[0] == 400
        print("PASS: migrations twice, runtime DB readiness, injected PORT, preview gate, SPA, API 404, host rejection")
    finally:
        for name in reversed(created):
            label = run(["inspect", "--format", '{{index .Config.Labels "eduops.audit"}}', name])
            if label != "EDU-0069":
                raise RuntimeError("Cleanup label mismatch")
            run(["rm", "-f", "-v", name])
        if network_created:
            run(["network", "rm", PREFIX])
        print("Task containers/storage/network removed; no online deployment performed")


if __name__ == "__main__":
    main()
