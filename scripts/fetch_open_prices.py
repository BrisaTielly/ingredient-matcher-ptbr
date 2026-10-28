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

SOURCE = "Open Food Facts Open Prices API"
PRICES_API = "https://prices.openfoodfacts.org/api/v1/prices"
USER_AGENT = "IngredientMatcherPTBR/0.2 (https://github.com/BrisaTielly/ingredient-matcher-ptbr)"
DEFAULT_OUTPUT = Path("data/open_prices_annotation.csv")


def request_json(url: str, *, attempts: int = 5) -> dict[str, Any]:
    headers = {"User-Agent": USER_AGENT}
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


def fetch_page(page: int, size: int = 100) -> dict[str, Any]:
    parameters = {
        "currency": "BRL",
        "duplicate_of__isnull": "true",
        "order_by": "-date",
        "page": page,
        "size": size,
    }
    return request_json(f"{PRICES_API}?{urllib.parse.urlencode(parameters)}")


def annotation_rows(target: int) -> list[dict[str, Any]]:
    matcher = FuzzyMatcher()
    annotations: list[dict[str, Any]] = []
    seen: set[str] = set()
    page = 1
    while len(annotations) < target:
        payload = fetch_page(page)
        batch = payload.get("items", [])
        if not batch:
            break
        for row in batch:
            product = row.get("product") or {}
            raw_name = str(row.get("product_name") or product.get("product_name") or "").strip()
            key = raw_name.casefold()
            if not raw_name or key in seen:
                continue
            seen.add(key)
            candidate = matcher.search(raw_name, top_k=1)[0]
            code = str(row.get("product_code") or product.get("code") or "").strip()
            annotations.append(
                {
                    "raw_name": raw_name,
                    "canonical_id": "",
                    "review_status": "needs_human_review",
                    "suggested_canonical_id": candidate.canonical_id,
                    "suggested_canonical_name": candidate.canonical_name,
                    "suggested_score": f"{candidate.score:.6f}",
                    "category_tag": row.get("category_tag")
                    or ",".join(product.get("categories_tags") or []),
                    "product_code": code,
                    "product_url": f"https://world.openfoodfacts.org/product/{code}" if code else "",
                    "source_price_id": row.get("id") or "",
                }
            )
            if len(annotations) == target:
                break
        if page >= int(payload.get("pages", page)):
            break
        page += 1
    return annotations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=100)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = annotation_rows(args.target)
    if len(rows) < 50:
        raise SystemExit(f"Only {len(rows)} unique descriptions were available; need at least 50.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "source": SOURCE,
        "source_url": PRICES_API,
        "query": {"currency": "BRL", "duplicate_of__isnull": True},
        "retrieved_at": datetime.now(UTC).isoformat(),
        "license": "ODbL-1.0",
        "rows": len(rows),
        "label_status": "needs_human_review",
    }
    args.output.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Wrote {len(rows)} unique real descriptions to {args.output}; "
        "labels still require human review."
    )


if __name__ == "__main__":
    main()
