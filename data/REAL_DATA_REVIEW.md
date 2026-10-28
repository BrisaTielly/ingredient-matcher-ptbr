# Real-data evaluation slice

`open_prices_annotation.csv` is a reviewed evaluation slice made from product names that have at least one observation in the Open Food Facts **Open Prices API**. It contains 60 ingredient matches and 20 hard `NO_MATCH` examples. The positive rows cover 24 canonical IDs; 42 observations use BRL, 37 use EUR, and one legacy price has no currency recorded.

The construction protocol avoids the failure mode where a supermarket sample is almost entirely `NO_MATCH`:

1. Search Open Prices product records with at least one observed price for ingredient-like names.
2. Select 60 products that genuinely map to the kitchen-supply catalogue, across dairy, grains, preserved fish, seasonings and other represented groups.
3. Add 20 confusable Brazilian supermarket products that are outside the catalogue as hard negatives.
4. Assign every label from `raw_name` only. Matcher suggestions are neither shown during review nor stored in the released CSV.
5. Validate the completed labels with `python scripts/validate_real_labels.py`.

`scripts/fetch_open_prices.py` now writes a separate, unlabelled `open_prices_candidates.csv`. It never overwrites the reviewed slice and does not generate automatic label suggestions.

`scripts/evaluate_llm.py` compares direct LLM classification with E5 top-5 plus LLM reranking. It records tokens, latency, total cost and cost per 1,000 items. Prices are required CLI arguments so the report records the assumptions used at execution time instead of silently relying on a changing price table.

The source database is provided by [Open Food Facts](https://world.openfoodfacts.org/) under the Open Database License (ODbL). The generated metadata records the query and retrieval time. This derived annotation table is redistributed under the same share-alike terms.
