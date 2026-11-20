"""Pydantic schemas for students, classes and enrollments API."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SchoolClassCreate(BaseModel):
    school_id: UUID
    academic_year_id: UUID
    name: str = Field(min_length=1, max_length=50)
    grade: int = Field(ge=1, le=12)
    homeroom_teacher_name: str | None = Field(None, max_length=200)


class SchoolClassRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: UUID
    academic_year_id: UUID
    name: str
    grade: int
    homeroom_teacher_name: str | None
    created_at: datetime
    updated_at: datetime


class SchoolClassUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    homeroom_teacher_name: str | None = Field(None, max_length=200)


class StudentCreate(BaseModel):
    school_id: UUID
    student_code: str = Field(min_length=1, max_length=50)
    full_name: str = Field(min_length=1, max_length=200)
    date_of_birth: date | None = None
    gender: str | None = Field(None, max_length=20)
    notes: str | None = None


class StudentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: UUID
    student_code: str
    full_name: str
    date_of_birth: date | None
    gender: str | None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime


class StudentUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=200)
    date_of_birth: date | None = None
    gender: str | None = Field(None, max_length=20)
    notes: str | None = None


class StudentStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(active|graduated|withdrawn|transferred)$")


class EnrollmentCreate(BaseModel):
    student_id: UUID
    school_class_id: UUID
    academic_year_id: UUID
    notes: str | None = None


class EnrollmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID
    school_class_id: UUID
    academic_year_id: UUID
    status: str
    enrolled_at: datetime
    notes: str | None
    created_at: datetime
    updated_at: datetime


class EnrollmentStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(enrolled|withdrawn|transferred)$")


class StudentImportPreviewRow(BaseModel):
    row_number: int
    student_code: str | None
    status: str
    normalized_values: dict
    errors: list[dict]


class StudentImportPreview(BaseModel):
    id: UUID
    state: str
    checksum: str
    counts: dict
    rows: list[StudentImportPreviewRow]


class StudentImportCommit(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=128)
