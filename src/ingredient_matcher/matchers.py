"""Implementações dos matchers comparados no benchmark."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import numpy as np
from rapidfuzz import fuzz

from ingredient_matcher.data import DEFAULT_CANONICALS, read_canonicals
from ingredient_matcher.normalize import normalize


@dataclass(frozen=True)
class Candidate:
    canonical_id: str
    canonical_name: str
    score: float


class Matcher(Protocol):
    def search(self, raw_name: str, top_k: int = 5) -> list[Candidate]: ...


class FuzzyMatcher:
    def __init__(self, canonicals_path: Path = DEFAULT_CANONICALS):
        self.canonicals = read_canonicals(canonicals_path)
        self.normalized = [normalize(row["name"]) for row in self.canonicals]

    def search(self, raw_name: str, top_k: int = 5) -> list[Candidate]:
        query = normalize(raw_name)
        scored = [
            Candidate(row["id"], row["name"], fuzz.WRatio(query, canonical) / 100.0)
            for row, canonical in zip(self.canonicals, self.normalized, strict=True)
        ]
        return sorted(scored, key=lambda candidate: candidate.score, reverse=True)[:top_k]


class EmbeddingMatcher:
    def __init__(
        self,
        model_name_or_path: str,
        canonicals_path: Path = DEFAULT_CANONICALS,
        use_e5_prefixes: bool = True,
    ):
        from sentence_transformers import SentenceTransformer

        self.canonicals = read_canonicals(canonicals_path)
        self.use_e5_prefixes = use_e5_prefixes
        self.model = SentenceTransformer(model_name_or_path)
        names = [self._passage(row["name"]) for row in self.canonicals]
        self.embeddings = self.model.encode(
            names, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False
        )

    def _query(self, value: str) -> str:
        value = normalize(value)
        return f"query: {value}" if self.use_e5_prefixes else value

    def _passage(self, value: str) -> str:
        value = normalize(value)
        return f"passage: {value}" if self.use_e5_prefixes else value

    def search(self, raw_name: str, top_k: int = 5) -> list[Candidate]:
        query = self.model.encode(
            [self._query(raw_name)],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]
        scores = np.dot(self.embeddings, query)
        indices = np.argsort(-scores)[:top_k]
        return [
            Candidate(
                self.canonicals[index]["id"],
                self.canonicals[index]["name"],
                float(scores[index]),
            )
            for index in indices
        ]
