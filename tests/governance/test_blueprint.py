import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('validator',ROOT/'scripts/validate_blueprint.py')
validator=importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

class BlueprintTests(unittest.TestCase):
    def test_current_repo_is_valid(self):
        skills,roles,errors=validator.validate(ROOT)
        self.assertGreaterEqual(skills,25)
        self.assertGreaterEqual(roles,10)
        self.assertEqual(errors,[])

    def test_empty_tree_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            skills,roles,errors=validator.validate(Path(d))
            self.assertGreater(len(errors),5)

if __name__ == '__main__': unittest.main()
