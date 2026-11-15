import tempfile
import unittest
from pathlib import Path

from scripts.check_text_encoding import audit
from scripts.validate_blueprint import validate


class SourceScannerTests(unittest.TestCase):
    def test_dependency_cache_is_skipped_but_project_source_is_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("node_modules/package", ".venv/Lib", ".local/tmp"):
                path = root / folder / "invalid.py"
                path.parent.mkdir(parents=True)
                path.write_bytes(b"\xff")
            source = root / "source.py"
            source.write_bytes(b"\xff")
            self.assertEqual(audit(root), (1, [("source.py", "invalid_utf8")]))
            _, _, errors = validate(root)
            encoding_errors = [
                error for error in errors if error.startswith("invalid UTF-8")
            ]
            self.assertEqual(encoding_errors, ["invalid UTF-8 source.py"])
