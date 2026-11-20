import unicodedata

from app.modules.students.import_pipeline import (
    build_student_export_csv,
    decode_csv,
    escape_formula,
    normalize_row,
)


def test_decode_accepts_bom_utf8_and_preserves_leading_zero():
    raw = (
        "\ufeffstudent_code,full_name,date_of_birth,gender,academic_year,"
        "grade_level,class_code,enrollment_status\n"
        "HS0001,Nguyễn Văn An,2012-05-15,Nam,2026-2027,8,8A1,active\n"
    ).encode("utf-8")
    error, rows = decode_csv(raw)
    assert error is None
    assert rows[0]["student_code"] == "HS0001"


def test_decode_rejects_invalid_utf8_and_malformed_header():
    assert decode_csv(b"\xff")[0] == "INVALID_UTF8"
    assert decode_csv(b"wrong,header\nx,y\n")[0] == "UNEXPECTED_COLUMNS_OR_ORDER"


def test_normalize_row_converts_nfd_to_nfc_and_rejects_bad_year():
    nfd_name = unicodedata.normalize("NFD", "Nguyễn Văn An")
    row = {
        "student_code": "HS0001",
        "full_name": nfd_name,
        "date_of_birth": "2012-05-15",
        "gender": "Nam",
        "academic_year": "2026-2028",
        "grade_level": "8",
        "class_code": "8A1",
        "enrollment_status": "active",
    }
    values, errors = normalize_row(row)
    assert values["full_name"] == unicodedata.normalize("NFC", nfd_name)
    assert any(error["code"] == "INVALID_YEAR" for error in errors)


def test_formula_export_is_safely_prefixed_and_csv_uses_bom():
    assert escape_formula("=1+1") == "'=1+1"
    assert escape_formula("Nguyễn Văn An") == "Nguyễn Văn An"
    assert (
        build_student_export_csv(
            [],
            [],
            academic_year_name="2026-2027",
            classes=[],
        )[:3]
        == b"\xef\xbb\xbf"
    )
