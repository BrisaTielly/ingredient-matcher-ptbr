"""Geração determinística do dataset sintético."""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANONICALS = ROOT / "data" / "canonicals.csv"
DEFAULT_OUTPUT = ROOT / "data" / "dataset.csv"
SEED = 42

ABBREVIATE = {
    "acucar": "ACUC",
    "azeite": "AZ",
    "batata": "BAT",
    "bovina": "BOV",
    "cebola": "CEB",
    "conserva": "CONS",
    "farinha": "FAR",
    "file": "FILE",
    "frango": "FR",
    "integral": "INT",
    "leite": "LT",
    "mussarela": "MUSS",
    "peito": "PTO",
    "po": "PO",
    "queijo": "QJ",
    "tomate": "TOM",
}

BRANDS = ["SERRA BOA", "CASA NOVA", "SABOR REAL", "VILA SUL", "CAMPO VERDE"]
UNITS = ["1KG", "500G", "PCT 1KG", "CX 12UN", "2,5KG"]

NO_MATCH = [
    "DETERGENTE NEUTRO 5L",
    "ESPONJA DUPLA FACE CX 60",
    "SACO LIXO 100L PCT",
    "GUARDANAPO FOLHA DUPLA",
    "PAPEL TOALHA BOBINA",
    "LUVA NITRILICA PRETA M",
    "ALCOOL GEL 70 5L",
    "DESINFETANTE LAVANDA",
    "FILME PVC 28CM",
    "PAPEL ALUMINIO 45CM",
    "MARMITA ALUMINIO N8",
    "COPO DESCARTAVEL 300ML",
    "TAMPA COPO 300ML",
    "CANUDO BIODEGRADAVEL",
    "PALITO DENTE CX",
    "TOUCA DESCARTAVEL PCT",
    "AVENTAL DESCARTAVEL",
    "SABAO MAQUINA LOUCA",
    "SECANTE MAQUINA LOUCA",
    "LIMPADOR DESENGORDURANTE",
    "CAIXA PIZZA 35CM",
    "SACOLA KRAFT MEDIA",
    "ETIQUETA TERMICA 40X30",
    "BOBINA TERMICA 80MM",
    "FOSFORO LONGO CX",
    "GAS BUTANO CARTUCHO",
    "PANO MULTIUSO ROLO",
    "VASSOURA NYLON",
    "RODO ALUMINIO 40CM",
    "BALDE PLASTICO 20L",
]


def _ascii(value: str) -> str:
    return "".join(
        char for char in unicodedata.normalize("NFKD", value) if not unicodedata.combining(char)
    )


def _abbreviated(name: str, index: int) -> str:
    words = _ascii(name).lower().replace("-", " ").split()
    tokens = [ABBREVIATE.get(word, word[:4].upper()) for word in words if word not in {"de", "do"}]
    return f"{' '.join(tokens).upper()} {UNITS[index % len(UNITS)]}"


def _branded(name: str, index: int) -> str:
    descriptor = ["RESF", "TIPO A", "PREMIUM", "TRADICIONAL", "FOOD SERVICE"][index % 5]
    return f"{_ascii(name).upper()} {descriptor} {BRANDS[index % len(BRANDS)]} {UNITS[(index + 2) % 5]}"


def _noisy(name: str, index: int) -> str:
    text = re.sub(r"[^a-zA-Z0-9 ]", "", _ascii(name)).upper()
    text = text.replace("QUEIJO", "QJ").replace("MUSSARELA", "MUSS").replace("FRANGO", "FR")
    if index % 2 == 0:
        text = text.replace(" ", "  ", 1)
    return f"{text[:24]} {UNITS[(index + 1) % 5]}"


def _split_map(ids: list[str]) -> dict[str, str]:
    shuffled = ids[:]
    random.Random(SEED).shuffle(shuffled)
    train_end = int(len(shuffled) * 0.70)
    val_end = train_end + int(len(shuffled) * 0.10)
    return {
        item_id: "train" if i < train_end else "validation" if i < val_end else "test"
        for i, item_id in enumerate(shuffled)
    }


def read_canonicals(path: Path = DEFAULT_CANONICALS) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    required = {"id", "name", "category"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"canonical CSV must contain {sorted(required)}")
    return rows


def generate_rows(canonicals: list[dict[str, str]]) -> list[dict[str, str]]:
    split_by_id = _split_map([row["id"] for row in canonicals])
    transforms = [("invoice_abbreviation", _abbreviated), ("brand_noise", _branded), ("ocr_noise", _noisy)]
    output: list[dict[str, str]] = []

    for index, canonical in enumerate(canonicals):
        for transform_name, transform in transforms:
            raw_name = transform(canonical["name"], index)
            example_id = hashlib.sha1(
                f"{canonical['id']}:{transform_name}:{raw_name}".encode()
            ).hexdigest()[:12]
            output.append(
                {
                    "example_id": example_id,
                    "raw_name": raw_name,
                    "canonical_id": canonical["id"],
                    "canonical_name": canonical["name"],
                    "category": canonical["category"],
                    "transformation": transform_name,
                    "source_group": canonical["id"],
                    "split": split_by_id[canonical["id"]],
                    "label_source": "synthetic_rule",
                }
            )

    no_match_splits = ["train"] * 21 + ["validation"] * 3 + ["test"] * 6
    random.Random(SEED).shuffle(no_match_splits)
    for raw_name, split in zip(NO_MATCH, no_match_splits, strict=True):
        output.append(
            {
                "example_id": hashlib.sha1(f"NO_MATCH:{raw_name}".encode()).hexdigest()[:12],
                "raw_name": raw_name,
                "canonical_id": "NO_MATCH",
                "canonical_name": "Sem correspondência",
                "category": "fora_catalogo",
                "transformation": "out_of_scope",
                "source_group": f"no_match_{hashlib.md5(raw_name.encode()).hexdigest()[:8]}",
                "split": split,
                "label_source": "human_authored",
            }
        )

    return sorted(output, key=lambda row: (row["split"], row["example_id"]))


def write_dataset(rows: list[dict[str, str]], path: Path = DEFAULT_OUTPUT) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonicals", type=Path, default=DEFAULT_CANONICALS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    rows = generate_rows(read_canonicals(args.canonicals))
    write_dataset(rows, args.output)
    counts = {split: sum(row["split"] == split for row in rows) for split in ("train", "validation", "test")}
    print(f"wrote {len(rows)} examples to {args.output} ({counts})")


if __name__ == "__main__":
    main()
