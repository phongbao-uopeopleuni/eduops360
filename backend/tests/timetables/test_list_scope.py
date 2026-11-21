"""Live school/year scope checks against isolated synthetic PostgreSQL."""

from __future__ import annotations

import asyncio
import os
from contextlib import closing
from types import SimpleNamespace
from uuid import uuid4

import psycopg
import pytest
from psycopg.types.json import Jsonb
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.errors import AppError
from app.core.event_loop import create_event_loop
from app.modules.auth.constants import ActionType, ResourceType
from app.modules.auth.guards import AuthorizationContext
from app.modules.auth.permissions import Permission, Principal, Scope
from app.modules.timetables import router as timetable_router
from app.modules.timetables.schemas import TeachingAssignmentInput, TimetableJobCreate

MIGRATOR_DSN = os.getenv("EDUOPS_TEST_MIGRATOR_DSN")
RUNTIME_DSN = os.getenv("EDUOPS_TEST_RUNTIME_DSN")

pytestmark = pytest.mark.skipif(
    not all((MIGRATOR_DSN, RUNTIME_DSN)),
    reason="isolated PostgreSQL timetable scope DSNs are not configured",
)


def _insert_fixtures(schools, years, schedules, actor_id) -> None:
    assert MIGRATOR_DSN is not None
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as connection:
        for school_id, code in schools:
            connection.execute(
                "INSERT INTO schools (id, code, name) VALUES (%s, %s, %s)",
                (school_id, code, f"Synthetic {code}"),
            )
        for year_id, school_id, name in years:
            connection.execute(
                """
                INSERT INTO academic_years
                    (id, school_id, name, start_date, end_date, status)
                VALUES (%s, %s, %s, '2026-09-01', '2027-06-30', 'active')
                """,
                (year_id, school_id, name),
            )
        for job_id, version_id, school_id, year_id in schedules:
            connection.execute(
                """
                INSERT INTO timetable_jobs
                    (id, school_id, academic_year_id, actor_id, status,
                     snapshot_checksum, snapshot, result, time_limit_seconds)
                VALUES (%s, %s, %s, %s, 'queued', %s, %s, %s, 30)
                """,
                (job_id, school_id, year_id, actor_id, "a" * 64, Jsonb({}), Jsonb({})),
            )
            connection.execute(
                """
                INSERT INTO timetable_versions
                    (id, school_id, academic_year_id, job_id, revision, status, entries)
                VALUES (%s, %s, %s, %s, 1, 'draft', %s)
                """,
                (version_id, school_id, year_id, job_id, Jsonb([])),
            )


def _delete_fixtures(schools, years, schedules) -> None:
    assert MIGRATOR_DSN is not None
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as connection:
        for job_id, version_id, _, _ in schedules:
            connection.execute("DELETE FROM timetable_versions WHERE id = %s", (version_id,))
            connection.execute("DELETE FROM timetable_jobs WHERE id = %s", (job_id,))
        for year_id, _, _ in years:
            connection.execute("DELETE FROM academic_years WHERE id = %s", (year_id,))
        for school_id, _ in schools:
            connection.execute("DELETE FROM schools WHERE id = %s", (school_id,))


def _context(actor_id, scope: Scope) -> AuthorizationContext:
    permission = Permission(
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.READ,
        scope=scope,
    )
    return AuthorizationContext(
        auth=SimpleNamespace(user=SimpleNamespace(id=actor_id)),
        principal=Principal(user_id=actor_id, permissions=frozenset({permission})),
    )


def test_timetable_lists_filter_school_and_year_and_enforce_scope() -> None:
    assert MIGRATOR_DSN is not None
    assert RUNTIME_DSN is not None
    school_one, school_two = uuid4(), uuid4()
    year_one, year_two, year_three = uuid4(), uuid4(), uuid4()
    job_one, job_two, job_three = uuid4(), uuid4(), uuid4()
    version_one, version_two, version_three = uuid4(), uuid4(), uuid4()
    actor_id = uuid4()
    schools = ((school_one, f"F02-{uuid4().hex}"), (school_two, f"F02-{uuid4().hex}"))
    years = (
        (year_one, school_one, "2026-2027"),
        (year_two, school_one, "2027-2028"),
        (year_three, school_two, "2026-2027"),
    )
    schedules = (
        (job_one, version_one, school_one, year_one),
        (job_two, version_two, school_one, year_two),
        (job_three, version_three, school_two, year_three),
    )
    _insert_fixtures(schools, years, schedules, actor_id)
    engine = create_async_engine(
        RUNTIME_DSN.replace("postgresql://", "postgresql+psycopg://", 1),
        pool_size=1,
        max_overflow=0,
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def verify_lists() -> None:
        school_context = _context(actor_id, Scope(school_id=school_one))
        year_context = _context(
            actor_id,
            Scope(school_id=school_one, academic_year_id=year_one),
        )
        async with session_factory() as session:
            school_jobs = await timetable_router.list_timetable_jobs(
                school_context, session, school_id=school_one
            )
            school_versions = await timetable_router.list_timetable_versions(
                school_context, session, school_id=school_one
            )
            year_jobs = await timetable_router.list_timetable_jobs(
                year_context,
                session,
                school_id=school_one,
                academic_year_id=year_one,
            )
            year_versions = await timetable_router.list_timetable_versions(
                year_context,
                session,
                school_id=school_one,
                academic_year_id=year_one,
            )
            with pytest.raises(AppError):
                await timetable_router.list_timetable_jobs(
                    school_context, session, school_id=school_two
                )

        assert {job.id for job in school_jobs} == {job_one, job_two}
        assert {version.id for version in school_versions} == {version_one, version_two}
        assert {job.id for job in year_jobs} == {job_one}
        assert {version.id for version in year_versions} == {version_one}

    try:
        asyncio.run(verify_lists(), loop_factory=create_event_loop)
    finally:
        asyncio.run(engine.dispose(), loop_factory=create_event_loop)
        _delete_fixtures(schools, years, schedules)


def test_unique_active_template_index_rejects_duplicate_active_template() -> None:
    assert MIGRATOR_DSN is not None
    school_id, year_id = uuid4(), uuid4()
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=False)) as connection:
        try:
            connection.execute(
                "INSERT INTO schools (id, code, name) VALUES (%s, %s, %s)",
                (school_id, f"F04-{uuid4().hex}", "Synthetic F04 School"),
            )
            connection.execute(
                """
                INSERT INTO academic_years
                    (id, school_id, name, start_date, end_date, status)
                VALUES (%s, %s, '2026-2027', '2026-09-01', '2027-06-30', 'active')
                """,
                (year_id, school_id),
            )
            connection.execute(
                """
                INSERT INTO schedule_templates
                    (id, school_id, academic_year_id, name, status, revision)
                VALUES (%s, %s, %s, 'Template A', 'active', 1)
                """,
                (uuid4(), school_id, year_id),
            )
            with pytest.raises(psycopg.errors.UniqueViolation):
                connection.execute(
                    """
                    INSERT INTO schedule_templates
                        (id, school_id, academic_year_id, name, status, revision)
                    VALUES (%s, %s, %s, 'Template B', 'active', 1)
                    """,
                    (uuid4(), school_id, year_id),
                )
        finally:
            connection.rollback()
            connection.execute("DELETE FROM schedule_templates WHERE school_id = %s", (school_id,))
            connection.execute("DELETE FROM academic_years WHERE id = %s", (year_id,))
            connection.execute("DELETE FROM schools WHERE id = %s", (school_id,))


def test_create_timetable_job_uses_server_template_holiday_and_slots(monkeypatch) -> None:
    assert MIGRATOR_DSN is not None
    assert RUNTIME_DSN is not None
    school_id, year_id, actor_id = uuid4(), uuid4(), uuid4()
    template_id = uuid4()
    with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as connection:
        connection.execute(
            "INSERT INTO schools (id, code, name) VALUES (%s, %s, %s)",
            (school_id, f"F04-{uuid4().hex}", "Synthetic F04 Closure School"),
        )
        connection.execute(
            """
            INSERT INTO academic_years
                (id, school_id, name, start_date, end_date, status)
            VALUES (%s, %s, '2026-2027', '2026-09-01', '2027-06-30', 'active')
            """,
            (year_id, school_id),
        )
        connection.execute(
            """
            INSERT INTO schedule_templates
                (id, school_id, academic_year_id, name, status, revision)
            VALUES (%s, %s, %s, 'Server Template', 'active', 1)
            """,
            (template_id, school_id, year_id),
        )
        connection.execute(
            """
            INSERT INTO schedule_slots
                (id, template_id, weekday, label, period, start_time, end_time, slot_order)
            VALUES (%s, %s, 1, 'Monday 1', 'AM', '08:00', '08:45', 1)
            """,
            (uuid4(), template_id),
        )
        connection.execute(
            """
            INSERT INTO school_holidays
                (id, school_id, academic_year_id, name, start_date, end_date, status)
            VALUES (%s, %s, %s, 'Synthetic Monday Closure', '2026-09-07', '2026-09-14', 'active')
            """,
            (uuid4(), school_id, year_id),
        )

    async_url = RUNTIME_DSN.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_async_engine(async_url, pool_size=1, max_overflow=0)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async def no_audit(*args, **kwargs):
        return None

    monkeypatch.setattr(timetable_router, "enforce_permission", lambda *args, **kwargs: None)
    monkeypatch.setattr(timetable_router, "write_audit_in_transaction", no_audit)
    context = SimpleNamespace(
        auth=SimpleNamespace(
            user=SimpleNamespace(id=actor_id, email="synthetic-f04@example.invalid")
        )
    )
    body = TimetableJobCreate(
        school_id=school_id,
        academic_year_id=year_id,
        assignments=[
            TeachingAssignmentInput(
                assignment_id="assignment-1",
                teacher_id="teacher-1",
                class_id="class-1",
                subject_id="subject-1",
                room_id="room-1",
                required_lessons=1,
            )
        ],
        time_limit_seconds=10,
    )

    async def verify_create() -> dict:
        async with session_factory() as session:
            job = await timetable_router.create_timetable_job(body, context, session)
            snapshot = job.snapshot
            return snapshot

    try:
        snapshot = asyncio.run(verify_create(), loop_factory=create_event_loop)
        assert len(snapshot["slots"]) == 1
        assert len(snapshot["closed_slot_ids"]) == 1
    finally:
        asyncio.run(engine.dispose(), loop_factory=create_event_loop)
        with closing(psycopg.connect(MIGRATOR_DSN, autocommit=True)) as connection:
            connection.execute(
                "DELETE FROM timetable_versions WHERE school_id = %s",
                (school_id,),
            )
            connection.execute(
                "DELETE FROM timetable_jobs WHERE school_id = %s",
                (school_id,),
            )
            connection.execute("DELETE FROM school_holidays WHERE school_id = %s", (school_id,))
            connection.execute("DELETE FROM schedule_slots WHERE template_id = %s", (template_id,))
            connection.execute("DELETE FROM schedule_templates WHERE id = %s", (template_id,))
            connection.execute("DELETE FROM academic_years WHERE id = %s", (year_id,))
            connection.execute("DELETE FROM schools WHERE id = %s", (school_id,))
