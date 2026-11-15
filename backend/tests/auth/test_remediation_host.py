"""Host-level regressions for EDU-0032 (A0102-F02, A0102-F07); no database required.

The login route runs against a minimal in-memory stand-in for ``AsyncSession`` so the
tests observe exactly what the route would persist and on which thread it hashes.
"""

from __future__ import annotations

import asyncio
import threading
import time
from datetime import UTC, datetime
from uuid import uuid4

from argon2.exceptions import VerifyMismatchError
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.event_loop import create_event_loop
from app.db.dependencies import get_db_session
from app.main import create_app
from app.modules.audit_logs.models import AuditLog
from app.modules.audit_logs.service import write_audit_in_transaction
from app.modules.auth import services
from app.modules.auth.models import Session, User

USER_AGENT_COLUMN_LENGTH = 500
LONG_USER_AGENT = "Mozilla/5.0 " + "A" * 600
PASSWORD = "Synthetic-Password-123!"


class _Result:
    def __init__(self, value: object) -> None:
        self._value = value

    def scalar_one_or_none(self) -> object:
        return self._value


class FakeDbSession:
    """Records ORM objects the route adds and the thread that awaits database calls."""

    def __init__(self, user: User | None = None) -> None:
        self.user = user
        self.added: list[object] = []
        self.execute_threads: list[int] = []

    async def execute(self, _statement: object) -> _Result:
        self.execute_threads.append(threading.get_ident())
        return _Result(self.user)

    def add(self, obj: object) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


class RecordingHasher:
    """Stand-in for the Argon2 hasher that records concurrency and calling thread."""

    def __init__(self, delay: float = 0.0) -> None:
        self.delay = delay
        self.threads: list[int] = []
        self.active = 0
        self.max_concurrent = 0
        self._lock = threading.Lock()

    def _enter(self) -> None:
        with self._lock:
            self.threads.append(threading.get_ident())
            self.active += 1
            self.max_concurrent = max(self.max_concurrent, self.active)
        if self.delay:
            time.sleep(self.delay)
        with self._lock:
            self.active -= 1

    def verify(self, _password_hash: str, _password: str) -> bool:
        self._enter()
        raise VerifyMismatchError

    def hash(self, password: str) -> str:
        self._enter()
        return f"recorded:{password}"

    def check_needs_rehash(self, _password_hash: str) -> bool:
        return False


def _app_with(db: FakeDbSession):
    app = create_app(Settings(database_url=None, environment="test", _env_file=None))

    async def override_db():
        yield db

    app.dependency_overrides[get_db_session] = override_db
    return app


def _client(app) -> TestClient:
    return TestClient(
        app,
        base_url="https://testserver",
        backend_options={"loop_factory": create_event_loop},
    )


def _active_user() -> User:
    return User(
        id=uuid4(),
        email="host-login@example.com",
        display_name="Synthetic Host Login",
        password_hash=services.hash_password(PASSWORD),
        status="active",
        mfa_enabled=False,
        failed_login_count=0,
        created_at=datetime.now(UTC),
    )


def test_failed_login_audit_bounds_long_user_agent_to_column_length() -> None:
    """A0102-F02: an oversized header must not reach the VARCHAR(500) audit column."""
    db = FakeDbSession(user=None)
    with _client(_app_with(db)) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong-password"},
            headers={"User-Agent": LONG_USER_AGENT},
        )
    assert response.status_code == 401
    audits = [obj for obj in db.added if isinstance(obj, AuditLog)]
    assert len(audits) == 1
    assert audits[0].user_agent == LONG_USER_AGENT[:USER_AGENT_COLUMN_LENGTH]


def test_successful_login_bounds_session_and_audit_user_agent() -> None:
    """A0102-F02: the session row and login audit both receive the bounded value."""
    db = FakeDbSession(user=_active_user())
    with _client(_app_with(db)) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "host-login@example.com", "password": PASSWORD},
            headers={"User-Agent": LONG_USER_AGENT},
        )
    assert response.status_code == 200
    sessions = [obj for obj in db.added if isinstance(obj, Session)]
    audits = [obj for obj in db.added if isinstance(obj, AuditLog)]
    assert len(sessions) == 1
    assert sessions[0].user_agent == LONG_USER_AGENT[:USER_AGENT_COLUMN_LENGTH]
    assert audits and all(
        audit.user_agent == LONG_USER_AGENT[:USER_AGENT_COLUMN_LENGTH] for audit in audits
    )


def test_audit_writer_bounds_user_agent_for_every_caller() -> None:
    """A0102-F02: the shared audit writer itself never emits an over-length header."""
    db = FakeDbSession()

    async def write() -> AuditLog:
        return await write_audit_in_transaction(
            db,
            action="session:login_failed",
            resource_type="session",
            user_agent=LONG_USER_AGENT,
        )

    audit = asyncio.run(write(), loop_factory=create_event_loop)
    assert audit.user_agent == LONG_USER_AGENT[:USER_AGENT_COLUMN_LENGTH]


def test_login_password_verification_runs_off_the_event_loop_thread(monkeypatch) -> None:
    """A0102-F07: Argon2 verification must not execute on the event-loop thread."""
    hasher = RecordingHasher()
    monkeypatch.setattr(services, "_password_hasher", hasher)
    db = FakeDbSession(user=None)
    with _client(_app_with(db)) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong-password"},
        )
    assert response.status_code == 401
    assert hasher.threads, "password verification was not invoked"
    loop_thread = db.execute_threads[0]
    assert all(thread != loop_thread for thread in hasher.threads)


def test_password_hashing_concurrency_is_bounded(monkeypatch) -> None:
    """A0102-F07: concurrent Argon2 work is capped so memory/CPU stay bounded."""
    hasher = RecordingHasher(delay=0.05)
    monkeypatch.setattr(services, "_password_hasher", hasher)
    limit = services.PASSWORD_HASH_CONCURRENCY

    async def run_many() -> None:
        await asyncio.gather(
            *(services.verify_password_async("candidate", "stored") for _ in range(limit)),
            *(services.hash_password_async("candidate") for _ in range(limit * 2)),
        )

    asyncio.run(run_many(), loop_factory=create_event_loop)
    assert len(hasher.threads) == limit * 3
    assert 1 < hasher.max_concurrent <= limit
