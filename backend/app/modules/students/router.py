"""API router for students, classes and enrollments management."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
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
from app.modules.students.import_pipeline import (
    build_student_export_csv,
    classify_rows,
    csv_sha256,
    decode_csv,
)
from app.modules.students.models import (
    Enrollment,
    SchoolClass,
    Student,
    StudentImportBatch,
    StudentImportRow,
)
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
SchoolIdForm = Annotated[UUID, Form(...)]
AcademicYearIdForm = Annotated[UUID, Form(...)]
IdempotencyKeyForm = Annotated[
    str,
    Form(min_length=8, max_length=128),
]
CsvFileUpload = Annotated[UploadFile, File(...)]


@router.get("/classes", response_model=list[SchoolClassRead])
async def list_classes(
    ctx: WriteGuard,
    db: Db,
    school_id: UUID | None = None,
    academic_year_id: UUID | None = None,
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.CLASS,
        action=ActionType.READ,
        scope=Scope(school_id=school_id, academic_year_id=academic_year_id),
    )
    q = select(SchoolClass).order_by(SchoolClass.grade, SchoolClass.name)
    if school_id:
        q = q.where(SchoolClass.school_id == school_id)
    if academic_year_id:
        q = q.where(SchoolClass.academic_year_id == academic_year_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/classes", response_model=SchoolClassRead, status_code=201)
async def create_class(body: SchoolClassCreate, ctx: WriteGuard, db: Db):
    enforce_permission(
        ctx,
        resource_type=ResourceType.CLASS,
        action=ActionType.CREATE,
        scope=Scope(school_id=body.school_id, academic_year_id=body.academic_year_id),
    )
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
        raise AppError(
            409,
            "CLASS_NAME_EXISTS",
            f"Lớp '{body.name}' đã tồn tại trong năm học này.",
        ) from None
    await db.refresh(sc)
    return sc


@router.get("/classes/{class_id}", response_model=SchoolClassRead)
async def get_class(class_id: UUID, ctx: WriteGuard, db: Db):
    sc = await db.get(SchoolClass, class_id)
    if not sc:
        raise AppError(404, "CLASS_NOT_FOUND", "Không tìm thấy lớp.")
    enforce_permission(
        ctx,
        resource_type=ResourceType.CLASS,
        action=ActionType.READ,
        scope=Scope(school_id=sc.school_id, academic_year_id=sc.academic_year_id, class_id=sc.id),
    )
    return sc


@router.patch("/classes/{class_id}", response_model=SchoolClassRead)
async def update_class(class_id: UUID, body: SchoolClassUpdate, ctx: WriteGuard, db: Db):
    sc = await db.get(SchoolClass, class_id)
    if not sc:
        raise AppError(404, "CLASS_NOT_FOUND", "Không tìm thấy lớp.")
    enforce_permission(
        ctx,
        resource_type=ResourceType.CLASS,
        action=ActionType.UPDATE,
        scope=Scope(school_id=sc.school_id, academic_year_id=sc.academic_year_id, class_id=sc.id),
    )
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
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.READ,
        scope=Scope(school_id=school_id),
    )
    q = select(Student).order_by(Student.full_name)
    if school_id:
        q = q.where(Student.school_id == school_id)
    if search:
        q = q.where(
            Student.full_name.ilike(f"%{search}%") | Student.student_code.ilike(f"%{search}%")
        )
    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/students", response_model=StudentRead, status_code=201)
async def create_student(body: StudentCreate, ctx: WriteGuard, db: Db):
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.CREATE,
        scope=Scope(school_id=body.school_id),
    )
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
        raise AppError(
            409,
            "STUDENT_CODE_EXISTS",
            f"Mã học sinh '{body.student_code}' đã tồn tại.",
        ) from None
    await db.refresh(student)
    return student


@router.get("/students/{student_id}", response_model=StudentRead)
async def get_student(student_id: UUID, ctx: WriteGuard, db: Db):
    student = await db.get(Student, student_id)
    if not student:
        raise AppError(404, "STUDENT_NOT_FOUND", "Không tìm thấy học sinh.")
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.READ,
        scope=Scope(school_id=student.school_id),
    )
    return student


@router.patch("/students/{student_id}", response_model=StudentRead)
async def update_student(student_id: UUID, body: StudentUpdate, ctx: WriteGuard, db: Db):
    student = await db.get(Student, student_id)
    if not student:
        raise AppError(404, "STUDENT_NOT_FOUND", "Không tìm thấy học sinh.")
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.UPDATE,
        scope=Scope(school_id=student.school_id),
    )
    if student.status != "active":
        raise AppError(422, "STUDENT_NOT_ACTIVE", "Chỉ có thể cập nhật học sinh đang hoạt động.")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    await db.commit()
    await db.refresh(student)
    return student


@router.post("/students/{student_id}/status", response_model=StudentRead)
async def update_student_status(
    student_id: UUID, body: StudentStatusUpdate, ctx: WriteGuard, db: Db
):
    student = await db.get(Student, student_id)
    if not student:
        raise AppError(404, "STUDENT_NOT_FOUND", "Không tìm thấy học sinh.")
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.UPDATE,
        scope=Scope(school_id=student.school_id),
    )
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
    enforce_permission(
        ctx,
        resource_type=ResourceType.ENROLLMENT,
        action=ActionType.READ,
        scope=Scope(academic_year_id=academic_year_id),
    )
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
    enforce_permission(
        ctx,
        resource_type=ResourceType.ENROLLMENT,
        action=ActionType.CREATE,
        scope=Scope(academic_year_id=body.academic_year_id),
    )
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
        raise AppError(
            409,
            "ENROLLMENT_EXISTS",
            "Học sinh đã được ghi danh vào lớp này.",
        ) from None
    await db.refresh(enrollment)
    return enrollment


@router.patch("/enrollments/{enrollment_id}/status", response_model=EnrollmentRead)
async def update_enrollment_status(
    enrollment_id: UUID, body: EnrollmentStatusUpdate, ctx: WriteGuard, db: Db
):
    enrollment = await db.get(Enrollment, enrollment_id)
    if not enrollment:
        raise AppError(404, "ENROLLMENT_NOT_FOUND", "Không tìm thấy ghi danh.")
    enforce_permission(
        ctx,
        resource_type=ResourceType.ENROLLMENT,
        action=ActionType.UPDATE,
        scope=Scope(academic_year_id=enrollment.academic_year_id),
    )
    enrollment.status = body.status
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.post("/student-import/preview")
async def preview_student_import(
    request: Request,
    ctx: WriteGuard,
    db: Db,
    school_id: SchoolIdForm,
    academic_year_id: AcademicYearIdForm,
    idempotency_key: IdempotencyKeyForm,
    file: CsvFileUpload,
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.IMPORT,
        scope=Scope(school_id=school_id, academic_year_id=academic_year_id),
    )
    if len(idempotency_key) > 128 or not idempotency_key.isascii():
        raise AppError(422, "INVALID_IDEMPOTENCY_KEY", "Khóa idempotency không hợp lệ.")

    raw = await file.read()
    checksum = csv_sha256(raw)
    existing = (
        await db.execute(
            select(StudentImportBatch).where(
                StudentImportBatch.school_id == school_id,
                StudentImportBatch.actor_id == ctx.auth.user.id,
                StudentImportBatch.idempotency_key == idempotency_key,
            )
        )
    ).scalar_one_or_none()
    if existing:
        if existing.checksum != checksum or existing.academic_year_id != academic_year_id:
            await db.rollback()
            raise AppError(409, "IDEMPOTENCY_CONFLICT", "Khóa đã được dùng với nội dung khác.")
        rows = (
            (
                await db.execute(
                    select(StudentImportRow)
                    .where(StudentImportRow.batch_id == existing.id)
                    .order_by(StudentImportRow.row_number)
                )
            )
            .scalars()
            .all()
        )
        return {
            "id": existing.id,
            "state": existing.state,
            "checksum": existing.checksum,
            "counts": existing.counts,
            "rows": [
                {
                    "row_number": row.row_number,
                    "student_code": row.student_code,
                    "status": row.status,
                    "normalized_values": row.normalized_values,
                    "errors": row.errors,
                }
                for row in rows
            ],
        }

    file_error, raw_rows = decode_csv(raw)
    if file_error:
        raise AppError(422, "INVALID_CSV", file_error)

    try:
        rows = await classify_rows(
            db,
            school_id=school_id,
            academic_year_id=academic_year_id,
            raw_rows=raw_rows,
        )
    except LookupError as exc:
        raise AppError(422, "YEAR_SCOPE_MISMATCH", "Năm học không thuộc trường đã chọn.") from exc

    counts = {
        "total": len(rows),
        "new": sum(row["status"] == "new" for row in rows),
        "existing": sum(row["status"] == "existing" for row in rows),
        "conflicting": sum(row["status"] == "conflicting" for row in rows),
        "error": sum(row["status"] == "error" for row in rows),
    }
    state = "ready" if counts["error"] == 0 and counts["conflicting"] == 0 else "preview"
    filename = (file.filename or "students.csv").replace("/", "_").replace("\\", "_")[:255]
    batch = StudentImportBatch(
        school_id=school_id,
        academic_year_id=academic_year_id,
        actor_id=ctx.auth.user.id,
        idempotency_key=idempotency_key,
        checksum=checksum,
        original_filename=filename,
        mode="create_only",
        state=state,
        counts=counts,
    )
    db.add(batch)
    await db.flush()
    for row in rows:
        db.add(
            StudentImportRow(
                batch_id=batch.id,
                row_number=row["row_number"],
                student_code=row["student_code"],
                status=row["status"],
                normalized_values=row["normalized_values"],
                errors=row["errors"],
            )
        )
    await write_audit_in_transaction(
        db,
        action="preview",
        resource_type=ResourceType.STUDENT,
        resource_id=str(batch.id),
        actor_id=ctx.auth.user.id,
        actor_email=getattr(ctx.auth.user, "email", None),
        request_id=getattr(request.state, "request_id", None),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        extra_data={
            "school_id": str(school_id),
            "academic_year_id": str(academic_year_id),
            "checksum": checksum,
            "counts": counts,
        },
        create_outbox=True,
    )
    await db.commit()
    await db.refresh(batch)
    return {
        "id": batch.id,
        "state": batch.state,
        "checksum": batch.checksum,
        "counts": batch.counts,
        "rows": rows,
    }


@router.post("/student-import/{batch_id}/commit")
async def commit_student_import(
    batch_id: UUID,
    request: Request,
    ctx: WriteGuard,
    db: Db,
):
    batch = await db.get(StudentImportBatch, batch_id)
    if not batch:
        raise AppError(404, "IMPORT_BATCH_NOT_FOUND", "Không tìm thấy lô nhập.")
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.IMPORT,
        scope=Scope(
            school_id=batch.school_id,
            academic_year_id=batch.academic_year_id,
        ),
    )
    if batch.actor_id != ctx.auth.user.id:
        raise AppError(403, "FORBIDDEN", "Chỉ người tạo lô mới được xác nhận nhập.")
    if batch.state == "committed":
        return {"id": batch.id, "state": batch.state, "counts": batch.counts}
    if batch.state not in {"ready", "preview"}:
        raise AppError(409, "IMPORT_STATE_INVALID", "Không thể nhập lô ở trạng thái hiện tại.")

    rows = (
        (
            await db.execute(
                select(StudentImportRow)
                .where(StudentImportRow.batch_id == batch.id)
                .order_by(StudentImportRow.row_number)
            )
        )
        .scalars()
        .all()
    )
    if any(row.status in {"error", "conflicting"} for row in rows):
        batch.state = "preview"
        await db.commit()
        raise AppError(422, "IMPORT_HAS_ERRORS", "Lô còn dòng lỗi hoặc xung đột.")

    created = 0
    enrolled = 0
    for row in rows:
        values = row.normalized_values
        result = await db.execute(
            select(Student).where(
                Student.school_id == batch.school_id,
                Student.student_code == row.student_code,
            )
        )
        student = result.scalar_one_or_none()
        if student is None:
            student = Student(
                school_id=batch.school_id,
                student_code=row.student_code,
                full_name=values["full_name"],
                date_of_birth=date.fromisoformat(values["date_of_birth"])
                if values["date_of_birth"]
                else None,
                gender=values["gender"] or None,
                status="active",
            )
            db.add(student)
            await db.flush()
            created += 1

        class_result = await db.execute(
            select(SchoolClass).where(
                SchoolClass.school_id == batch.school_id,
                SchoolClass.academic_year_id == batch.academic_year_id,
                SchoolClass.name == values["class_code"],
            )
        )
        school_class = class_result.scalar_one_or_none()
        if school_class is None:
            await db.rollback()
            raise AppError(422, "CLASS_NOT_FOUND", "Lớp trong lô không còn tồn tại.")
        enrollment_result = await db.execute(
            select(Enrollment).where(
                Enrollment.student_id == student.id,
                Enrollment.academic_year_id == batch.academic_year_id,
            )
        )
        enrollment = enrollment_result.scalar_one_or_none()
        if enrollment is None:
            db.add(
                Enrollment(
                    student_id=student.id,
                    school_class_id=school_class.id,
                    academic_year_id=batch.academic_year_id,
                    status="enrolled",
                )
            )
            enrolled += 1

    batch.state = "committed"
    batch.committed_at = datetime.now(UTC)
    batch.counts = {
        **batch.counts,
        "created": created,
        "enrolled": enrolled,
    }
    await write_audit_in_transaction(
        db,
        action="commit",
        resource_type=ResourceType.STUDENT,
        resource_id=str(batch.id),
        actor_id=ctx.auth.user.id,
        actor_email=getattr(ctx.auth.user, "email", None),
        request_id=getattr(request.state, "request_id", None),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        extra_data={
            "school_id": str(batch.school_id),
            "academic_year_id": str(batch.academic_year_id),
            "checksum": batch.checksum,
            "counts": batch.counts,
        },
        create_outbox=True,
    )
    await db.commit()
    await db.refresh(batch)
    return {"id": batch.id, "state": batch.state, "counts": batch.counts}


@router.get("/students/export")
async def export_students(
    ctx: WriteGuard,
    db: Db,
    school_id: UUID,
    academic_year_id: UUID,
):
    enforce_permission(
        ctx,
        resource_type=ResourceType.STUDENT,
        action=ActionType.EXPORT,
        scope=Scope(school_id=school_id, academic_year_id=academic_year_id),
    )
    students = (
        (await db.execute(select(Student).where(Student.school_id == school_id))).scalars().all()
    )
    class_ids = (
        (
            await db.execute(
                select(SchoolClass.id).where(
                    SchoolClass.school_id == school_id,
                    SchoolClass.academic_year_id == academic_year_id,
                )
            )
        )
        .scalars()
        .all()
    )
    enrollments = []
    if class_ids:
        enrollments = (
            (
                await db.execute(
                    select(Enrollment).where(
                        Enrollment.academic_year_id == academic_year_id,
                        Enrollment.school_class_id.in_(class_ids),
                    )
                )
            )
            .scalars()
            .all()
        )
    year = await db.get(AcademicYear, academic_year_id)
    if year is None or year.school_id != school_id:
        raise AppError(422, "YEAR_SCOPE_MISMATCH", "Năm học không thuộc trường đã chọn.")
    classes = (
        (
            await db.execute(
                select(SchoolClass).where(
                    SchoolClass.school_id == school_id,
                    SchoolClass.academic_year_id == academic_year_id,
                )
            )
        )
        .scalars()
        .all()
    )
    raw = build_student_export_csv(
        students,
        enrollments,
        academic_year_name=year.name,
        classes=classes,
    )
    return StreamingResponse(
        iter([raw]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="students.csv"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )
