"""LLM and hybrid evaluation helpers with explicit token-cost accounting."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

from ingredient_matcher.matchers import Candidate


def classification_metrics(expected: list[str], predicted: list[str]) -> dict[str, float | int]:
    if len(expected) != len(predicted):
        raise ValueError("expected and predicted must have the same length")
    accepted = [index for index, value in enumerate(predicted) if value != "NO_MATCH"]
    match_rows = [index for index, value in enumerate(expected) if value != "NO_MATCH"]
    no_match_rows = [index for index, value in enumerate(expected) if value == "NO_MATCH"]
    correct_accepted = sum(predicted[index] == expected[index] for index in accepted)
    correct_matches = sum(predicted[index] == expected[index] for index in match_rows)
    correct_no_match = sum(predicted[index] == "NO_MATCH" for index in no_match_rows)
    precision = correct_accepted / len(accepted) if accepted else 0.0
    recall = correct_matches / len(match_rows) if match_rows else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "n": len(expected),
        "accuracy": (correct_matches + correct_no_match) / len(expected) if expected else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "coverage": len(accepted) / len(expected) if expected else 0.0,
        "no_match_accuracy": correct_no_match / len(no_match_rows) if no_match_rows else 0.0,
    }


def cost_summary(
    *,
    input_tokens: int,
    output_tokens: int,
    item_count: int,
    input_usd_per_million: float,
    output_usd_per_million: float,
) -> dict[str, float | int]:
    total_usd = (
        input_tokens * input_usd_per_million + output_tokens * output_usd_per_million
    ) / 1_000_000
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_usd": total_usd,
        "usd_per_1000_items": total_usd * 1_000 / item_count if item_count else 0.0,
    }


def match_with_llm(client: Any, model: str, raw_name: str, candidates: list[Candidate]):
    allowed_ids = [candidate.canonical_id for candidate in candidates] + ["NO_MATCH"]
    candidate_payload = [
        {"canonical_id": candidate.canonical_id, "name": candidate.canonical_name}
        for candidate in candidates
    ]
    schema = {
        "type": "object",
        "properties": {
            "canonical_id": {"type": "string", "enum": allowed_ids},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reason": {"type": "string"},
        },
        "required": ["canonical_id", "confidence", "reason"],
        "additionalProperties": False,
    }
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "developer",
                "content": (
                    "Match a noisy Brazilian Portuguese supplier description to exactly one "
                    "candidate. Ignore brand, quantity and packaging. Choose NO_MATCH when the "
                    "item is not represented. Return only the requested structured output."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {"raw_name": raw_name, "candidates": candidate_payload}, ensure_ascii=False
                ),
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "ingredient_match",
                "strict": True,
                "schema": schema,
            }
        },
    )
    return json.loads(response.output_text), response.usage


def evaluate_llm_method(
    *,
    client: Any,
    model: str,
    rows: list[dict[str, str]],
    candidates_for: Callable[[str], list[Candidate]],
    input_usd_per_million: float,
    output_usd_per_million: float,
) -> dict[str, Any]:
    predicted: list[str] = []
    input_tokens = 0
    output_tokens = 0
    started = time.perf_counter()
    for row in rows:
        decision, usage = match_with_llm(client, model, row["raw_name"], candidates_for(row["raw_name"]))
        predicted.append(decision["canonical_id"])
        input_tokens += int(usage.input_tokens)
        output_tokens += int(usage.output_tokens)
    elapsed = time.perf_counter() - started
    return {
        "model": model,
        "metrics": classification_metrics(
            [row["canonical_id"] for row in rows], predicted
        ),
        "cost": cost_summary(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            item_count=len(rows),
            input_usd_per_million=input_usd_per_million,
            output_usd_per_million=output_usd_per_million,
        ),
        "latency_seconds": elapsed,
        "seconds_per_item": elapsed / len(rows) if rows else 0.0,
        "predictions": predicted,
    }
