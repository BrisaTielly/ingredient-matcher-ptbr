"""Normalização conservadora de descrições de ingredientes."""

from __future__ import annotations

import re
import unicodedata

ABBREVIATIONS = {
    "acuc": "acucar",
    "az": "azeite",
    "bat": "batata",
    "bov": "bovino",
    "cafe": "cafe",
    "cong": "congelado",
    "desc": "descascado",
    "fat": "fatiado",
    "fr": "frango",
    "int": "integral",
    "lt": "leite",
    "muss": "mussarela",
    "qj": "queijo",
    "resf": "resfriado",
    "s": "sem",
    "tom": "tomate",
}

UNITS_RE = re.compile(
    r"\b(?:pct|pcte|pacote|cx|caixa|fd|fardo|un|und|kg|g|gr|mg|l|lt|ml)\b"
    r"|\b\d+(?:[.,]\d+)?\s*(?:kg|g|gr|mg|l|lt|ml|un|und)\b",
    re.IGNORECASE,
)


def strip_accents(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )


def normalize(value: str) -> str:
    """Normaliza caixa, acentos, pontuação, unidades e abreviações conhecidas."""
    text = strip_accents(value.lower())
    text = UNITS_RE.sub(" ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [ABBREVIATIONS.get(token, token) for token in text.split()]
    return " ".join(tokens)
