import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RailwayPackageTests(unittest.TestCase):
    def test_runtime_configuration_does_not_run_owner_migrations(self):
        web = json.loads((ROOT / "railway.json").read_text())
        migrator = json.loads((ROOT / "infra/railway.migrate.json").read_text())
        self.assertNotIn("preDeployCommand", web["deploy"])
        self.assertNotIn("startCommand", web["deploy"])
        self.assertEqual(web["deploy"]["healthcheckPath"], "/api/v1/health/ready")
        self.assertEqual(migrator["deploy"]["startCommand"], "python -m app.staging_migrate")
        self.assertEqual(migrator["deploy"]["restartPolicyType"], "NEVER")

    def test_root_build_context_excludes_local_sensitive_material(self):
        ignored = (ROOT / ".dockerignore").read_text().splitlines()
        for pattern in (".git", ".local", "**/.env", "**/.env.*", "**/logs",
                        "**/private-data", "**/backups", "**/uploads"):
            self.assertIn(pattern, ignored)
        dockerfile = (ROOT / "infra/Dockerfile.railway").read_text()
        self.assertIn("COPY --from=frontend", dockerfile)
        self.assertIn("USER eduops", dockerfile)
        self.assertNotIn('"dev"', dockerfile)
