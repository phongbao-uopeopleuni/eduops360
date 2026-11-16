import unittest
from pathlib import Path

from scripts.check_repository_secrets import scan_text

ROOT = Path(__file__).resolve().parents[2]


class Phase11CiGateTests(unittest.TestCase):
    def test_secret_scanner_rejects_high_confidence_values_without_echoing_them(self):
        github_token = "ghp_" + "a" * 36
        findings = scan_text(f"GITHUB_TOKEN={github_token}\n", "fixture.txt")
        self.assertEqual(findings, ["fixture.txt:1: github_token"])
        self.assertNotIn(github_token, "\n".join(findings))

    def test_secret_scanner_accepts_variable_references_and_placeholders(self):
        content = "POSTGRES_RUNTIME_PASSWORD=${POSTGRES_RUNTIME_PASSWORD}\nAPI_TOKEN=<set-in-secret-store>\n"
        self.assertEqual(scan_text(content, "workflow.yml"), [])

    def test_foundation_workflow_enforces_security_audit_and_offline_migration_gate(self):
        workflow = (ROOT / ".github/workflows/foundation-check.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python scripts/check_repository_secrets.py", workflow)
        self.assertIn("npm audit --omit=dev --audit-level=high", workflow)
        self.assertIn("-e PYTHONIOENCODING=utf-8", workflow)
        self.assertIn("python -m alembic upgrade --sql head", workflow)

    def test_ml_workflow_fails_closed_when_future_ml_code_changes_without_eval_contract(self):
        workflow = (ROOT / ".github/workflows/ml-evaluation-check.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("backend/app/modules/machine_learning/**", workflow)
        self.assertIn("backend/tests/machine_learning", workflow)
        self.assertIn("scripts/evaluate_ml_models.py --check", workflow)


if __name__ == "__main__":
    unittest.main()
