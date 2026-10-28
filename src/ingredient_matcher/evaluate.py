"""Avaliação reproduzível com calibração de abstenção na validação."""

from __future__ import annotations

import argparse
import csv
import json
import random
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from ingredient_matcher.data import DEFAULT_OUTPUT
from ingredient_matcher.matchers import EmbeddingMatcher, FuzzyMatcher, Matcher

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results"
DEFAULT_BASE_MODEL = "intfloat/multilingual-e5-small"
BOOTSTRAP_METRICS = (
    "accuracy",
    "precision",
    "recall",
    "f1",
    "coverage",
    "retrieval_top1_accuracy",
    "recall_at_5",
    "no_match_accuracy",
)


def read_dataset(path: Path = DEFAULT_OUTPUT) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def predict_rows(matcher: Matcher, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    for row in rows:
        candidates = matcher.search(row["raw_name"], top_k=5)
        predictions.append(
            {
                **row,
                "top1_id": candidates[0].canonical_id,
                "top1_name": candidates[0].canonical_name,
                "top1_score": candidates[0].score,
                "top5_ids": [candidate.canonical_id for candidate in candidates],
                "candidates": [asdict(candidate) for candidate in candidates],
            }
        )
    return predictions


def metrics_at_threshold(predictions: list[dict[str, Any]], threshold: float) -> dict[str, float | int]:
    accepted = [prediction for prediction in predictions if prediction["top1_score"] >= threshold]
    match_rows = [prediction for prediction in predictions if prediction["canonical_id"] != "NO_MATCH"]
    no_match_rows = [prediction for prediction in predictions if prediction["canonical_id"] == "NO_MATCH"]

    correct_accepted = sum(
        prediction["top1_id"] == prediction["canonical_id"] for prediction in accepted
    )
    correct_matches = sum(
        prediction["top1_score"] >= threshold
        and prediction["top1_id"] == prediction["canonical_id"]
        for prediction in match_rows
    )
    correct_no_match = sum(prediction["top1_score"] < threshold for prediction in no_match_rows)
    correct_total = correct_matches + correct_no_match

    precision = correct_accepted / len(accepted) if accepted else 0.0
    recall = correct_matches / len(match_rows) if match_rows else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    return {
        "n": len(predictions),
        "threshold": round(threshold, 6),
        "accuracy": correct_total / len(predictions) if predictions else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "coverage": len(accepted) / len(predictions) if predictions else 0.0,
        "retrieval_top1_accuracy": sum(
            prediction["top1_id"] == prediction["canonical_id"] for prediction in match_rows
        )
        / len(match_rows)
        if match_rows
        else 0.0,
        "recall_at_5": sum(
            prediction["canonical_id"] in prediction["top5_ids"] for prediction in match_rows
        )
        / len(match_rows)
        if match_rows
        else 0.0,
        "no_match_accuracy": correct_no_match / len(no_match_rows) if no_match_rows else 0.0,
    }


def calibrate_threshold(predictions: list[dict[str, Any]]) -> tuple[float, dict[str, float | int]]:
    scores = sorted({0.0, 1.0, *(float(row["top1_score"]) for row in predictions)})
    candidates = []
    for threshold in scores:
        metrics = metrics_at_threshold(predictions, threshold)
        candidates.append((metrics["f1"], metrics["accuracy"], metrics["precision"], threshold, metrics))
    _, _, _, threshold, metrics = max(candidates, key=lambda item: item[:4])
    return threshold, metrics


def bootstrap_intervals(
    predictions: list[dict[str, Any]],
    threshold: float,
    *,
    iterations: int = 2_000,
    seed: int = 42,
    confidence: float = 0.95,
) -> dict[str, dict[str, float]]:
    """Estimate percentile intervals while preserving match/no-match class counts."""
    if not predictions:
        return {}

    rng = random.Random(seed)
    strata = [
        [row for row in predictions if row["canonical_id"] != "NO_MATCH"],
        [row for row in predictions if row["canonical_id"] == "NO_MATCH"],
    ]
    samples = {metric: [] for metric in BOOTSTRAP_METRICS}
    for _ in range(iterations):
        resampled = [
            row
            for stratum in strata
            for row in (rng.choices(stratum, k=len(stratum)) if stratum else [])
        ]
        metrics = metrics_at_threshold(resampled, threshold)
        for metric in BOOTSTRAP_METRICS:
            samples[metric].append(float(metrics[metric]))

    alpha = (1 - confidence) / 2
    return {
        metric: {
            "low": float(np.quantile(values, alpha)),
            "high": float(np.quantile(values, 1 - alpha)),
        }
        for metric, values in samples.items()
    }


def evaluate_method(
    name: str, matcher: Matcher, validation: list[dict[str, str]], test: list[dict[str, str]]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    validation_predictions = predict_rows(matcher, validation)
    threshold, validation_metrics = calibrate_threshold(validation_predictions)
    test_predictions = predict_rows(matcher, test)
    test_metrics = metrics_at_threshold(test_predictions, threshold)
    confidence_intervals = bootstrap_intervals(test_predictions, threshold)
    return {
        "method": name,
        "threshold_source": "validation",
        "bootstrap": {
            "iterations": 2_000,
            "confidence": 0.95,
            "stratified_by": "match_vs_no_match",
        },
        "validation": validation_metrics,
        "test": test_metrics,
        "test_confidence_intervals": confidence_intervals,
    }, [{"method": name, **row} for row in test_predictions]


def write_results(
    metrics: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    results_dir: Path = RESULTS,
) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "metrics.json").write_text(
        json.dumps({"methods": metrics}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    flat_predictions = [
        {key: value for key, value in row.items() if key != "candidates"} for row in predictions
    ]
    with (results_dir / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(flat_predictions[0]))
        writer.writeheader()
        writer.writerows(flat_predictions)

    lines = [
        "# Evaluation report",
        "",
        "Thresholds were calibrated on validation only; metrics below are from the frozen test split.",
        "",
        "Bootstrap percentile intervals are stratified by match/no-match class (2,000 samples).",
        "",
        "| Method | F1 (95% CI) | Precision | Recall | Top-1 | Recall@5 | No-match acc. | Coverage |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in metrics:
        test = result["test"]
        f1_interval = result["test_confidence_intervals"]["f1"]
        lines.append(
            f"| {result['method']} | {test['f1']:.3f} "
            f"[{f1_interval['low']:.3f}, {f1_interval['high']:.3f}] | "
            f"{test['precision']:.3f} | "
            f"{test['recall']:.3f} | {test['retrieval_top1_accuracy']:.3f} | "
            f"{test['recall_at_5']:.3f} | {test['no_match_accuracy']:.3f} | {test['coverage']:.3f} |"
        )
    (results_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--methods", default="fuzzy,e5")
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    parser.add_argument("--fine-tuned-model", default=str(ROOT / "artifacts" / "model"))
    parser.add_argument("--results-dir", type=Path, default=RESULTS)
    args = parser.parse_args()

    rows = read_dataset(args.dataset)
    validation = [row for row in rows if row["split"] == "validation"]
    test = [row for row in rows if row["split"] == "test"]
    requested = [method.strip() for method in args.methods.split(",")]
    matchers: list[tuple[str, Matcher]] = []
    if "fuzzy" in requested:
        matchers.append(("RapidFuzz", FuzzyMatcher()))
    if "e5" in requested:
        matchers.append(("E5 base", EmbeddingMatcher(args.base_model)))
    if "fine_tuned" in requested:
        matchers.append(("E5 fine-tuned", EmbeddingMatcher(args.fine_tuned_model)))

    all_metrics: list[dict[str, Any]] = []
    all_predictions: list[dict[str, Any]] = []
    for name, matcher in matchers:
        metrics, predictions = evaluate_method(name, matcher, validation, test)
        all_metrics.append(metrics)
        all_predictions.extend(predictions)
    write_results(all_metrics, all_predictions, args.results_dir)
    print((args.results_dir / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
