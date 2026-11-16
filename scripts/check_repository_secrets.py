"""Fail CI when tracked source contains high-confidence credential material.

This is a deliberately narrow guardrail, not a replacement for an approved
secret manager or an external security review. It never prints a matched value.
"""

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIPPED_PARTS = {".git", ".local", "node_modules", ".venv"}
TOKEN_PATTERNS = (
    ("private_key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
)
SENSITIVE_ASSIGNMENT = re.compile(
    r"^[ \t]*(?:export[ \t]+)?[A-Z][A-Z0-9_]*(?:PASSWORD|SECRET|TOKEN|API_KEY|PRIVATE_KEY)[A-Z0-9_]*[ \t]*=[ \t]*(?P<value>.+?)\s*$"
)


def _is_placeholder(value: str) -> bool:
    normalized = value.strip().strip("'\"").lower()
    return (
        not normalized
        or normalized.startswith(("$", "{{", "<"))
        or normalized in {"change-me", "example", "placeholder", "replace-me"}
    )


def scan_text(content: str, display_path: str) -> list[str]:
    """Return sanitized finding identifiers for text without exposing matches."""
    findings: list[str] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        kinds = [kind for kind, pattern in TOKEN_PATTERNS if pattern.search(line)]
        if not kinds:
            assignment = SENSITIVE_ASSIGNMENT.search(line)
            if assignment and not _is_placeholder(assignment.group("value")):
                kinds.append("sensitive_assignment")
        findings.extend(f"{display_path}:{line_number}: {kind}" for kind in kinds)
    return findings


def tracked_paths(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    paths: list[Path] = []
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        relative = Path(raw_path.decode("utf-8"))
        if relative.name.startswith(".env") or any(part in SKIPPED_PARTS for part in relative.parts):
            continue
        paths.append(relative)
    return paths


def scan_repository(root: Path = ROOT) -> list[str]:
    findings: list[str] = []
    for relative in tracked_paths(root):
        path = root / relative
        content = path.read_text(encoding="utf-8", errors="replace")
        findings.extend(scan_text(content, relative.as_posix()))
    return findings


def main() -> int:
    findings = scan_repository()
    if findings:
        print("Repository secret scan failed; values are intentionally redacted:")
        print("\n".join(findings))
        return 1
    print("Repository secret scan: no high-confidence tracked values found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
