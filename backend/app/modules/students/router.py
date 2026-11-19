"""API router for students, classes and enrollments management."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.dependencies import get_db_session
from app.modules.academic_years.models import AcademicYear, School
from app.modules.auth.constants import ActionType, ResourceType
from app.modules.auth.guards import (
    AuthorizationContext,
    enforce_permission,
    get_csrf_authorization_context,
)
from app.modules.auth.permissions import Scope
from app.modules.students.models import Enrollment, SchoolClass, Student
from app.modules.students.schemas import (
    EnrollmentCreate,
    EnrollmentRead,
    EnrollmentStatusUpdate,
    SchoolClassCreate,
    SchoolClassRead,
    SchoolClassUpdate,
    StudentCreate,
    StudentRead,
    StudentStatusUpdate,
    StudentUpdate,
)

router = APIRouter(prefix="/admin", tags=["Student Management"])

WriteGuard = Annotated[AuthorizationContext, Depends(get_csrf_authorization_context)]
Db = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/classes", response_model=list[SchoolClassRead])
async def list_classes(
    ctx: WriteGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
):
    enforce_permission(ctx, resource_type=ResourceType.CLASS, action=ActionType.READ, scope=Scope(school_id=school_id, academic_year_id=academic_year_id))
    q = select(SchoolClass).order_by(SchoolClass.grade, SchoolClass.name)
    if school_id:
        q = q.where(SchoolClass.school_id == school_id)
    if academic_year_id:
        q = q.where(SchoolClass.academic_year_id == academic_year_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/classes", response_model=SchoolClassRead, status_code=201)
async def create_class(body: SchoolClassCreate, ctx: WriteGuard, db: Db):
    enforce_permission(ctx, resource_type=ResourceType.CLASS, action=ActionType.CREATE, scope=Scope(school_id=body.school_id, academic_year_id=body.academic_year_id))
    school = await db.get(School, body.school_id)
    if not school:
        raise AppError(404, "SCHOOL_NOT_FOUND", "Không tìm thấy trường.")
    year = await db.get(AcademicYear, body.academic_year_id)
    if not year:
        raise AppError(404, "YEAR_NOT_FOUND", "Không tìm thấy năm học.")
    if year.school_id != body.school_id:
        raise AppError(422, "SCHOOL_MISMATCH", "Năm học không thuộc trường đã chọn.")
    sc = SchoolClass(
        school_id=body.school_id,
        academic_year_id=body.academic_year_id,
        name=body.name,
        grade=body.grade,
        homeroom_teacher_name=body.homeroom_teacher_name,
    )
    db.add(sc)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "CLASS_NAME_EXISTS", f"Lớp '{body.name}' đã tồn tại trong năm học này.")
    await db.refresh(sc)
    return sc


@router.get("/classes/{class_id}", response_model=SchoolClassRead)
async def get_class(class_id: UUID, ctx: WriteGuard, db: Db):
    sc = await db.get(SchoolClass, class_id)
    if not sc:
        raise AppError(404, "CLASS_NOT_FOUND", "Không tìm thấy lớp.")
    enforce_permission(ctx, resource_type=ResourceType.CLASS, action=ActionType.READ, scope=Scope(school_id=sc.school_id, academic_year_id=sc.academic_year_id, class_id=sc.id))
    return sc


@router.patch("/classes/{class_id}", response_model=SchoolClassRead)
async def update_class(class_id: UUID, body: SchoolClassUpdate, ctx: WriteGuard, db: Db):
    sc = await db.get(SchoolClass, class_id)
    if not sc:
        raise AppError(404, "CLASS_NOT_FOUND", "Không tìm thấy lớp.")
    enforce_permission(ctx, resource_type=ResourceType.CLASS, action=ActionType.UPDATE, scope=Scope(school_id=sc.school_id, academic_year_id=sc.academic_year_id, class_id=sc.id))
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(sc, field, value)
    await db.commit()
    await db.refresh(sc)
    return sc


@router.get("/students", response_model=list[StudentRead])
async def list_students(
    ctx: WriteGuard,
    db: Db,
    school_id: UUID | None = None,
    search: str | None = Query(None, max_length=200),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    enforce_permission(ctx, resource_type=ResourceType.STUDENT, action=ActionType.READ, scope=Scope(school_id=school_id))
    q = select(Student).order_by(Student.full_name)
    if school_id:
        q = q.where(Student.school_id == school_id)
    if search:
        q = q.where(
            Student.full_name.ilike(f"%{search}%")
            | Student.student_code.ilike(f"%{search}%")
        )
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/students", response_model=StudentRead, status_code=201)
async def create_student(body: StudentCreate, ctx: WriteGuard, db: Db):
    enforce_permission(ctx, resource_type=ResourceType.STUDENT, action=ActionType.CREATE, scope=Scope(school_id=body.school_id))
    school = await db.get(School, body.school_id)
    if not school:
        raise AppError(404, "SCHOOL_NOT_FOUND", "Không tìm thấy trường.")
    student = Student(
        school_id=body.school_id,
        student_code=body.student_code,
        full_name=body.full_name,
        date_of_birth=body.date_of_birth,
        gender=body.gender,
        notes=body.notes,
    )
    db.add(student)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "STUDENT_CODE_EXISTS", f"Mã học sinh '{body.student_code}' đã tồn tại.")
    await db.refresh(student)
    return student


@router.get("/students/{student_id}", response_model=StudentRead)
async def get_student(student_id: UUID, ctx: WriteGuard, db: Db):
    student = await db.get(Student, student_id)
    if not student:
        raise AppError(404, "STUDENT_NOT_FOUND", "Không tìm thấy học sinh.")
    enforce_permission(ctx, resource_type=ResourceType.STUDENT, action=ActionType.READ, scope=Scope(school_id=student.school_id))
    return student


@router.patch("/students/{student_id}", response_model=StudentRead)
async def update_student(student_id: UUID, body: StudentUpdate, ctx: WriteGuard, db: Db):
    student = await db.get(Student, student_id)
    if not student:
        raise AppError(404, "STUDENT_NOT_FOUND", "Không tìm thấy học sinh.")
    enforce_permission(ctx, resource_type=ResourceType.STUDENT, action=ActionType.UPDATE, scope=Scope(school_id=student.school_id))
    if student.status != "active":
        raise AppError(422, "STUDENT_NOT_ACTIVE", "Chỉ có thể cập nhật học sinh đang hoạt động.")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    await db.commit()
    await db.refresh(student)
    return student


@router.post("/students/{student_id}/status", response_model=StudentRead)
async def update_student_status(student_id: UUID, body: StudentStatusUpdate, ctx: WriteGuard, db: Db):
    student = await db.get(Student, student_id)
    if not student:
        raise AppError(404, "STUDENT_NOT_FOUND", "Không tìm thấy học sinh.")
    enforce_permission(ctx, resource_type=ResourceType.STUDENT, action=ActionType.UPDATE, scope=Scope(school_id=student.school_id))
    student.status = body.status
    await db.commit()
    await db.refresh(student)
    return student


@router.get("/enrollments", response_model=list[EnrollmentRead])
async def list_enrollments(
    ctx: WriteGuard,
    db: Db,
    student_id: UUID | None = None,
    school_class_id: UUID | None = None,
    academic_year_id: UUID | None = None,
):
    enforce_permission(ctx, resource_type=ResourceType.ENROLLMENT, action=ActionType.READ, scope=Scope(academic_year_id=academic_year_id))
    q = select(Enrollment).order_by(Enrollment.enrolled_at.desc())
    if student_id:
        q = q.where(Enrollment.student_id == student_id)
    if school_class_id:
        q = q.where(Enrollment.school_class_id == school_class_id)
    if academic_year_id:
        q = q.where(Enrollment.academic_year_id == academic_year_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/enrollments", response_model=EnrollmentRead, status_code=201)
async def create_enrollment(body: EnrollmentCreate, ctx: WriteGuard, db: Db):
    enforce_permission(ctx, resource_type=ResourceType.ENROLLMENT, action=ActionType.CREATE, scope=Scope(academic_year_id=body.academic_year_id))
    student = await db.get(Student, body.student_id)
    if not student:
        raise AppError(404, "STUDENT_NOT_FOUND", "Không tìm thấy học sinh.")
    if student.status != "active":
        raise AppError(422, "STUDENT_NOT_ACTIVE", "Học sinh không ở trạng thái hoạt động.")
    sc = await db.get(SchoolClass, body.school_class_id)
    if not sc:
        raise AppError(404, "CLASS_NOT_FOUND", "Không tìm thấy lớp.")
    year = await db.get(AcademicYear, body.academic_year_id)
    if not year:
        raise AppError(404, "YEAR_NOT_FOUND", "Không tìm thấy năm học.")
    if sc.academic_year_id != body.academic_year_id:
        raise AppError(422, "YEAR_MISMATCH", "Lớp không thuộc năm học đã chọn.")
    if student.school_id != sc.school_id:
        raise AppError(422, "SCHOOL_MISMATCH", "Học sinh và lớp không cùng trường.")
    enrollment = Enrollment(
        student_id=body.student_id,
        school_class_id=body.school_class_id,
        academic_year_id=body.academic_year_id,
        notes=body.notes,
    )
    db.add(enrollment)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise AppError(409, "ENROLLMENT_EXISTS", "Học sinh đã được ghi danh vào lớp này.")
    await db.refresh(enrollment)
    return enrollment


@router.patch("/enrollments/{enrollment_id}/status", response_model=EnrollmentRead)
async def update_enrollment_status(enrollment_id: UUID, body: EnrollmentStatusUpdate, ctx: WriteGuard, db: Db):
    enrollment = await db.get(Enrollment, enrollment_id)
    if not enrollment:
        raise AppError(404, "ENROLLMENT_NOT_FOUND", "Không tìm thấy ghi danh.")
    enforce_permission(ctx, resource_type=ResourceType.ENROLLMENT, action=ActionType.UPDATE, scope=Scope(academic_year_id=enrollment.academic_year_id))
    enrollment.status = body.status
    await db.commit()
    await db.refresh(enrollment)
    return enrollment
