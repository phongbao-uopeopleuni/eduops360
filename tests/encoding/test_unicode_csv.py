"""Unicode/CSV regression tests: stdlib only, synthetic data."""
import csv
import importlib.util
import tempfile
import unittest
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

spec = importlib.util.spec_from_file_location("student_validator", ROOT / "scripts" / "validate_students_csv.py")
student_validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(student_validator)


class EncodingTests(unittest.TestCase):
    def test_csv_template_bom_and_vietnamese(self):
        sample = ROOT / "samples/templates/students_import_template.csv"
        self.assertTrue(sample.read_bytes().startswith(b"\xef\xbb\xbf"))
        with sample.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 3)
        self.assertIn("Nguyễn", rows[0]["full_name"])
        count, errors = student_validator.validate(sample)
        self.assertEqual((count, errors), (3, []))

    def test_roundtrip_preserves_text_quotes_newline_and_leading_zero(self):
        for encoding in ("utf-8", "utf-8-sig"):
            with self.subTest(encoding=encoding), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "fixture.csv"
                values = ["00125", 'Trần Thị Hồng, "Minh"\nLớp 8A1']
                with path.open("w", encoding=encoding, newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["student_code", "full_name"])
                    writer.writerow(values)
                with path.open("r", encoding="utf-8-sig", newline="") as handle:
                    rows = list(csv.reader(handle))
                self.assertEqual(rows[1], values)

    def test_unicode_normalization_equivalence(self):
        name = "Nguyễn Thị Ánh"
        decomposed = unicodedata.normalize("NFD", name)
        self.assertNotEqual(name, decomposed)
        self.assertEqual(unicodedata.normalize("NFC", decomposed), name)

    def test_reject_malformed_encoding(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.csv"
            path.write_bytes(b"student_code,full_name\n00125,\xff\n")
            _, errors = student_validator.validate(path)
            self.assertTrue(errors)
            self.assertEqual(errors[-1][2], "unicodedecodeerror")

    def test_reject_formula_like_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "formula.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(student_validator.COLUMNS)
                writer.writerow(["HS009", "=1+1", "2012-05-01", "Nam", "2026-2027", "8", "8A1", "active"])
            _, errors = student_validator.validate(path)
            self.assertIn((2, "full_name", "invalid_name"), errors)


if __name__ == "__main__":
    unittest.main()
