import csv
from pathlib import Path


def test_reviewed_real_slice_is_balanced_and_has_no_suggestion_leakage():
    path = Path(__file__).parents[1] / "data" / "open_prices_annotation.csv"
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))

    matches = [row for row in rows if row["canonical_id"] != "NO_MATCH"]
    no_matches = [row for row in rows if row["canonical_id"] == "NO_MATCH"]

    assert len(rows) == 80
    assert len(matches) == 60
    assert len(no_matches) == 20
    assert len({row["canonical_id"] for row in matches}) == 24
    assert all(row["review_status"] == "reviewed" for row in rows)
    assert all(not column.startswith("suggested_") for column in rows[0])
