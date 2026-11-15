"""EDU-0042: concurrent TOTP replay with one app instance per worker (synthetic data only).

The first probe shared one FastAPI app between two TestClients; both lifespans overwrite
app.state.database, so one request used an engine bound to the other thread's event loop
and hung. This version gives each worker its own app, like two server processes.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import struct
import threading
import time
from contextlib import closing
from pathlib import Path
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.event_loop import create_event_loop
from app.main import create_app
from app.modules.auth.services import hash_password

MIGRATOR_DSN = os.environ["EDUOPS_TEST_MIGRATOR_DSN"]
RUNTIME_SQLA = os.environ["EDUOPS_TEST_RUNTIME_DSN"].replace(
    "postgresql://", "postgresql+psycopg://", 1
)
SECRET = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
PASSWORD = "Synthetic-Password-123!"
RUN = uuid4().hex[:10]


def totp(timestamp: int) -> str:
    key = base64.b32decode(SECRET)
    digest = hmac.new(key, struct.pack(">Q", timestamp // 30), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    value = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return f"{value % 1_000_000:06d}"


def main() -> dict:
    attempts = []
    for attempt in range(5):
        email = f"rd2-mfa-{attempt}-{RUN}@example.com"
        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as c:
            c.execute(
                "INSERT INTO users (id, email, password_hash, display_name, status, "
                "mfa_enabled, mfa_secret) VALUES (%s, %s, %s, 'Synthetic EDU-0042 MFA', "
                "'active', TRUE, %s)",
                (uuid4(), email, hash_password(PASSWORD), SECRET),
            )
        if int(time.time()) % 30 > 24:
            time.sleep(31 - int(time.time()) % 30)
        code = totp(int(time.time()))
        clients = []
        for _ in range(2):
            app = create_app(
                Settings(database_url=RUNTIME_SQLA, environment="test", _env_file=None)
            )
            client = TestClient(
                app,
                base_url="https://testserver",
                backend_options={"loop_factory": create_event_loop},
                raise_server_exceptions=False,
            )
            client.__enter__()
            clients.append(client)
        barrier = threading.Barrier(2)
        statuses: list[int] = []
        lock = threading.Lock()

        def worker(client: TestClient) -> None:
            barrier.wait()
            response = client.post(
                "/api/v1/auth/login",
                json={"email": email, "password": PASSWORD, "mfa_code": code},
            )
            with lock:
                statuses.append(response.status_code)

        threads = [threading.Thread(target=worker, args=(c,)) for c in clients]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(60)
        for client in clients:
            client.__exit__(None, None, None)
        attempts.append(sorted(statuses))
    return {
        "statuses_per_attempt": attempts,
        "all_attempts_complete": all(len(a) == 2 for a in attempts),
        "max_successes_in_any_attempt": max(a.count(200) for a in attempts),
    }


if __name__ == "__main__":
    started = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    result = {"started_at": started, "run": RUN, "result": main()}
    Path(__file__).with_name("probe_totp_race.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
