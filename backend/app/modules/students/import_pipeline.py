"""CSV staging and safe export helpers for student imports."""

from __future__ import annotations

import csv
import hashlib
import io
import re
import unicodedata
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.academic_years.models import AcademicYear
from app.modules.students.models import Enrollment, SchoolClass, Student

CSV_COLUMNS = [
    "student_code",
    "full_name",
    "date_of_birth",
    "gender",
    "academic_year",
    "grade_level",
    "class_code",
    "enrollment_status",
]
STATUSES = {"active", "transferred", "withdrawn", "graduated"}
GENDERS = {"Nam", "Nữ", "Khác", "Không khai báo", ""}
DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r", "\n", "＝", "＋", "－", "＠")
YEAR_RE = re.compile(r"^(\d{4})-(\d{4})$")
CODE_RE = re.compile(r"^[a-zA-Z0-9_-]{1,40}$")
MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 100_000


async def read_bounded_upload(
    file: Any, content_length: int | None
) -> tuple[bytes | None, str | None]:
    if content_length is not None and content_length > MAX_BYTES:
        return None, "EXCEEDS_10MB"
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_BYTES:
            return None, "EXCEEDS_10MB"
        chunks.append(chunk)
    return b"".join(chunks), None


def decode_csv(raw: bytes) -> tuple[str | None, list[dict[str, Any]]]:
    if len(raw) > MAX_BYTES:
        return "EXCEEDS_10MB", []
    try:
        text = raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError:
        return "INVALID_UTF8", []
    if "\x00" in text:
        return "NUL_CHARACTER", []
    reader = csv.DictReader(io.StringIO(text, newline=""), restkey="__EXTRA__", strict=True)
    if reader.fieldnames is None or reader.fieldnames != CSV_COLUMNS:
        return "UNEXPECTED_COLUMNS_OR_ORDER", []
    try:
        rows = list(reader)
    except csv.Error:
        return "MALFORMED_CSV", []
    if len(rows) > MAX_ROWS:
        return "EXCEEDS_ROW_LIMIT", []
    return None, rows


def normalize_row(row: dict[str, Any]) -> tuple[dict[str, str], list[dict[str, str]]]:
    normalized = {
        key: unicodedata.normalize("NFC", str(row.get(key) or "").strip()) for key in CSV_COLUMNS
    }
    errors: list[dict[str, str]] = []

    code = normalized["student_code"]
    name = normalized["full_name"]
    dob = normalized["date_of_birth"]
    gender = normalized["gender"]
    year = normalized["academic_year"]
    grade = normalized["grade_level"]
    cls = normalized["class_code"]
    status = normalized["enrollment_status"]

    if not CODE_RE.fullmatch(code):
        errors.append({"column": "student_code", "code": "INVALID_CODE"})
    if not name or len(name) > 120 or name.startswith(DANGEROUS_PREFIXES):
        errors.append({"column": "full_name", "code": "INVALID_NAME"})
    try:
        parsed_dob = date.fromisoformat(dob)
        if parsed_dob > date.today():
            raise ValueError
    except ValueError:
        errors.append({"column": "date_of_birth", "code": "INVALID_ISO_DATE"})
    if gender not in GENDERS:
        errors.append({"column": "gender", "code": "INVALID_VALUE"})
    match = YEAR_RE.fullmatch(year)
    if not match or int(match.group(2)) != int(match.group(1)) + 1:
        errors.append({"column": "academic_year", "code": "INVALID_YEAR"})
    if not grade.isdigit() or not 1 <= int(grade) <= 12:
        errors.append({"column": "grade_level", "code": "INVALID_GRADE"})
    if not cls or len(cls) > 30 or cls.startswith(DANGEROUS_PREFIXES):
        errors.append({"column": "class_code", "code": "INVALID_CLASS"})
    elif grade.isdigit():
        class_match = re.match(r"^(\d{1,2})", cls)
        if class_match and int(class_match.group(1)) != int(grade):
            errors.append({"column": "class_code", "code": "GRADE_MISMATCH"})
    if status not in STATUSES:
        errors.append({"column": "enrollment_status", "code": "INVALID_STATUS"})
    if "__EXTRA__" in row or any(row.get(key) is None for key in CSV_COLUMNS):
        errors.append({"column": "row", "code": "COLUMN_COUNT_MISMATCH"})
    return normalized, errors


async def classify_rows(
    db: AsyncSession,
    *,
    school_id,
    academic_year_id,
    raw_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    year = await db.get(AcademicYear, academic_year_id)
    if year is None or year.school_id != school_id:
        raise LookupError("YEAR_SCOPE_MISMATCH")

    existing_students = (
        (await db.execute(select(Student).where(Student.school_id == school_id))).scalars().all()
    )
    students_by_code = {item.student_code: item for item in existing_students}

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
    classes_by_name = {item.name: item for item in classes}

    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row_number, raw in enumerate(raw_rows, start=2):
        values, errors = normalize_row(raw)
        code = values["student_code"]
        duplicate_key = code.casefold()
        if duplicate_key in seen:
            errors.append({"column": "student_code", "code": "DUPLICATE_IN_FILE"})
        seen.add(duplicate_key)

        if values["academic_year"] != year.name:
            errors.append({"column": "academic_year", "code": "YEAR_NOT_SELECTED"})
        if values["class_code"] not in classes_by_name:
            errors.append({"column": "class_code", "code": "CLASS_NOT_FOUND"})
        else:
            cls = classes_by_name[values["class_code"]]
            if str(cls.grade) != values["grade_level"]:
                errors.append({"column": "class_code", "code": "CLASS_GRADE_MISMATCH"})

        status = "error"
        if not errors:
            status = "existing" if code in students_by_code else "new"
        elif any(
            error["code"] in {"YEAR_NOT_SELECTED", "CLASS_NOT_FOUND", "CLASS_GRADE_MISMATCH"}
            for error in errors
        ):
            status = "conflicting"

        result.append(
            {
                "row_number": row_number,
                "student_code": code or None,
                "status": status,
                "normalized_values": values,
                "errors": errors,
            }
        )
    return result


def csv_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def escape_formula(value: str) -> str:
    if value.startswith(DANGEROUS_PREFIXES):
        return "'" + value
    return value


def build_student_export_csv(
    students: list[Student],
    enrollments: list[Enrollment],
    *,
    academic_year_name: str,
    classes: list[SchoolClass],
) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS)
    writer.writeheader()
    enrollment_by_student = {item.student_id: item for item in enrollments}
    class_by_id = {item.id: item for item in classes}
    for student in students:
        enrollment = enrollment_by_student.get(student.id)
        school_class = class_by_id.get(enrollment.school_class_id) if enrollment else None
        writer.writerow(
            {
                "student_code": escape_formula(student.student_code),
                "full_name": escape_formula(student.full_name),
                "date_of_birth": student.date_of_birth.isoformat() if student.date_of_birth else "",
                "gender": escape_formula(student.gender or ""),
                "academic_year": academic_year_name,
                "grade_level": str(school_class.grade) if school_class else "",
                "class_code": escape_formula(school_class.name) if school_class else "",
                "enrollment_status": escape_formula(
                    enrollment.status if enrollment else student.status
                ),
            }
        )
    return ("\ufeff" + output.getvalue()).encode("utf-8")
