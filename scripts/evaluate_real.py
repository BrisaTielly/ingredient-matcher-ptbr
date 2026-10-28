"""Evaluate matchers on the reviewed Open Prices slice."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from ingredient_matcher.data import DEFAULT_OUTPUT
from ingredient_matcher.evaluate import evaluate_method, read_dataset, write_results
from ingredient_matcher.matchers import EmbeddingMatcher, FuzzyMatcher, Matcher


def read_reviewed(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or any(row.get("review_status") != "reviewed" for row in rows):
        raise ValueError("all real-data rows must be reviewed")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("data/open_prices_annotation.csv"))
    parser.add_argument("--calibration-dataset", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--methods", default="fuzzy,fine_tuned")
    parser.add_argument(
        "--fine-tuned-model", default="BrisaTielly/ingredient-matcher-ptbr-model"
    )
    parser.add_argument("--results-dir", type=Path, default=Path("results/real"))
    args = parser.parse_args()

    synthetic = read_dataset(args.calibration_dataset)
    validation = [row for row in synthetic if row["split"] == "validation"]
    real_test = read_reviewed(args.dataset)
    requested = {method.strip() for method in args.methods.split(",")}
    matchers: list[tuple[str, Matcher]] = []
    if "fuzzy" in requested:
        matchers.append(("RapidFuzz", FuzzyMatcher()))
    if "fine_tuned" in requested:
        matchers.append(("E5 fine-tuned", EmbeddingMatcher(args.fine_tuned_model)))

    metrics = []
    predictions = []
    for name, matcher in matchers:
        result, method_predictions = evaluate_method(name, matcher, validation, real_test)
        result["test_source"] = "reviewed_open_prices"
        metrics.append(result)
        predictions.extend(method_predictions)
    write_results(metrics, predictions, args.results_dir)
    report_path = args.results_dir / "report.md"
    report = report_path.read_text(encoding="utf-8").replace(
        "metrics below are from the frozen test split.",
        "metrics below are from the reviewed Open Prices slice.",
    )
    report_path.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
