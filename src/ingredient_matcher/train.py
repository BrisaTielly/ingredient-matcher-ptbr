"""Fine-tuning contrastivo do E5 para matching de ingredientes."""

from __future__ import annotations

import argparse
import random
from pathlib import Path

import numpy as np

from ingredient_matcher.data import DEFAULT_OUTPUT
from ingredient_matcher.evaluate import DEFAULT_BASE_MODEL, read_dataset
from ingredient_matcher.normalize import normalize

ROOT = Path(__file__).resolve().parents[2]


def training_pairs(dataset_path: Path = DEFAULT_OUTPUT) -> list[tuple[str, str]]:
    rows = read_dataset(dataset_path)
    return [
        (f"query: {normalize(row['raw_name'])}", f"passage: {normalize(row['canonical_name'])}")
        for row in rows
        if row["split"] == "train" and row["canonical_id"] != "NO_MATCH"
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--base-model", default=DEFAULT_BASE_MODEL)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts" / "model")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    import torch
    from sentence_transformers import InputExample, SentenceTransformer, losses
    from torch.utils.data import DataLoader

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    pairs = training_pairs(args.dataset)
    examples = [InputExample(texts=[query, passage]) for query, passage in pairs]
    loader = DataLoader(examples, shuffle=True, batch_size=args.batch_size)
    model = SentenceTransformer(args.base_model)
    loss = losses.MultipleNegativesRankingLoss(model)
    warmup_steps = max(1, int(len(loader) * args.epochs * 0.1))
    model.fit(
        train_objectives=[(loader, loss)],
        epochs=args.epochs,
        warmup_steps=warmup_steps,
        optimizer_params={"lr": 2e-5},
        show_progress_bar=True,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    model.save(str(args.output))
    print(f"saved model to {args.output} using {len(examples)} pairs")


if __name__ == "__main__":
    main()
