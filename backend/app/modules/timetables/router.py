"""API router for bounded timetable CP-SAT jobs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, date, datetime, timedelta
from functools import partial
from typing import Annotated
from uuid import UUID

from anyio import CancelScope, CapacityLimiter, get_cancelled_exc_class, to_thread
from anyio.lowlevel import RunVar
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.dependencies import get_db_session
from app.modules.academic_years.models import AcademicYear, School
from app.modules.audit_logs.service import write_audit_in_transaction
from app.modules.auth.constants import ActionType, ResourceType
from app.modules.auth.guards import (
    AuthorizationContext,
    enforce_permission,
    get_csrf_authorization_context,
)
from app.modules.auth.permissions import Scope
from app.modules.school_calendar.models import ScheduleSlot, ScheduleTemplate, SchoolHoliday
from app.modules.timetables.models import TimetableJob, TimetableVersion
from app.modules.timetables.schemas import (
    TimetableJobCreate,
    TimetableJobRead,
    TimetableVersionRead,
)

router = APIRouter(prefix="/admin/timetables", tags=["Timetables"])

WriteGuard = Annotated[AuthorizationContext, Depends(get_csrf_authorization_context)]
Db = Annotated[AsyncSession, Depends(get_db_session)]
TIMETABLE_SOLVER_CONCURRENT_LIMIT = 2
_solver_limiter: RunVar[CapacityLimiter] = RunVar("eduops_timetable_solver_limiter")


def _current_solver_limiter() -> CapacityLimiter:
    try:
        return _solver_limiter.get()
    except LookupError:
        limiter = CapacityLimiter(TIMETABLE_SOLVER_CONCURRENT_LIMIT)
        _solver_limiter.set(limiter)
        return limiter


def _closed_slot_ids(
    template_slots: tuple[ScheduleSlot, ...],
    holidays: tuple[SchoolHoliday, ...],
    year_start: date,
    year_end: date,
) -> frozenset[str]:
    closed_weekdays: set[int] = set()
    for holiday in holidays:
        start = max(holiday.start_date, year_start)
        end = min(holiday.end_date, year_end)
        current = start
        while current <= end:
            closed_weekdays.add(current.isoweekday())
            current += timedelta(days=1)
    return frozenset(str(slot.id) for slot in template_slots if slot.weekday in closed_weekdays)


def _minutes(value: object) -> int:
    hour, minute = value.hour, value.minute
    return hour * 60 + minute


@router.post("/jobs", response_model=TimetableJobRead, status_code=201)
async def create_timetable_job(
    body: TimetableJobCreate,
    ctx: WriteGuard,
    db: Db,
):
    from app.modules.timetables.solver import (
        AvailableSlot,
        Snapshot,
        SolverStatus,
        TeachingAssignment,
        solve_timetable,
    )

    scope = Scope(
        school_id=body.school_id,
        academic_year_id=body.academic_year_id,
    )
    enforce_permission(
        ctx,
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.CREATE,
        scope=scope,
    )
    school = await db.get(School, body.school_id)
    year = await db.get(AcademicYear, body.academic_year_id)
    if not school:
        raise AppError(404, "SCHOOL_NOT_FOUND", "Không tìm thấy trường.")
    if not year:
        raise AppError(404, "YEAR_NOT_FOUND", "Không tìm thấy năm học.")
    if year.school_id != body.school_id:
        raise AppError(422, "SCHOOL_MISMATCH", "Năm học không thuộc trường đã chọn.")

    active_templates = (
        (
            await db.execute(
                select(ScheduleTemplate).where(
                    ScheduleTemplate.school_id == body.school_id,
                    ScheduleTemplate.academic_year_id == body.academic_year_id,
                    ScheduleTemplate.status == "active",
                )
            )
        )
        .scalars()
        .all()
    )
    if len(active_templates) == 0:
        raise AppError(
            422,
            "ACTIVE_TEMPLATE_NOT_FOUND",
            "Không có schedule template active duy nhất cho trường và năm học.",
        )
    if len(active_templates) > 1:
        raise AppError(
            422,
            "AMBIGUOUS_ACTIVE_TEMPLATE",
            "Có nhiều schedule template active cho trường và năm học.",
        )

    template = active_templates[0]
    template_slots = (
        (
            await db.execute(
                select(ScheduleSlot)
                .where(ScheduleSlot.template_id == template.id)
                .order_by(ScheduleSlot.weekday, ScheduleSlot.slot_order)
            )
        )
        .scalars()
        .all()
    )
    if not template_slots:
        raise AppError(
            422,
            "ACTIVE_TEMPLATE_HAS_NO_SLOTS",
            "Schedule template active không có tiết nào.",
        )

    active_holidays = (
        (
            await db.execute(
                select(SchoolHoliday).where(
                    SchoolHoliday.school_id == body.school_id,
                    SchoolHoliday.academic_year_id == body.academic_year_id,
                    SchoolHoliday.status == "active",
                    SchoolHoliday.start_date <= year.end_date,
                    SchoolHoliday.end_date >= year.start_date,
                )
            )
        )
        .scalars()
        .all()
    )
    closed_slots = _closed_slot_ids(
        tuple(template_slots),
        tuple(active_holidays),
        year.start_date,
        year.end_date,
    )

    snapshot_payload = body.model_dump(mode="json")
    snapshot_payload["slots"] = [
        {
            "slot_id": str(slot.id),
            "weekday": slot.weekday,
            "start_minute": _minutes(slot.start_time),
            "end_minute": _minutes(slot.end_time),
        }
        for slot in template_slots
    ]
    snapshot_payload["closed_slot_ids"] = sorted(closed_slots)
    snapshot_checksum = hashlib.sha256(
        json.dumps(snapshot_payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    snapshot = Snapshot(
        school_id=str(body.school_id),
        academic_year_id=str(body.academic_year_id),
        assignments=tuple(
            TeachingAssignment(
                assignment_id=item.assignment_id,
                teacher_id=item.teacher_id,
                class_id=item.class_id,
                subject_id=item.subject_id,
                room_id=item.room_id,
                required_lessons=item.required_lessons,
            )
            for item in body.assignments
        ),
        slots=tuple(
            AvailableSlot(
                slot_id=str(slot.id),
                weekday=slot.weekday,
                start_minute=_minutes(slot.start_time),
                end_minute=_minutes(slot.end_time),
            )
            for slot in template_slots
        ),
        closed_slots=closed_slots,
    )

    job = TimetableJob(
        school_id=body.school_id,
        academic_year_id=body.academic_year_id,
        actor_id=ctx.auth.user.id,
        status="running",
        snapshot_checksum=snapshot_checksum,
        snapshot=snapshot_payload,
        result={},
        time_limit_seconds=body.time_limit_seconds,
        started_at=datetime.now(UTC),
    )
    db.add(job)
    await db.flush()

    try:
        solver_status, entries, evidence = await to_thread.run_sync(
            partial(
                solve_timetable,
                snapshot,
                time_limit_seconds=float(body.time_limit_seconds),
                random_seed=body.random_seed,
            ),
            limiter=_current_solver_limiter(),
            abandon_on_cancel=False,
        )
    except get_cancelled_exc_class():
        with CancelScope(shield=True):
            job.status = "cancelled"
            job.completed_at = datetime.now(UTC)
            job.error = "SOLVER_CANCELLED"
            try:
                await db.commit()
            except IntegrityError:
                await db.rollback()
                job.status = "failed"
                job.solver_status = SolverStatus.UNKNOWN
                job.error = "TIMETABLE_REVISION_CONFLICT"
                db.add(job)
                await db.commit()
        raise
    job.solver_status = solver_status
    job.completed_at = datetime.now(UTC)
    entry_payload = [
        {
            "assignment_id": entry.assignment_id,
            "teacher_id": entry.teacher_id,
            "class_id": entry.class_id,
            "subject_id": entry.subject_id,
            "room_id": entry.room_id,
            "slot_id": entry.slot_id,
            "weekday": entry.weekday,
            "start_minute": entry.start_minute,
            "end_minute": entry.end_minute,
        }
        for entry in entries
    ]
    job.result = evidence | {"entries": entry_payload}

    if solver_status in {SolverStatus.OPTIMAL, SolverStatus.FEASIBLE}:
        job.status = "completed"
        version_count = (
            await db.execute(
                select(TimetableVersion)
                .where(
                    TimetableVersion.school_id == body.school_id,
                    TimetableVersion.academic_year_id == body.academic_year_id,
                )
                .order_by(TimetableVersion.revision.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        revision = 1 if version_count is None else version_count.revision + 1
        db.add(
            TimetableVersion(
                school_id=body.school_id,
                academic_year_id=body.academic_year_id,
                job_id=job.id,
                revision=revision,
                status="draft",
                entries=entry_payload,
            )
        )
    elif solver_status == SolverStatus.INFEASIBLE:
        job.status = "completed"
    else:
        job.status = "failed"
        job.error = evidence.get("reason")

    await write_audit_in_transaction(
        db,
        action="solve",
        resource_type=ResourceType.TIMETABLE,
        resource_id=str(job.id),
        actor_id=ctx.auth.user.id,
        actor_email=getattr(ctx.auth.user, "email", None),
        extra_data={
            "school_id": str(body.school_id),
            "academic_year_id": str(body.academic_year_id),
            "snapshot_checksum": snapshot_checksum,
            "solver_status": job.solver_status,
            "time_limit_seconds": body.time_limit_seconds,
        },
        create_outbox=True,
    )
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/jobs", response_model=list[TimetableJobRead])
async def list_timetable_jobs(
    ctx: WriteGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.READ,
        scope=Scope(school_id=school_id, academic_year_id=academic_year_id),
    )
    query = select(TimetableJob).order_by(TimetableJob.created_at.desc()).limit(100)
    if school_id is not None:
        query = query.where(TimetableJob.school_id == school_id)
    if academic_year_id is not None:
        query = query.where(TimetableJob.academic_year_id == academic_year_id)
    jobs = (await db.execute(query)).scalars().all()
    return jobs


@router.get("/versions", response_model=list[TimetableVersionRead])
async def list_timetable_versions(
    ctx: WriteGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.READ,
        scope=Scope(school_id=school_id, academic_year_id=academic_year_id),
    )
    query = select(TimetableVersion).order_by(
        TimetableVersion.academic_year_id,
        TimetableVersion.revision.desc(),
    )
    if school_id is not None:
        query = query.where(TimetableVersion.school_id == school_id)
    if academic_year_id is not None:
        query = query.where(TimetableVersion.academic_year_id == academic_year_id)
    versions = (await db.execute(query)).scalars().all()
    return versions
