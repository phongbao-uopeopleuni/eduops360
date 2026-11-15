"""Generate deterministic, explicitly synthetic student CSV fixtures for local tests."""

import argparse
import csv
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_students_csv import COLUMNS, YEAR_RE  # noqa: E402


def generate(destination: Path, count: int, seed: int, academic_year: str) -> None:
    local_root = (ROOT / ".local").resolve()
    resolved_destination = destination.resolve()
    if not resolved_destination.is_relative_to(local_root):
        raise ValueError("Synthetic fixtures may only be written below workspace/.local")
    if not 1 <= count <= 10_000:
        raise ValueError("Fixture count must be between 1 and 10000")
    match = YEAR_RE.fullmatch(academic_year)
    if not match or int(match[2]) != int(match[1]) + 1:
        raise ValueError("Academic year must contain consecutive years YYYY-YYYY")
    start_year = int(match[1])
    if not 1900 <= start_year <= 2100:
        raise ValueError("Fixture academic year must be between 1900 and 2100")
    randomizer = random.Random(seed)
    resolved_destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects existing datasets, including previous fixtures.
    with resolved_destination.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(COLUMNS)
        for index in range(1, count + 1):
            grade = (index - 1) % 12 + 1
            class_index = (index - 1) // (12 * 35) + 1
            birth_year = start_year - grade - 5
            birth_month = randomizer.randint(1, 12)
            birth_day = randomizer.randint(1, 28)
            writer.writerow(
                [
                    f"{index:06d}",
                    f"Học sinh giả lập {index:06d}",
                    f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}",
                    "",
                    academic_year,
                    str(grade),
                    f"{grade}A{class_index}",
                    "active",
                ]
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--count", type=int, choices=[2000, 10000], required=True)
    parser.add_argument("--seed", type=int, default=360)
    parser.add_argument("--academic-year", required=True)
    args = parser.parse_args()
    try:
        generate(args.destination, args.count, args.seed, args.academic_year)
    except (ValueError, FileExistsError) as error:
        parser.exit(1, f"{error}\n")
    print(f"Generated {args.count} synthetic rows at {args.destination}")


if __name__ == "__main__":
    main()
