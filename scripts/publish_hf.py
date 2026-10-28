"""Publica dataset, modelo e Space no Hugging Face Hub."""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--private", action="store_true")
    args = parser.parse_args()
    api = HfApi()

    dataset_id = f"{args.namespace}/ingredient-matcher-ptbr"
    model_id = f"{args.namespace}/ingredient-matcher-ptbr-model"
    space_id = f"{args.namespace}/ingredient-matcher-ptbr"

    api.create_repo(dataset_id, repo_type="dataset", private=args.private, exist_ok=True)
    for source, destination in [
        (ROOT / "dataset_card.md", "README.md"),
        (ROOT / "data" / "dataset.csv", "dataset.csv"),
        (ROOT / "data" / "canonicals.csv", "canonicals.csv"),
    ]:
        api.upload_file(path_or_fileobj=source, path_in_repo=destination, repo_id=dataset_id, repo_type="dataset")

    api.create_repo(model_id, repo_type="model", private=args.private, exist_ok=True)
    api.upload_folder(folder_path=ROOT / "artifacts" / "model", repo_id=model_id, repo_type="model")
    api.upload_file(path_or_fileobj=ROOT / "model_card.md", path_in_repo="README.md", repo_id=model_id, repo_type="model")

    api.create_repo(space_id, repo_type="space", space_sdk="gradio", private=args.private, exist_ok=True)
    allow = [
        "app.py",
        "README.md",
        "LICENSE",
        "pyproject.toml",
        "requirements.txt",
        "data/canonicals.csv",
        "results/metrics.json",
        "src/ingredient_matcher/*.py",
    ]
    api.upload_folder(folder_path=ROOT, repo_id=space_id, repo_type="space", allow_patterns=allow)

    print(f"dataset: https://huggingface.co/datasets/{dataset_id}")
    print(f"model: https://huggingface.co/{model_id}")
    print(f"space: https://huggingface.co/spaces/{space_id}")


if __name__ == "__main__":
    main()
