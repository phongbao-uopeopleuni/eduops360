from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db_session
from app.modules.academic_data.models import (
    Assessment,
    Attendance,
    Subject,
    Teacher,
    TeachingAssignment,
)
from app.modules.academic_data.schemas import (
    AssessmentRead,
    AttendanceRead,
    SubjectRead,
    TeacherRead,
    TeachingAssignmentRead,
)
from app.modules.auth.constants import ActionType, ResourceType
from app.modules.auth.guards import (
    AuthorizationContext,
    enforce_permission,
    get_csrf_authorization_context,
)
from app.modules.auth.permissions import Scope

router = APIRouter(prefix="/admin/academic-data", tags=["Academic Data"])
ReadGuard = Annotated[AuthorizationContext, Depends(get_csrf_authorization_context)]
Db = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/subjects", response_model=list[SubjectRead])
async def list_subjects(ctx: ReadGuard, db: Db, school_id: UUID | None = None):
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.READ,
        scope=Scope(school_id=school_id),
    )
    query = select(Subject).order_by(Subject.source_id, Subject.id)
    if school_id:
        query = query.where(Subject.school_id == school_id)
    return (await db.execute(query)).scalars().all()


@router.get("/teachers", response_model=list[TeacherRead])
async def list_teachers(
    ctx: ReadGuard,
    db: Db,
    school_id: UUID | None = None,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.READ,
        scope=Scope(school_id=school_id),
    )
    query = select(Teacher).order_by(Teacher.source_id, Teacher.id).limit(limit).offset(offset)
    if school_id:
        query = query.where(Teacher.school_id == school_id)
    return (await db.execute(query)).scalars().all()


@router.get("/teaching-assignments", response_model=list[TeachingAssignmentRead])
async def list_teaching_assignments(
    ctx: ReadGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
    limit: int = Query(200, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.READ,
        scope=Scope(school_id=school_id, academic_year_id=academic_year_id),
    )
    query = (
        select(TeachingAssignment)
        .order_by(TeachingAssignment.semester, TeachingAssignment.id)
        .limit(limit)
        .offset(offset)
    )
    if school_id:
        query = query.where(TeachingAssignment.school_id == school_id)
    if academic_year_id:
        query = query.where(TeachingAssignment.academic_year_id == academic_year_id)
    return (await db.execute(query)).scalars().all()


@router.get("/assessments", response_model=list[AssessmentRead])
async def list_assessments(
    ctx: ReadGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
    student_id: UUID | None = None,
    limit: int = Query(200, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.GRADE,
        action=ActionType.READ,
        scope=Scope(school_id=school_id, academic_year_id=academic_year_id),
    )
    query = (
        select(Assessment)
        .order_by(Assessment.student_id, Assessment.subject_id, Assessment.id)
        .limit(limit)
        .offset(offset)
    )
    if school_id:
        query = query.where(Assessment.school_id == school_id)
    if academic_year_id:
        query = query.where(Assessment.academic_year_id == academic_year_id)
    if student_id:
        query = query.where(Assessment.student_id == student_id)
    return (await db.execute(query)).scalars().all()


@router.get("/attendance", response_model=list[AttendanceRead])
async def list_attendance(
    ctx: ReadGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
    student_id: UUID | None = None,
    limit: int = Query(200, ge=1, le=2000),
    offset: int = Query(0, ge=0),
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.READ,
        scope=Scope(school_id=school_id, academic_year_id=academic_year_id),
    )
    query = (
        select(Attendance)
        .order_by(Attendance.attendance_date, Attendance.id)
        .limit(limit)
        .offset(offset)
    )
    if school_id:
        query = query.where(Attendance.school_id == school_id)
    if academic_year_id:
        query = query.where(Attendance.academic_year_id == academic_year_id)
    if student_id:
        query = query.where(Attendance.student_id == student_id)
    return (await db.execute(query)).scalars().all()
