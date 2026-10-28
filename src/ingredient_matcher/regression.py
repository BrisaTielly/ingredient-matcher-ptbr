"""Metric regression gate used by CI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def indexed_methods(path: Path) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {row["method"]: row for row in payload["methods"]}


def regression_failures(
    baseline: dict[str, dict],
    candidate: dict[str, dict],
    methods: list[str],
    tolerances: dict[str, float],
) -> list[str]:
    failures: list[str] = []
    for method in methods:
        if method not in baseline or method not in candidate:
            failures.append(f"{method}: missing from baseline or candidate metrics")
            continue
        for metric, tolerance in tolerances.items():
            previous = float(baseline[method]["test"][metric])
            current = float(candidate[method]["test"][metric])
            drop = previous - current
            print(
                f"{method} {metric}: baseline={previous:.4f} "
                f"candidate={current:.4f} drop={drop:.4f} limit={tolerance:.4f}"
            )
            if drop > tolerance + 1e-12:
                failures.append(
                    f"{method} {metric} dropped {drop:.4f}, above the {tolerance:.4f} limit"
                )
    return failures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--method", action="append", required=True)
    parser.add_argument("--max-f1-drop", type=float, default=0.01)
    parser.add_argument("--max-top1-drop", type=float, default=0.01)
    args = parser.parse_args()

    failures = regression_failures(
        indexed_methods(args.baseline),
        indexed_methods(args.candidate),
        args.method,
        {
            "f1": args.max_f1_drop,
            "retrieval_top1_accuracy": args.max_top1_drop,
        },
    )
    if failures:
        raise SystemExit("Regression gate failed:\n- " + "\n- ".join(failures))
    print("Regression gate passed.")
