"""Export the authoritative FastAPI contract without starting a server or database."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    app = create_app(Settings(database_url=None, environment="test", _env_file=None))
    content = json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    destination = ROOT / "contracts/openapi.json"
    if args.check:
        if not destination.is_file() or destination.read_text(encoding="utf-8") != content:
            raise SystemExit("OpenAPI drift: run python scripts/export_openapi.py")
        print("OpenAPI contract matches FastAPI")
        return
    destination.write_text(content, encoding="utf-8")
    print("Exported contracts/openapi.json")


if __name__ == "__main__":
    main()
