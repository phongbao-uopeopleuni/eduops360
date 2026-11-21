"""Pydantic schemas for schools and academic years API."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SchoolCreate(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=200)
    timezone: str = Field(default="Asia/Ho_Chi_Minh", max_length=100)
    address: str | None = None


class SchoolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    timezone: str
    address: str | None
    created_at: datetime
    updated_at: datetime


class SchoolUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    timezone: str | None = Field(None, max_length=100)
    address: str | None = None


class AcademicYearCreate(BaseModel):
    school_id: UUID
    name: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date


class AcademicYearRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    school_id: UUID
    name: str
    start_date: date
    end_date: date
    status: str
    revision: int
    created_at: datetime
    updated_at: datetime


class AcademicYearUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    start_date: date | None = None
    end_date: date | None = None


class AcademicYearStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(active|archived)$")


class AcademicTermCreate(BaseModel):
    academic_year_id: UUID
    name: str = Field(min_length=1, max_length=100)
    start_date: date
    end_date: date
    term_order: int = Field(ge=1)


class AcademicTermRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    academic_year_id: UUID
    name: str
    start_date: date
    end_date: date
    status: str
    term_order: int
    created_at: datetime
    updated_at: datetime
