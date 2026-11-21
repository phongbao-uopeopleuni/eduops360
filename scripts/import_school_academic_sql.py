"""Import the complete SQLite-style synthetic dataset into EduOps PostgreSQL.

Maps the attached 2000-student dataset into schools, years, classes, students,
enrollments, subjects, teachers, grade-subjects, teaching assignments,
assessments, and attendance.
"""

from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import date as Date
from pathlib import Path
from uuid import uuid4

import psycopg

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SQL = ROOT / "backend" / "school_academic_2000_import.sql"


def map_gender(value: str | None) -> str | None:
    normalized = (value or "").strip().upper()
    if normalized == "NAM":
        return "NAM"
    if normalized == "NU":
        return "NU"
    return None


def map_student_status(value: str | None) -> tuple[str, str | None]:
    normalized = (value or "").strip().upper()
    if normalized == "BAO_LUU":
        return "withdrawn", "Nguồn dữ liệu: BAO_LUU"
    return "active", None


def map_enrollment_status(value: str | None) -> str:
    normalized = (value or "").strip().upper()
    return "withdrawn" if normalized == "BAO_LUU" else "enrolled"


def load_source(sql_path: Path) -> dict[str, list[dict]]:
    database = sqlite3.connect(":memory:")
    database.row_factory = sqlite3.Row
    database.executescript(sql_path.read_text(encoding="utf-8-sig"))

    year_rows = [
        dict(row)
        for row in database.execute(
            "SELECT year_id, year_name, start_date, end_date FROM academic_years"
        )
    ]
    class_rows = [
        dict(row)
        for row in database.execute(
            """
            SELECT c.class_id, c.class_name, c.grade, c.level,
                   t.full_name AS homeroom_teacher_name
            FROM classes c
            LEFT JOIN teachers t ON t.teacher_id = c.homeroom_teacher_id
            ORDER BY c.class_id
            """
        )
    ]
    student_rows = [
        dict(row)
        for row in database.execute(
            """
            SELECT student_id, student_code, full_name, gender,
                   date_of_birth, enrollment_date, status, class_id
            FROM students
            ORDER BY student_id
            """
        )
    ]
    subject_rows = [
        dict(row)
        for row in database.execute(
            """
            SELECT subject_id, subject_code, subject_name, subject_group
            FROM subjects
            ORDER BY subject_id
            """
        )
    ]
    teacher_rows = [
        dict(row)
        for row in database.execute(
            """
            SELECT teacher_id, teacher_code, full_name, gender, hire_date, role,
                   specialty_subject_id
            FROM teachers
            ORDER BY teacher_id
            """
        )
    ]
    grade_subject_rows = [
        dict(row)
        for row in database.execute(
            "SELECT grade, subject_id, subject_type FROM grade_subjects ORDER BY grade, subject_id"
        )
    ]
    teaching_assignment_rows = [
        dict(row)
        for row in database.execute(
            """
            SELECT assignment_id, class_id, subject_id, teacher_id, semester
            FROM teaching_assignments
            ORDER BY assignment_id
            """
        )
    ]
    assessment_rows = [
        dict(row)
        for row in database.execute(
            """
            SELECT assessment_id, student_id, subject_id, semester,
                   assessment_type, score, result_label, exam_date
            FROM assessments
            ORDER BY assessment_id
            """
        )
    ]
    attendance_rows = [
        dict(row)
        for row in database.execute(
            """
            SELECT attendance_id, student_id, attendance_date, status
            FROM attendance
            ORDER BY attendance_id
            """
        )
    ]
    database.close()
    return {
        "years": year_rows,
        "classes": class_rows,
        "students": student_rows,
        "subjects": subject_rows,
        "teachers": teacher_rows,
        "grade_subjects": grade_subject_rows,
        "teaching_assignments": teaching_assignment_rows,
        "assessments": assessment_rows,
        "attendance": attendance_rows,
    }


def normalize_dsn(raw: str) -> str:
    if raw.startswith("postgresql+psycopg://"):
        return "postgresql://" + raw.split("://", 1)[1]
    return raw


def import_source(dsn: str, sql_path: Path) -> dict[str, int]:
    source = load_source(sql_path)
    with psycopg.connect(normalize_dsn(dsn)) as connection, connection.transaction():
            school_id = uuid4()
            connection.execute(
                """
                INSERT INTO schools (id, code, name, timezone)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (code) DO UPDATE
                SET name = EXCLUDED.name,
                    timezone = EXCLUDED.timezone,
                    updated_at = now()
                RETURNING id
                """,
                (school_id, "DATA-2000", "Trường dữ liệu vận hành 2000", "Asia/Ho_Chi_Minh"),
            )
            school_id = connection.execute(
                "SELECT id FROM schools WHERE code = %s", ("DATA-2000",)
            ).fetchone()[0]

            year_count = 0
            class_count = 0
            student_count = 0
            enrollment_count = 0
            subject_count = 0
            teacher_count = 0
            grade_subject_count = 0
            teaching_assignment_count = 0
            assessment_count = 0
            attendance_count = 0

            year_ids: dict[int, object] = {}
            for year in source["years"]:
                connection.execute(
                    """
                    INSERT INTO academic_years
                        (id, school_id, name, start_date, end_date, status, revision)
                    VALUES (%s, %s, %s, %s, %s, 'active', 1)
                    ON CONFLICT (school_id, name) DO UPDATE
                    SET start_date = EXCLUDED.start_date,
                        end_date = EXCLUDED.end_date,
                        status = 'active',
                        revision = GREATEST(academic_years.revision, 1),
                        updated_at = now()
                    RETURNING id
                    """,
                    (
                        uuid4(),
                        school_id,
                        year["year_name"],
                        year["start_date"],
                        year["end_date"],
                    ),
                )
                year_id = connection.execute(
                    "SELECT id FROM academic_years WHERE school_id = %s AND name = %s",
                    (school_id, year["year_name"]),
                ).fetchone()[0]
                year_ids[int(year["year_id"])] = year_id
                year_count += 1

            class_ids: dict[int, object] = {}
            for class_row in source["classes"]:
                connection.execute(
                    """
                    INSERT INTO school_classes
                        (id, school_id, academic_year_id, name, grade, homeroom_teacher_name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (school_id, academic_year_id, name) DO UPDATE
                    SET grade = EXCLUDED.grade,
                        homeroom_teacher_name = EXCLUDED.homeroom_teacher_name,
                        updated_at = now()
                    RETURNING id
                    """,
                    (
                        uuid4(),
                        school_id,
                        year_ids[1],
                        class_row["class_name"],
                        int(class_row["grade"]),
                        class_row["homeroom_teacher_name"],
                    ),
                )
                class_id = connection.execute(
                    """
                    SELECT id FROM school_classes
                    WHERE school_id = %s AND academic_year_id = %s AND name = %s
                    """,
                    (school_id, year_ids[1], class_row["class_name"]),
                ).fetchone()[0]
                class_ids[int(class_row["class_id"])] = class_id
                class_count += 1

            subject_ids: dict[int, object] = {}
            for subject in source["subjects"]:
                connection.execute(
                    """
                    INSERT INTO subjects
                        (id, school_id, source_id, code, name, subject_group)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (school_id, source_id) DO UPDATE
                    SET code = EXCLUDED.code,
                        name = EXCLUDED.name,
                        subject_group = EXCLUDED.subject_group
                    """,
                    (
                        uuid4(),
                        school_id,
                        int(subject["subject_id"]),
                        subject["subject_code"],
                        subject["subject_name"],
                        subject["subject_group"],
                    ),
                )
                subject_db_id = connection.execute(
                    "SELECT id FROM subjects WHERE school_id = %s AND source_id = %s",
                    (school_id, int(subject["subject_id"])),
                ).fetchone()[0]
                subject_ids[int(subject["subject_id"])] = subject_db_id
                subject_count += 1

            teacher_ids: dict[int, object] = {}
            for teacher in source["teachers"]:
                specialty_id = (
                    subject_ids[int(teacher["specialty_subject_id"])]
                    if teacher["specialty_subject_id"] is not None
                    else None
                )
                hire_date = (
                    Date.fromisoformat(teacher["hire_date"])
                    if teacher["hire_date"]
                    else None
                )
                connection.execute(
                    """
                    INSERT INTO teachers
                        (id, school_id, source_id, code, full_name, gender,
                         hire_date, role, specialty_subject_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (school_id, source_id) DO UPDATE
                    SET code = EXCLUDED.code,
                        full_name = EXCLUDED.full_name,
                        gender = EXCLUDED.gender,
                        hire_date = EXCLUDED.hire_date,
                        role = EXCLUDED.role,
                        specialty_subject_id = EXCLUDED.specialty_subject_id
                    """,
                    (
                        uuid4(),
                        school_id,
                        int(teacher["teacher_id"]),
                        teacher["teacher_code"],
                        teacher["full_name"],
                        map_gender(teacher["gender"]),
                        hire_date,
                        teacher["role"],
                        specialty_id,
                    ),
                )
                teacher_db_id = connection.execute(
                    "SELECT id FROM teachers WHERE school_id = %s AND source_id = %s",
                    (school_id, int(teacher["teacher_id"])),
                ).fetchone()[0]
                teacher_ids[int(teacher["teacher_id"])] = teacher_db_id
                teacher_count += 1

            grade_subject_rows = []
            for grade_subject in source["grade_subjects"]:
                grade_subject_rows.append(
                    (
                        uuid4(),
                        school_id,
                        year_ids[1],
                        int(grade_subject["grade"]),
                        subject_ids[int(grade_subject["subject_id"])],
                        grade_subject["subject_type"],
                    )
                )
            cursor = connection.cursor()
            cursor.executemany(
                """
                INSERT INTO grade_subjects
                    (id, school_id, academic_year_id, grade, subject_id, subject_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (school_id, academic_year_id, grade, subject_id) DO UPDATE
                SET subject_type = EXCLUDED.subject_type
                """,
                grade_subject_rows,
            )
            grade_subject_count = len(grade_subject_rows)

            teaching_assignment_rows = []
            for assignment in source["teaching_assignments"]:
                teaching_assignment_rows.append(
                    (
                        uuid4(),
                        school_id,
                        year_ids[1],
                        class_ids[int(assignment["class_id"])],
                        subject_ids[int(assignment["subject_id"])],
                        teacher_ids[int(assignment["teacher_id"])],
                        int(assignment["semester"]),
                    )
                )
            cursor.executemany(
                """
                INSERT INTO teaching_assignments
                    (id, school_id, academic_year_id, class_id, subject_id, teacher_id, semester)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (school_id, academic_year_id, class_id, subject_id, semester)
                DO UPDATE SET teacher_id = EXCLUDED.teacher_id
                """,
                teaching_assignment_rows,
            )
            teaching_assignment_count = len(teaching_assignment_rows)

            student_ids: dict[int, object] = {}
            for student in source["students"]:
                status, source_note = map_student_status(student["status"])
                student_id = uuid4()
                connection.execute(
                    """
                    INSERT INTO students
                        (id, school_id, student_code, full_name, date_of_birth,
                         gender, status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (school_id, student_code) DO UPDATE
                    SET full_name = EXCLUDED.full_name,
                        date_of_birth = EXCLUDED.date_of_birth,
                        gender = EXCLUDED.gender,
                        status = EXCLUDED.status,
                        notes = EXCLUDED.notes,
                        updated_at = now()
                    RETURNING id
                    """,
                    (
                        student_id,
                        school_id,
                        student["student_code"],
                        student["full_name"],
                        student["date_of_birth"] or None,
                        map_gender(student["gender"]),
                        status,
                        source_note,
                    ),
                )
                student_db_id = connection.execute(
                    "SELECT id FROM students WHERE school_id = %s AND student_code = %s",
                    (school_id, student["student_code"]),
                ).fetchone()[0]
                student_ids[int(student["student_id"])] = student_db_id
                student_count += 1

                connection.execute(
                    """
                    INSERT INTO enrollments
                        (id, student_id, school_class_id, academic_year_id, status,
                         enrolled_at, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (student_id, school_class_id, academic_year_id) DO UPDATE
                    SET status = EXCLUDED.status,
                        enrolled_at = EXCLUDED.enrolled_at,
                        notes = EXCLUDED.notes,
                        updated_at = now()
                    """,
                    (
                        uuid4(),
                        student_db_id,
                        class_ids[int(student["class_id"])],
                        year_ids[1],
                        map_enrollment_status(student["status"]),
                        Date.fromisoformat(student["enrollment_date"]),
                        "Nguồn dữ liệu: school_academic_2000_import.sql",
                    ),
                )
                enrollment_count += 1

            assessment_rows = []
            for assessment in source["assessments"]:
                exam_date = (
                    Date.fromisoformat(assessment["exam_date"])
                    if assessment["exam_date"]
                    else None
                )
                assessment_rows.append(
                    (
                        uuid4(),
                        school_id,
                        int(assessment["assessment_id"]),
                        year_ids[1],
                        student_ids[int(assessment["student_id"])],
                        subject_ids[int(assessment["subject_id"])],
                        int(assessment["semester"]),
                        assessment["assessment_type"],
                        assessment["score"],
                        assessment["result_label"],
                        exam_date,
                    )
                )
            cursor.executemany(
                """
                INSERT INTO assessments
                    (id, school_id, source_id, academic_year_id, student_id, subject_id,
                     semester, assessment_type, score, result_label, exam_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (school_id, source_id) DO UPDATE
                SET semester = EXCLUDED.semester,
                    assessment_type = EXCLUDED.assessment_type,
                    score = EXCLUDED.score,
                    result_label = EXCLUDED.result_label,
                    exam_date = EXCLUDED.exam_date
                """,
                assessment_rows,
            )
            assessment_count = len(assessment_rows)

            attendance_rows = []
            for attendance in source["attendance"]:
                attendance_rows.append(
                    (
                        uuid4(),
                        school_id,
                        year_ids[1],
                        student_ids[int(attendance["student_id"])],
                        Date.fromisoformat(attendance["attendance_date"]),
                        attendance["status"],
                    )
                )
            cursor.executemany(
                """
                INSERT INTO attendance
                    (id, school_id, academic_year_id, student_id,
                     attendance_date, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (student_id, attendance_date) DO UPDATE
                SET status = EXCLUDED.status
                """,
                attendance_rows,
            )
            attendance_count = len(attendance_rows)

    return {
        "years": year_count,
        "classes": class_count,
        "students": student_count,
        "enrollments": enrollment_count,
        "subjects": subject_count,
        "teachers": teacher_count,
        "grade_subjects": grade_subject_count,
        "teaching_assignments": teaching_assignment_count,
        "assessments": assessment_count,
        "attendance": attendance_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sql-file", type=Path, default=DEFAULT_SQL)
    parser.add_argument(
        "--dsn",
        help="PostgreSQL DSN. If omitted, EDUOPS_DATABASE_URL or EDUOPS_TEST_MIGRATOR_DSN is used.",
    )
    args = parser.parse_args()
    dsn = args.dsn or os.getenv("EDUOPS_DATABASE_URL") or os.getenv("EDUOPS_TEST_MIGRATOR_DSN")
    if not dsn:
        parser.error("provide --dsn or set EDUOPS_DATABASE_URL/EDUOPS_TEST_MIGRATOR_DSN")
    if not args.sql_file.is_absolute():
        args.sql_file = (ROOT / args.sql_file).resolve()
    if not args.sql_file.is_file():
        parser.error(f"SQL file not found: {args.sql_file}")

    counts = import_source(dsn, args.sql_file)
    print(
        "Imported "
        f"{counts['years']} year(s), "
        f"{counts['classes']} class(es), "
        f"{counts['students']} student(s), "
        f"{counts['enrollments']} enrollment(s), "
        f"{counts['subjects']} subject(s), "
        f"{counts['teachers']} teacher(s), "
        f"{counts['grade_subjects']} grade-subject(s), "
        f"{counts['teaching_assignments']} teaching assignment(s), "
        f"{counts['assessments']} assessment(s), "
        f"{counts['attendance']} attendance row(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
