import tempfile
import unittest
from pathlib import Path

from scripts.generate_synthetic_students import ROOT, generate


class InfrastructureSafetyTests(unittest.TestCase):
    def test_compose_database_healthcheck_uses_tcp_loopback(self):
        compose = (ROOT / "infra/compose.dev.yml").read_text(encoding="utf-8")
        self.assertIn("pg_isready -h 127.0.0.1", compose)

    def test_playwright_ports_and_reuse_are_explicit(self):
        config = (ROOT / "frontend/playwright.config.ts").read_text(encoding="utf-8")
        self.assertIn("PLAYWRIGHT_API_PORT", config)
        self.assertIn("PLAYWRIGHT_FRONTEND_PORT", config)
        self.assertNotIn("--port 8000", config)
        self.assertIn("PLAYWRIGHT_REUSE_SERVER === '1'", config)
        self.assertIn("EDUOPS_DATABASE_URL", config)

    def test_generator_rejects_output_outside_workspace_local(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "students.csv"
            with self.assertRaises(ValueError):
                generate(destination, 1, 360, "2026-2027")
            self.assertFalse(destination.exists())

    def test_runtime_image_excludes_development_dependencies(self):
        dockerfile = (ROOT / "backend/Dockerfile").read_text(encoding="utf-8")
        self.assertIn("requirements.runtime.lock", dockerfile)
        runtime_lock = (ROOT / "backend/requirements.runtime.lock").read_text(
            encoding="utf-8"
        )
        development_lock = (ROOT / "backend/requirements.lock").read_text(
            encoding="utf-8"
        )
        self.assertLessEqual(
            set(runtime_lock.splitlines()), set(development_lock.splitlines())
        )
        for package in ("httpx2==", "pytest==", "ruff=="):
            self.assertNotIn(package, runtime_lock)

    def test_examples_and_migrations_use_explicit_database_roles(self):
        backend_example = (ROOT / "backend/.env.example").read_text(encoding="utf-8")
        migration_env = (ROOT / "backend/migrations/env.py").read_text(encoding="utf-8")
        self.assertIn("eduops_runtime", backend_example)
        self.assertIn('os.environ.get("EDUOPS_DATABASE_URL")', migration_env)
        self.assertIn("Settings(_env_file=None)", migration_env)

    def test_live_integration_tests_do_not_mutate_seeded_admin_roles(self):
        source = (ROOT / "backend/tests/integration/test_auth_api.py").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("system_admin", source)
        self.assertNotIn("WHERE code = 'auditor'", source)

    def test_foundation_ci_uses_current_database_roles(self):
        workflow = (ROOT / ".github/workflows/foundation-check.yml").read_text(
            encoding="utf-8"
        )
        for variable in (
            "POSTGRES_MIGRATOR_PASSWORD",
            "POSTGRES_RUNTIME_PASSWORD",
            "POSTGRES_AUDIT_WORKER_PASSWORD",
        ):
            self.assertIn(f"{variable}=", workflow)
        self.assertNotIn("'POSTGRES_PASSWORD='", workflow)
        self.assertNotIn("exec -T backend python -m alembic", workflow)
        self.assertIn("run --rm migrate python -m alembic check", workflow)


if __name__ == "__main__":
    unittest.main()
