#!/usr/bin/env python3
"""Validate core governance directory existence, avoiding platform-specific symlinks."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
required = [
    "frontend/README.md", "backend/README.md", "AGENTS.md", "CLAUDE.md",
    "ai-agent-sp/PROJECT_CONTEXT.md", "ai-agent-sp/OPERATING_RULES.md",
    "ai-agent-sp/ARCHITECTURE.md", "ai-agent-sp/skills/thuc-thi/csv-import-pipeline/SKILL.md",
    "docs/progress/HANDOFF.md", "docs/progress/TASK_BOARD.md",
    "docs/requirements/STUDENT_IMPORT.md",
    "samples/templates/students_import_template.csv",
    "docs/architecture/OWNERSHIP.md", "scripts/sync_task_board.py",
    "scripts/validate_students_csv.py",
]
missing = [p for p in required if not (root/p).is_file()]
if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))
print("Unified AI Agent SP governance structure: OK")
