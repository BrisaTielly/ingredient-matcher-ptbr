"""Validate that the real-data slice has been completely reviewed."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ingredient_matcher.data import read_canonicals


def validation_errors(path: Path) -> list[str]:
    valid_ids = {row["id"] for row in read_canonicals()} | {"NO_MATCH"}
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    errors: list[str] = []
    if len(rows) < 100:
        errors.append(f"expected at least 100 rows, found {len(rows)}")
    for index, row in enumerate(rows, start=2):
        if row.get("review_status") != "reviewed":
            errors.append(f"line {index}: review_status is not reviewed")
        if row.get("canonical_id") not in valid_ids:
            errors.append(f"line {index}: invalid canonical_id {row.get('canonical_id')!r}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path", type=Path, nargs="?", default=Path("data/open_prices_annotation.csv")
    )
    args = parser.parse_args()
    errors = validation_errors(args.path)
    if errors:
        preview = "\n- ".join(errors[:20])
        suffix = f"\n... and {len(errors) - 20} more" if len(errors) > 20 else ""
        raise SystemExit(f"Real-data validation failed:\n- {preview}{suffix}")
    print("Real-data labels are complete and valid.")
