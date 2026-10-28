"""Build a human-review queue from real Open Prices receipt descriptions."""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ingredient_matcher.matchers import FuzzyMatcher

try:
    from huggingface_hub import get_token
except ImportError:  # Optional for public, unauthenticated dataset access.
    get_token = None

DATASET = "openfoodfacts/open-prices"
DATASET_SERVER = "https://datasets-server.huggingface.co/filter"
DATASET_API = f"https://huggingface.co/api/datasets/{DATASET}"
USER_AGENT = "IngredientMatcherPTBR/0.2 (https://github.com/BrisaTielly/ingredient-matcher-ptbr)"
DEFAULT_OUTPUT = Path("data/open_prices_annotation.csv")


def request_json(url: str, *, attempts: int = 5) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT}
    token = get_token() if get_token else None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            retryable = error.code in {429, 500, 502, 503, 504}
            if not retryable or attempt == attempts - 1:
                raise
        except (TimeoutError, urllib.error.URLError):
            if attempt == attempts - 1:
                raise
        time.sleep(2**attempt)
    raise RuntimeError("unreachable")


def fetch_rows(offset: int, length: int) -> list[dict[str, Any]]:
    parameters = {
        "dataset": DATASET,
        "config": "default",
        "split": "prices",
        "where": '"location_osm_address_country_code"=\'BR\'',
        "orderby": '"date" DESC',
        "offset": offset,
        "length": length,
    }
    payload = request_json(f"{DATASET_SERVER}?{urllib.parse.urlencode(parameters)}")
    return [entry["row"] for entry in payload.get("rows", [])]


def annotation_rows(target: int) -> list[dict[str, Any]]:
    matcher = FuzzyMatcher()
    annotations: list[dict[str, Any]] = []
    seen: set[str] = set()
    offset = 0
    while len(annotations) < target:
        batch = fetch_rows(offset, min(100, target - len(annotations)))
        if not batch:
            break
        for row in batch:
            raw_name = str(row.get("product_name") or "").strip()
            key = raw_name.casefold()
            if not raw_name or key in seen:
                continue
            seen.add(key)
            candidate = matcher.search(raw_name, top_k=1)[0]
            code = str(row.get("product_code") or "").strip()
            annotations.append(
                {
                    "raw_name": raw_name,
                    "canonical_id": "",
                    "review_status": "needs_human_review",
                    "suggested_canonical_id": candidate.canonical_id,
                    "suggested_canonical_name": candidate.canonical_name,
                    "suggested_score": f"{candidate.score:.6f}",
                    "category_tag": row.get("category_tag") or "",
                    "product_code": code,
                    "product_url": f"https://world.openfoodfacts.org/product/{code}" if code else "",
                }
            )
            if len(annotations) == target:
                break
        offset += len(batch)
    return annotations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=100)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    dataset_metadata = request_json(DATASET_API)
    rows = annotation_rows(args.target)
    if len(rows) < args.target:
        raise SystemExit(f"Only {len(rows)} unique descriptions were available; wanted {args.target}.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "source": DATASET,
        "source_revision": dataset_metadata.get("sha"),
        "retrieved_at": datetime.now(UTC).isoformat(),
        "license": "ODbL-1.0",
        "rows": len(rows),
        "label_status": "needs_human_review",
    }
    args.output.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(rows)} rows to {args.output}; labels still require human review.")


if __name__ == "__main__":
    main()
