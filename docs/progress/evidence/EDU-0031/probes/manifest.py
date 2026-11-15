"""Audit-only manifest: hash tracked source files (excluding caches/vendor dirs).

Usage: python -I manifest.py <root> <out.json>
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

EXCLUDE_DIRS = {
    "node_modules", ".venv", ".local", "__pycache__", ".ruff_cache", ".pytest_cache",
    "dist", "test-results", "playwright-report", ".mypy_cache",
}


def main() -> None:
    root, out = sys.argv[1], sys.argv[2]
    files = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace("\\", "/")
            with open(path, "rb") as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
            st = os.stat(path)
            files[rel] = {
                "sha256": digest,
                "size": st.st_size,
                "mtime": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(),
            }
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": root,
        "excluded_dirs": sorted(EXCLUDE_DIRS),
        "file_count": len(files),
        "files": files,
    }
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
    print(f"files={len(files)} out={out}")


if __name__ == "__main__":
    main()
