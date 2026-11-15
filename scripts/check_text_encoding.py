#!/usr/bin/env python3
"""Strict UTF-8 check for textual project files; allow BOM only for CSV samples.

Not a security scanner and not a substitute for CSV validation. Avoid printing
file contents (which might include personal data); output only relative paths.
"""
from pathlib import Path
import argparse
import os

EXTENSIONS = {".md", ".py", ".ts", ".tsx", ".js", ".jsx", ".css", ".html", ".json", ".yml", ".yaml", ".sql", ".toml", ".csv", ".txt"}
IGNORE_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".next", ".pytest_cache", ".ruff_cache", ".local", "test-results", "playwright-report"}
BOM = b"\xef\xbb\xbf"


def audit(root: Path):
    checked = 0
    errors = []
    files = []
    for directory, folders, filenames in os.walk(root):
        folders[:] = [name for name in folders if name not in IGNORE_DIRS and not name.endswith('.egg-info')]
        files.extend(Path(directory) / name for name in filenames)
    for p in sorted(files):
        if p.suffix.lower() not in EXTENSIONS:
            continue
        checked += 1
        rel = p.relative_to(root).as_posix()
        raw = p.read_bytes()
        if raw.startswith(BOM) and p.suffix.lower() != ".csv":
            errors.append((rel, "unexpected_utf8_bom"))
        try:
            text = raw.decode("utf-8-sig" if p.suffix.lower() == ".csv" else "utf-8", errors="strict")
        except UnicodeDecodeError:
            errors.append((rel, "invalid_utf8"))
            continue
        if "\ufffd" in text:
            errors.append((rel, "unicode_replacement_character"))
        if "\x00" in text:
            errors.append((rel, "nul_character"))
    return checked, errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    root = parser.parse_args().root
    if not root.is_dir():
        parser.error("root must be a directory")
    checked, errors = audit(root)
    print(f"Checked text files: {checked}; encoding errors: {len(errors)}")
    for name, problem in errors:
        print(f"{name}: {problem}")
    raise SystemExit(1 if errors else 0)

if __name__ == "__main__":
    main()
