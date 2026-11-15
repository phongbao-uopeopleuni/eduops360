#!/usr/bin/env python3
"""Local student CSV preflight only: no database reads/writes or user data in output."""
import argparse
import csv
from datetime import date
from pathlib import Path
import re
import unicodedata

COLUMNS = [
    "student_code", "full_name", "date_of_birth", "gender",
    "academic_year", "grade_level", "class_code", "enrollment_status",
]
STATUSES = {"active", "transferred", "withdrawn", "graduated"}
GENDERS = {"Nam", "Nữ", "Khác", "Không khai báo", ""}
DANGEROUS = set("=+-@＝＋－＠\t\r\n")
YEAR_RE = re.compile(r"^(\d{4})-(\d{4})$")
CODE_RE = re.compile(r"^[a-zA-Z0-9_-]{1,40}$")
MAX_BYTES = 10 * 1024 * 1024
MAX_ROWS = 100000


def validate(path: Path):
    problems = []
    rows_count = 0
    seen = set()
    if not path.exists() or not path.is_file():
        return 0, [(0, "file", "not_found")]
    if path.stat().st_size > MAX_BYTES:
        return 0, [(0, "file", "exceeds_10mb")]
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, restkey="__EXTRA__", strict=True)
            if reader.fieldnames is None or reader.fieldnames != COLUMNS:
                return 0, [(1, "header", "unexpected_columns_or_order")]
            for row_index, row in enumerate(reader, start=2):
                rows_count += 1
                if rows_count > MAX_ROWS:
                    problems.append((row_index, "file", "exceeds_row_limit"))
                    break
                if "__EXTRA__" in row or any(v is None for v in row.values()):
                    problems.append((row_index, "row", "column_count_mismatch"))
                    continue
                for key in COLUMNS:
                    row[key] = unicodedata.normalize("NFC", row[key].strip())
                code, name, dob, gender, year, grade, cls, status = (row[k] for k in COLUMNS)
                if any("\x00" in value for value in row.values()):
                    problems.append((row_index, "row", "nul_character"))
                if not CODE_RE.fullmatch(code):
                    problems.append((row_index, "student_code", "invalid_code"))
                if not name or len(name) > 120 or name[0] in DANGEROUS:
                    problems.append((row_index, "full_name", "invalid_name"))
                try:
                    d = date.fromisoformat(dob)
                    if d > date.today(): raise ValueError("future")
                except ValueError:
                    problems.append((row_index, "date_of_birth", "invalid_iso_date"))
                if gender not in GENDERS:
                    problems.append((row_index, "gender", "invalid_value"))
                m = YEAR_RE.fullmatch(year)
                if not m or int(m.group(2)) != int(m.group(1)) + 1:
                    problems.append((row_index, "academic_year", "invalid_year"))
                if not grade.isdigit() or not (1 <= int(grade) <= 12):
                    problems.append((row_index, "grade_level", "invalid_grade"))
                if not cls or len(cls) > 30 or cls[0] in DANGEROUS:
                    problems.append((row_index, "class_code", "invalid_class"))
                elif grade.isdigit():
                    found = re.match(r"^(\d{1,2})", cls)
                    if found and int(found.group(1)) != int(grade):
                        problems.append((row_index, "class_code", "grade_mismatch"))
                if status not in STATUSES:
                    problems.append((row_index, "enrollment_status", "invalid_status"))
                dupkey = (code.casefold(), year)
                if dupkey in seen:
                    problems.append((row_index, "student_code", "duplicate_in_year"))
                seen.add(dupkey)
    except (UnicodeError, csv.Error, OSError) as exc:
        problems.append((rows_count + 2, "file", type(exc).__name__.lower()))
    return rows_count, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()
    count, errors = validate(args.csv_file)
    print(f"Rows examined: {count}; errors: {len(errors)}")
    for row, column, code in errors[:50]:
        print(f"row {row}: {column} [{code}]")
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
