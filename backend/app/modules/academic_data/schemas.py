from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    school_id: UUID
    source_id: int
    code: str
    name: str
    subject_group: str


class TeacherRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    school_id: UUID
    source_id: int
    code: str
    full_name: str
    gender: str
    hire_date: date | None
    role: str
    specialty_subject_id: UUID | None


class TeachingAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    school_id: UUID
    academic_year_id: UUID
    class_id: UUID
    subject_id: UUID
    teacher_id: UUID
    semester: int


class AssessmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    source_id: int
    school_id: UUID
    academic_year_id: UUID
    student_id: UUID
    subject_id: UUID
    semester: int
    assessment_type: str
    score: float | None
    result_label: str | None
    exam_date: date | None


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    school_id: UUID
    academic_year_id: UUID
    student_id: UUID
    attendance_date: date
    status: str
