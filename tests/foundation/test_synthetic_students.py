import csv
import tempfile
import unicodedata
import unittest
from pathlib import Path

from scripts.generate_synthetic_students import ROOT, generate
from scripts.validate_students_csv import validate


class SyntheticStudentsTests(unittest.TestCase):
    def test_2k_and_10k_fixtures_validate_and_preserve_codes(self):
        for count in (2000, 10000):
            with (
                self.subTest(count=count),
                tempfile.TemporaryDirectory(dir=ROOT / ".local") as directory,
            ):
                path = Path(directory) / "students.csv"
                generate(path, count, 360, "2026-2027")
                self.assertEqual(validate(path), (count, []))
                self.assertTrue(path.read_bytes().startswith(b"\xef\xbb\xbf"))
                with path.open(encoding="utf-8-sig", newline="") as stream:
                    rows = list(csv.DictReader(stream))
                self.assertEqual(rows[0]["student_code"], "000001")
                self.assertEqual(
                    {row["grade_level"] for row in rows}, {str(n) for n in range(1, 13)}
                )
                self.assertTrue(all("giả lập" in row["full_name"] for row in rows))
                self.assertTrue(
                    all(
                        unicodedata.is_normalized("NFC", row["full_name"])
                        for row in rows
                    )
                )

    def test_same_seed_produces_identical_bytes_and_protects_existing_files(self):
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as directory:
            first, second = (
                Path(directory) / name for name in ("first.csv", "second.csv")
            )
            generate(first, 20, 360, "2026-2027")
            generate(second, 20, 360, "2026-2027")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            original = first.read_bytes()
            with self.assertRaises(FileExistsError):
                generate(first, 20, 999, "2026-2027")
            self.assertEqual(first.read_bytes(), original)

    def test_invalid_inputs_fail_before_creating_output(self):
        for count, year in ((0, "2026-2027"), (10001, "2026-2027"), (20, "2026-2028")):
            with (
                self.subTest(count=count, year=year),
                tempfile.TemporaryDirectory(dir=ROOT / ".local") as directory,
            ):
                path = Path(directory) / "invalid.csv"
                with self.assertRaises(ValueError):
                    generate(path, count, 360, year)
                self.assertFalse(path.exists())
