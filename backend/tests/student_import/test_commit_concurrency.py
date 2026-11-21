"""Concurrent import commit checks against an isolated synthetic PostgreSQL database."""

from __future__ import annotations

import asyncio
import os
from contextlib import closing
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from fastapi import Request
from psycopg.types.json import Jsonb
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.event_loop import create_event_loop
from app.modules.students import router as student_router

MIGRATOR_DSN = os.getenv("EDUOPS_TEST_MIGRATOR_DSN")
RUNTIME_DSN = os.getenv("EDUOPS_TEST_RUNTIME_DSN")

pytestmark = pytest.mark.skipif(
    not all((MIGRATOR_DSN, RUNTIME_DSN)),
    reason="isolated PostgreSQL student import DSNs are not configured",
)


def _insert_fixture(
    *,
    school_id,
    academic_year_id,
    class_id,
    student_id,
    batch_id,
    row_id,
    actor_id,
    student_code: str,
) -> None:
    assert MIGRATOR_DSN is not None
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as connection:
        connection.execute(
            "INSERT INTO schools (id, code, name) VALUES (%s, %s, %s)",
            (school_id, f"F03-{student_code}", "Synthetic F03 School"),
        )
        connection.execute(
            """
            INSERT INTO academic_years
                (id, school_id, name, start_date, end_date, status)
            VALUES (%s, %s, '2026-2027', '2026-09-01', '2027-06-30', 'active')
            """,
            (academic_year_id, school_id),
        )
        connection.execute(
            """
            INSERT INTO school_classes (id, school_id, academic_year_id, name, grade)
            VALUES (%s, %s, %s, '5A1', 5)
            """,
            (class_id, school_id, academic_year_id),
        )
        connection.execute(
            """
            INSERT INTO students (id, school_id, student_code, full_name, status)
            VALUES (%s, %s, %s, 'Synthetic Student', 'active')
            """,
            (student_id, school_id, student_code),
        )
        connection.execute(
            """
            INSERT INTO student_import_batches
                (id, school_id, academic_year_id, actor_id, idempotency_key, checksum,
                 original_filename, mode, state, counts)
            VALUES (%s, %s, %s, %s, %s, %s, 'synthetic.csv', 'create_only', 'ready', %s)
            """,
            (
                batch_id,
                school_id,
                academic_year_id,
                actor_id,
                f"f03-{student_code}",
                "0" * 64,
                Jsonb({"total": 1, "new": 1, "existing": 0, "conflicting": 0, "error": 0}),
            ),
        )
        connection.execute(
            """
            INSERT INTO student_import_rows
                (id, batch_id, row_number, student_code, status, normalized_values)
            VALUES (%s, %s, 2, %s, 'new', %s)
            """,
            (
                row_id,
                batch_id,
                student_code,
                Jsonb(
                    {
                        "full_name": "Synthetic Student",
                        "date_of_birth": "",
                        "gender": "",
                        "class_code": "5A1",
                    }
                ),
            ),
        )


def _delete_fixture(*, school_id, batch_id, student_id, class_id, academic_year_id) -> None:
    assert MIGRATOR_DSN is not None
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as connection:
        connection.execute(
            """
            DELETE FROM audit_outbox
            WHERE audit_log_id IN (
                SELECT id FROM audit_logs WHERE resource_id = %s AND action = 'commit'
            )
            """,
            (str(batch_id),),
        )
        connection.execute(
            "DELETE FROM audit_logs WHERE resource_id = %s AND action = 'commit'",
            (str(batch_id),),
        )
        connection.execute("DELETE FROM student_import_rows WHERE batch_id = %s", (batch_id,))
        connection.execute("DELETE FROM student_import_batches WHERE id = %s", (batch_id,))
        connection.execute("DELETE FROM enrollments WHERE student_id = %s", (student_id,))
        connection.execute("DELETE FROM students WHERE id = %s", (student_id,))
        connection.execute("DELETE FROM school_classes WHERE id = %s", (class_id,))
        connection.execute("DELETE FROM academic_years WHERE id = %s", (academic_year_id,))
        connection.execute("DELETE FROM schools WHERE id = %s", (school_id,))


def test_concurrent_commit_replays_after_single_transaction(monkeypatch) -> None:
    assert MIGRATOR_DSN is not None
    assert RUNTIME_DSN is not None
    school_id, year_id, class_id, student_id, batch_id, row_id, actor_id = (
        uuid4() for _ in range(7)
    )
    student_code = f"F03-{uuid4().hex}"
    _insert_fixture(
        school_id=school_id,
        academic_year_id=year_id,
        class_id=class_id,
        student_id=student_id,
        batch_id=batch_id,
        row_id=row_id,
        actor_id=actor_id,
        student_code=student_code,
    )

    async_url = RUNTIME_DSN.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_async_engine(async_url, pool_size=2, max_overflow=0)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    first_audit_started = asyncio.Event()
    release_first_audit = asyncio.Event()
    second_batch_select_started = asyncio.Event()
    second_batch_statements: list[str] = []
    audit_calls = 0
    original_audit_writer = student_router.write_audit_in_transaction

    async def pause_first_audit(session, **kwargs):
        nonlocal audit_calls
        audit_calls += 1
        if audit_calls == 1:
            first_audit_started.set()
            await release_first_audit.wait()
        return await original_audit_writer(session, **kwargs)

    def capture_second_batch_select(connection, _cursor, statement, _parameters, _context, _many):
        if (
            connection.info.get("test_session") == "second"
            and "student_import_batches" in statement.lower()
        ):
            second_batch_statements.append(statement)
            second_batch_select_started.set()

    monkeypatch.setattr(student_router, "enforce_permission", lambda *args, **kwargs: None)
    monkeypatch.setattr(student_router, "write_audit_in_transaction", pause_first_audit)
    event.listen(engine.sync_engine, "before_cursor_execute", capture_second_batch_select)

    request = Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "https",
            "path": f"/api/v1/admin/student-import/{batch_id}/commit",
            "raw_path": f"/api/v1/admin/student-import/{batch_id}/commit".encode(),
            "query_string": b"",
            "headers": [(b"user-agent", b"synthetic F03 test")],
            "client": ("127.0.0.1", 12345),
            "server": ("testserver", 443),
        }
    )
    context = SimpleNamespace(
        auth=SimpleNamespace(
            user=SimpleNamespace(id=actor_id, email="synthetic-f03@example.invalid")
        )
    )

    async def invoke(session):
        try:
            return await student_router.commit_student_import(
                batch_id=batch_id,
                request=request,
                ctx=context,
                db=session,
            )
        except Exception:
            await session.rollback()
            raise

    async def exercise_concurrent_commits():
        tasks = []
        try:
            async with session_factory() as first_session:
                first_task = asyncio.create_task(invoke(first_session))
                tasks.append(first_task)
                try:
                    await asyncio.wait_for(first_audit_started.wait(), timeout=10)
                except TimeoutError:
                    if first_task.done():
                        await first_task
                    raise

                async with session_factory() as second_session:
                    second_connection = await second_session.connection()
                    second_connection.sync_connection.info["test_session"] = "second"
                    second_task = asyncio.create_task(invoke(second_session))
                    tasks.append(second_task)
                    await asyncio.wait_for(second_batch_select_started.wait(), timeout=10)
                    second_statement = second_batch_statements[0]
                    release_first_audit.set()
                    outcomes = await asyncio.gather(*tasks, return_exceptions=True)
                    return second_statement, outcomes
        finally:
            release_first_audit.set()
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

    try:
        try:
            second_statement, outcomes = asyncio.run(
                exercise_concurrent_commits(), loop_factory=create_event_loop
            )
            assert "FOR UPDATE" in second_statement.upper()
            assert all(isinstance(outcome, dict) for outcome in outcomes), outcomes
            assert len(outcomes) == 2
            assert all(outcome["state"] == "committed" for outcome in outcomes)
            assert outcomes[0]["id"] == outcomes[1]["id"] == batch_id
            assert outcomes[0]["counts"] == outcomes[1]["counts"]
            assert audit_calls == 1

            with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as connection:
                assert connection.execute(
                    "SELECT count(*) FROM students WHERE id = %s", (student_id,)
                ).fetchone() == (1,)
                assert connection.execute(
                    "SELECT count(*) FROM enrollments "
                    "WHERE student_id = %s AND academic_year_id = %s",
                    (student_id, year_id),
                ).fetchone() == (1,)
                assert connection.execute(
                    "SELECT count(*) FROM audit_logs WHERE resource_id = %s AND action = 'commit'",
                    (str(batch_id),),
                ).fetchone() == (1,)
        finally:
            event.remove(engine.sync_engine, "before_cursor_execute", capture_second_batch_select)
            asyncio.run(engine.dispose(), loop_factory=create_event_loop)
    finally:
        _delete_fixture(
            school_id=school_id,
            batch_id=batch_id,
            student_id=student_id,
            class_id=class_id,
            academic_year_id=year_id,
        )
