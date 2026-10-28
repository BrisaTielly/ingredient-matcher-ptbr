"""Evaluate direct LLM matching and E5+LLM reranking on reviewed real data."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

from ingredient_matcher.data import read_canonicals
from ingredient_matcher.llm_eval import evaluate_llm_method
from ingredient_matcher.matchers import Candidate, EmbeddingMatcher


def read_reviewed_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or any(row.get("review_status") != "reviewed" for row in rows):
        raise ValueError("all real-data rows must be human-reviewed before LLM evaluation")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("data/open_prices_annotation.csv"))
    parser.add_argument("--model", required=True, help="Pinned OpenAI model snapshot")
    parser.add_argument("--input-usd-per-million", type=float, required=True)
    parser.add_argument("--output-usd-per-million", type=float, required=True)
    parser.add_argument("--fine-tuned-model", default="BrisaTielly/ingredient-matcher-ptbr-model")
    parser.add_argument("--output", type=Path, default=Path("results/llm_benchmark.json"))
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required; no API request was made.")
    try:
        from openai import OpenAI
    except ImportError as error:
        raise SystemExit("Install the LLM extra with: pip install -e '.[llm]'") from error

    rows = read_reviewed_rows(args.dataset)
    canonicals = [
        Candidate(row["id"], row["name"], 0.0) for row in read_canonicals()
    ]
    retriever = EmbeddingMatcher(args.fine_tuned_model)
    client = OpenAI()
    common = {
        "client": client,
        "model": args.model,
        "rows": rows,
        "input_usd_per_million": args.input_usd_per_million,
        "output_usd_per_million": args.output_usd_per_million,
    }
    results = {
        "direct_llm": evaluate_llm_method(
            **common,
            candidates_for=lambda _raw_name: canonicals,
        ),
        "e5_llm_rerank": evaluate_llm_method(
            **common,
            candidates_for=lambda raw_name: retriever.search(raw_name, top_k=5),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
