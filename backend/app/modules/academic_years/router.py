"""API router for schools and academic years management."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.dependencies import get_db_session
from app.modules.academic_years.domain import (
    AcademicYearStatus,
    DateWindow,
    ensure_academic_year_transition,
    ensure_year_mutable,
    validate_term_window,
)
from app.modules.academic_years.models import AcademicTerm, AcademicYear, School
from app.modules.academic_years.schemas import (
    AcademicTermCreate,
    AcademicTermRead,
    AcademicYearCreate,
    AcademicYearRead,
    AcademicYearStatusUpdate,
    AcademicYearUpdate,
    SchoolCreate,
    SchoolRead,
    SchoolUpdate,
)
from app.modules.auth.constants import ActionType, ResourceType
from app.modules.auth.guards import (
    AuthorizationContext,
    enforce_permission,
    get_csrf_authorization_context,
)
from app.modules.auth.permissions import Scope

router = APIRouter(prefix="/admin", tags=["Academic Year Management"])

WriteGuard = Annotated[AuthorizationContext, Depends(get_csrf_authorization_context)]
Db = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/schools", response_model=list[SchoolRead])
async def list_schools(ctx: WriteGuard, db: Db):
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.READ, scope=Scope())
    result = await db.execute(select(School).order_by(School.name))
    return result.scalars().all()


@router.post("/schools", response_model=SchoolRead, status_code=201)
async def create_school(body: SchoolCreate, ctx: WriteGuard, db: Db):
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.CREATE, scope=Scope())
    school = School(code=body.code, name=body.name, timezone=body.timezone, address=body.address)
    db.add(school)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "SCHOOL_CODE_EXISTS", f"Mã trường '{body.code}' đã tồn tại.")
    await db.refresh(school)
    return school


@router.get("/schools/{school_id}", response_model=SchoolRead)
async def get_school(school_id: UUID, ctx: WriteGuard, db: Db):
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.READ, scope=Scope(school_id=school_id))
    school = await db.get(School, school_id)
    if not school:
        raise AppError(404, "SCHOOL_NOT_FOUND", "Không tìm thấy trường.")
    return school


@router.patch("/schools/{school_id}", response_model=SchoolRead)
async def update_school(school_id: UUID, body: SchoolUpdate, ctx: WriteGuard, db: Db):
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.UPDATE, scope=Scope(school_id=school_id))
    school = await db.get(School, school_id)
    if not school:
        raise AppError(404, "SCHOOL_NOT_FOUND", "Không tìm thấy trường.")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(school, field, value)
    await db.commit()
    await db.refresh(school)
    return school


@router.get("/academic-years", response_model=list[AcademicYearRead])
async def list_academic_years(ctx: WriteGuard, db: Db, school_id: UUID | None = None):
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.READ, scope=Scope(school_id=school_id))
    q = select(AcademicYear).order_by(AcademicYear.start_date.desc())
    if school_id:
        q = q.where(AcademicYear.school_id == school_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/academic-years", response_model=AcademicYearRead, status_code=201)
async def create_academic_year(body: AcademicYearCreate, ctx: WriteGuard, db: Db):
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.CREATE, scope=Scope(school_id=body.school_id))
    if body.start_date >= body.end_date:
        raise AppError(422, "INVALID_DATES", "Ngày bắt đầu phải trước ngày kết thúc.")
    school = await db.get(School, body.school_id)
    if not school:
        raise AppError(404, "SCHOOL_NOT_FOUND", "Không tìm thấy trường.")
    year = AcademicYear(
        school_id=body.school_id,
        name=body.name,
        start_date=body.start_date,
        end_date=body.end_date,
    )
    db.add(year)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "YEAR_NAME_EXISTS", f"Năm học '{body.name}' đã tồn tại cho trường này.")
    await db.refresh(year)
    return year


@router.get("/academic-years/{year_id}", response_model=AcademicYearRead)
async def get_academic_year(year_id: UUID, ctx: WriteGuard, db: Db):
    year = await db.get(AcademicYear, year_id)
    if not year:
        raise AppError(404, "YEAR_NOT_FOUND", "Không tìm thấy năm học.")
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.READ, scope=Scope(school_id=year.school_id, academic_year_id=year.id))
    return year


@router.patch("/academic-years/{year_id}", response_model=AcademicYearRead)
async def update_academic_year(year_id: UUID, body: AcademicYearUpdate, ctx: WriteGuard, db: Db):
    year = await db.get(AcademicYear, year_id)
    if not year:
        raise AppError(404, "YEAR_NOT_FOUND", "Không tìm thấy năm học.")
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.UPDATE, scope=Scope(school_id=year.school_id, academic_year_id=year.id))
    ensure_year_mutable(AcademicYearStatus(year.status))
    updates = body.model_dump(exclude_unset=True)
    start = updates.get("start_date", year.start_date)
    end = updates.get("end_date", year.end_date)
    if start >= end:
        raise AppError(422, "INVALID_DATES", "Ngày bắt đầu phải trước ngày kết thúc.")
    for field, value in updates.items():
        setattr(year, field, value)
    year.revision += 1
    await db.commit()
    await db.refresh(year)
    return year


@router.post("/academic-years/{year_id}/activate", response_model=AcademicYearRead)
async def activate_academic_year(year_id: UUID, ctx: WriteGuard, db: Db):
    year = await db.get(AcademicYear, year_id)
    if not year:
        raise AppError(404, "YEAR_NOT_FOUND", "Không tìm thấy năm học.")
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.ACTIVATE, scope=Scope(school_id=year.school_id, academic_year_id=year.id))
    ensure_academic_year_transition(AcademicYearStatus(year.status), AcademicYearStatus.ACTIVE)
    active_check = await db.execute(
        select(AcademicYear).where(
            AcademicYear.school_id == year.school_id,
            AcademicYear.status == "active",
            AcademicYear.id != year.id,
        )
    )
    if active_check.scalars().first():
        raise AppError(409, "ACTIVE_YEAR_EXISTS", "Trường này đã có một năm học đang hoạt động.")
    year.status = AcademicYearStatus.ACTIVE
    year.revision += 1
    await db.commit()
    await db.refresh(year)
    return year


@router.post("/academic-years/{year_id}/archive", response_model=AcademicYearRead)
async def archive_academic_year(year_id: UUID, ctx: WriteGuard, db: Db):
    year = await db.get(AcademicYear, year_id)
    if not year:
        raise AppError(404, "YEAR_NOT_FOUND", "Không tìm thấy năm học.")
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.ARCHIVE, scope=Scope(school_id=year.school_id, academic_year_id=year.id))
    ensure_academic_year_transition(AcademicYearStatus(year.status), AcademicYearStatus.ARCHIVED)
    year.status = AcademicYearStatus.ARCHIVED
    year.revision += 1
    await db.commit()
    await db.refresh(year)
    return year


@router.get("/academic-terms", response_model=list[AcademicTermRead])
async def list_academic_terms(ctx: WriteGuard, db: Db, academic_year_id: UUID | None = None):
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.READ, scope=Scope(academic_year_id=academic_year_id))
    q = select(AcademicTerm).order_by(AcademicTerm.term_order)
    if academic_year_id:
        q = q.where(AcademicTerm.academic_year_id == academic_year_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/academic-terms", response_model=AcademicTermRead, status_code=201)
async def create_academic_term(body: AcademicTermCreate, ctx: WriteGuard, db: Db):
    year = await db.get(AcademicYear, body.academic_year_id)
    if not year:
        raise AppError(404, "YEAR_NOT_FOUND", "Không tìm thấy năm học.")
    enforce_permission(ctx, resource_type=ResourceType.ACADEMIC_YEAR, action=ActionType.CREATE, scope=Scope(school_id=year.school_id, academic_year_id=year.id))
    ensure_year_mutable(AcademicYearStatus(year.status))
    validate_term_window(
        term=DateWindow(start_date=body.start_date, end_date=body.end_date),
        academic_year=DateWindow(start_date=year.start_date, end_date=year.end_date),
    )
    term = AcademicTerm(
        academic_year_id=body.academic_year_id,
        name=body.name,
        start_date=body.start_date,
        end_date=body.end_date,
        term_order=body.term_order,
    )
    db.add(term)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "TERM_ORDER_EXISTS", f"Thứ tự học kỳ {body.term_order} đã tồn tại.")
    await db.refresh(term)
    return term
