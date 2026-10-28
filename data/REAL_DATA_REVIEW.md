# Real-data evaluation queue

`open_prices_annotation.csv` is generated from real Brazilian product descriptions returned by the Open Food Facts **Open Prices API** for prices in BRL. This source is closer to supplier noise than the synthetic generator.

The file is not an evaluation set until a person reviews every row:

1. Fill `canonical_id` with an ID from `canonicals.csv`, or `NO_MATCH`.
2. Change `review_status` to `reviewed` only after inspecting the raw description and, when available, its product link.
3. Keep the automatic suggestion only as annotation assistance; it must not be treated as ground truth.
4. Run `python scripts/validate_real_labels.py` before evaluating the slice.

After review, `scripts/evaluate_llm.py` compares direct LLM classification with E5 top-5 plus LLM reranking. It records tokens, latency, total cost and cost per 1,000 items. Prices are required CLI arguments so the report records the assumptions used at execution time instead of silently relying on a changing price table.

The source database is provided by [Open Food Facts](https://world.openfoodfacts.org/) under the Open Database License (ODbL). The generated metadata records the query and retrieval time. This derived annotation table is redistributed under the same share-alike terms.
