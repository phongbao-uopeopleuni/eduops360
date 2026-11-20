"""API router for school calendar templates and holiday ranges."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

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
from app.modules.school_calendar.domain import (
    validate_holiday_range,
    validate_slot_collection,
)
from app.modules.school_calendar.models import (
    ScheduleSlot,
    ScheduleTemplate,
    SchoolHoliday,
)
from app.modules.school_calendar.schemas import (
    ScheduleSlotRead,
    ScheduleTemplateCreate,
    ScheduleTemplateRead,
    SchoolHolidayCreate,
    SchoolHolidayRead,
)

router = APIRouter(prefix="/admin/calendar", tags=["School Calendar"])

WriteGuard = Annotated[AuthorizationContext, Depends(get_csrf_authorization_context)]
Db = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/templates", response_model=list[ScheduleTemplateRead])
async def list_templates(
    ctx: WriteGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.READ,
        scope=Scope(
            school_id=school_id,
            academic_year_id=academic_year_id,
        ),
    )
    query = select(ScheduleTemplate).order_by(
        ScheduleTemplate.academic_year_id,
        ScheduleTemplate.name,
        ScheduleTemplate.revision,
    )
    if school_id:
        query = query.where(ScheduleTemplate.school_id == school_id)
    if academic_year_id:
        query = query.where(ScheduleTemplate.academic_year_id == academic_year_id)
    return (await db.execute(query)).scalars().all()


@router.post("/templates", response_model=ScheduleTemplateRead, status_code=201)
async def create_template(
    body: ScheduleTemplateCreate,
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

    slots_by_weekday: dict[int, list[tuple[str, object, object]]] = {}
    seen_slots: set[tuple[int, int]] = set()
    for slot in body.slots:
        key = (slot.weekday, slot.slot_order)
        if key in seen_slots:
            raise AppError(422, "DUPLICATE_SLOT_ORDER", "Thứ và thứ tự tiết bị trùng.")
        seen_slots.add(key)
        slots_by_weekday.setdefault(slot.weekday, []).append(
            (slot.label, slot.start_time, slot.end_time)
        )
    for weekday, slots in slots_by_weekday.items():
        error = validate_slot_collection(slots)
        if error:
            raise AppError(
                422,
                "INVALID_SLOT_INTERVAL",
                f"Thứ {weekday}: {error}",
            )

    template = ScheduleTemplate(
        school_id=body.school_id,
        academic_year_id=body.academic_year_id,
        name=body.name,
        status="draft",
        revision=1,
    )
    db.add(template)
    await db.flush()
    for slot in body.slots:
        db.add(
            ScheduleSlot(
                template_id=template.id,
                weekday=slot.weekday,
                label=slot.label,
                period=slot.period,
                start_time=slot.start_time,
                end_time=slot.end_time,
                slot_order=slot.slot_order,
            )
        )
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise AppError(
            409,
            "CALENDAR_TEMPLATE_EXISTS",
            "Mẫu lịch trùng tên hoặc phiên bản trong năm học.",
        ) from None
    await write_audit_in_transaction(
        db,
        action="create",
        resource_type=ResourceType.TIMETABLE,
        resource_id=str(template.id),
        actor_id=ctx.auth.user.id,
        actor_email=getattr(ctx.auth.user, "email", None),
        after_state={
            "school_id": str(template.school_id),
            "academic_year_id": str(template.academic_year_id),
            "status": template.status,
            "revision": template.revision,
        },
        create_outbox=True,
    )
    await db.commit()
    await db.refresh(template)
    return template


@router.get("/templates/{template_id}/slots", response_model=list[ScheduleSlotRead])
async def list_template_slots(
    template_id: UUID,
    ctx: WriteGuard,
    db: Db,
):
    template = await db.get(ScheduleTemplate, template_id)
    if not template:
        raise AppError(404, "CALENDAR_TEMPLATE_NOT_FOUND", "Không tìm thấy mẫu lịch.")
    enforce_permission(
        ctx,
        resource_type=ResourceType.TIMETABLE,
        action=ActionType.READ,
        scope=Scope(
            school_id=template.school_id,
            academic_year_id=template.academic_year_id,
        ),
    )
    query = (
        select(ScheduleSlot)
        .where(ScheduleSlot.template_id == template_id)
        .order_by(ScheduleSlot.weekday, ScheduleSlot.slot_order)
    )
    return (await db.execute(query)).scalars().all()


@router.get("/holidays", response_model=list[SchoolHolidayRead])
async def list_holidays(
    ctx: WriteGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.HOLIDAY,
        action=ActionType.READ,
        scope=Scope(
            school_id=school_id,
            academic_year_id=academic_year_id,
        ),
    )
    query = select(SchoolHoliday).order_by(
        SchoolHoliday.start_date,
        SchoolHoliday.end_date,
    )
    if school_id:
        query = query.where(SchoolHoliday.school_id == school_id)
    if academic_year_id:
        query = query.where(SchoolHoliday.academic_year_id == academic_year_id)
    return (await db.execute(query)).scalars().all()


@router.post("/holidays", response_model=SchoolHolidayRead, status_code=201)
async def create_holiday(
    body: SchoolHolidayCreate,
    ctx: WriteGuard,
    db: Db,
):
    scope = Scope(
        school_id=body.school_id,
        academic_year_id=body.academic_year_id,
    )
    enforce_permission(
        ctx,
        resource_type=ResourceType.HOLIDAY,
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
    error = validate_holiday_range(
        body.start_date,
        body.end_date,
        year_start=year.start_date,
        year_end=year.end_date,
    )
    if error:
        raise AppError(422, "INVALID_HOLIDAY_RANGE", error)

    overlapping = (
        await db.execute(
            select(SchoolHoliday).where(
                SchoolHoliday.school_id == body.school_id,
                SchoolHoliday.academic_year_id == body.academic_year_id,
                SchoolHoliday.status == "active",
                SchoolHoliday.start_date <= body.end_date,
                SchoolHoliday.end_date >= body.start_date,
            )
        )
    ).scalar_one_or_none()
    if overlapping:
        raise AppError(
            409,
            "HOLIDAY_OVERLAP",
            "Khoảng nghỉ trùng với kỳ nghỉ đang hoạt động.",
        )

    holiday = SchoolHoliday(
        school_id=body.school_id,
        academic_year_id=body.academic_year_id,
        name=body.name,
        start_date=body.start_date,
        end_date=body.end_date,
        source_reference=body.source_reference,
        status="draft",
    )
    db.add(holiday)
    await db.flush()
    await write_audit_in_transaction(
        db,
        action="create",
        resource_type=ResourceType.HOLIDAY,
        resource_id=str(holiday.id),
        actor_id=ctx.auth.user.id,
        actor_email=getattr(ctx.auth.user, "email", None),
        after_state={
            "school_id": str(holiday.school_id),
            "academic_year_id": str(holiday.academic_year_id),
            "start_date": holiday.start_date.isoformat(),
            "end_date": holiday.end_date.isoformat(),
            "status": holiday.status,
        },
        create_outbox=True,
    )
    await db.commit()
    await db.refresh(holiday)
    return holiday
