import unittest
from pathlib import Path

from scripts.import_school_academic_sql import (
    load_source,
    map_gender,
    map_student_status,
)


class SchoolAcademicImportTest(unittest.TestCase):
    def test_source_counts(self):
        source = load_source(
            Path(__file__).resolve().parents[1] / "backend" / "school_academic_2000_import.sql"
        )
        self.assertEqual(len(source["years"]), 1)
        self.assertEqual(len(source["classes"]), 72)
        self.assertEqual(len(source["students"]), 2000)
        self.assertEqual(len(source["subjects"]), 26)
        self.assertEqual(len(source["teachers"]), 226)
        self.assertEqual(len(source["grade_subjects"]), 151)
        self.assertEqual(len(source["teaching_assignments"]), 1632)
        self.assertEqual(len(source["assessments"]), 50921)
        self.assertEqual(len(source["attendance"]), 40000)

    def test_status_and_gender_mapping(self):
        self.assertEqual(map_gender("NAM"), "NAM")
        self.assertEqual(map_gender("NU"), "NU")
        self.assertEqual(map_student_status("DANG_HOC"), ("active", None))
        self.assertEqual(map_student_status("BAO_LUU"), ("withdrawn", "Nguồn dữ liệu: BAO_LUU"))


if __name__ == "__main__":
    unittest.main()
