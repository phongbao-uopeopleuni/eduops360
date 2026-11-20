"""API router for bounded timetable CP-SAT jobs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
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
from app.modules.timetables.models import TimetableJob, TimetableVersion
from app.modules.timetables.schemas import (
    TimetableJobCreate,
    TimetableJobRead,
    TimetableVersionRead,
)
from app.modules.timetables.solver import (
    AvailableSlot,
    Snapshot,
    SolverStatus,
    TeachingAssignment,
    solve_timetable,
)

router = APIRouter(prefix="/admin/timetables", tags=["Timetables"])

WriteGuard = Annotated[AuthorizationContext, Depends(get_csrf_authorization_context)]
Db = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/jobs", response_model=TimetableJobRead, status_code=201)
async def create_timetable_job(
    body: TimetableJobCreate,
    ctx: WriteGuard,
    db: Db,
):
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

    snapshot_payload = body.model_dump(mode="json")
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
                slot_id=item.slot_id,
                weekday=item.weekday,
                start_minute=item.start_minute,
                end_minute=item.end_minute,
            )
            for item in body.slots
        ),
        closed_slots=frozenset(body.closed_slot_ids),
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

    solver_status, entries, evidence = solve_timetable(
        snapshot,
        time_limit_seconds=float(body.time_limit_seconds),
        random_seed=body.random_seed,
    )
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
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.READ,
        scope=Scope(),
    )
    jobs = (
        (await db.execute(select(TimetableJob).order_by(TimetableJob.created_at.desc()).limit(100)))
        .scalars()
        .all()
    )
    return jobs


@router.get("/versions", response_model=list[TimetableVersionRead])
async def list_timetable_versions(
    ctx: WriteGuard,
    db: Db,
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.READ,
        scope=Scope(),
    )
    versions = (
        (
            await db.execute(
                select(TimetableVersion).order_by(
                    TimetableVersion.academic_year_id,
                    TimetableVersion.revision.desc(),
                )
            )
        )
        .scalars()
        .all()
    )
    return versions
