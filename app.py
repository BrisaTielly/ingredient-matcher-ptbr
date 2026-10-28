"""Hugging Face Space for Ingredient Matcher PT-BR."""

from __future__ import annotations

import json
import os
from pathlib import Path

import gradio as gr

from ingredient_matcher.matchers import EmbeddingMatcher

MODEL_ID = os.getenv("MODEL_ID", "BrisaTielly/ingredient-matcher-ptbr-model")
METRICS_PATH = Path("results/metrics.json")
matcher = EmbeddingMatcher(MODEL_ID)


def _threshold() -> float:
    if not METRICS_PATH.exists():
        return 0.75
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    fine_tuned = next(
        (method for method in metrics["methods"] if method["method"] == "E5 fine-tuned"), None
    )
    return float(fine_tuned["test"]["threshold"]) if fine_tuned else 0.75


THRESHOLD = _threshold()


def match_ingredient(raw_name: str):
    if not raw_name or not raw_name.strip():
        return "Digite uma descrição.", []
    candidates = matcher.search(raw_name, top_k=5)
    decision = "match" if candidates[0].score >= THRESHOLD else "revisar"
    summary = (
        f"**{decision.upper()}** · {candidates[0].canonical_name} · "
        f"score {candidates[0].score:.3f} · limiar {THRESHOLD:.3f}"
    )
    table = [[candidate.canonical_name, candidate.canonical_id, candidate.score] for candidate in candidates]
    return summary, table


with gr.Blocks(title="Ingredient Matcher PT-BR") as demo:
    gr.Markdown(
        "# Ingredient Matcher PT-BR\n"
        "Liga descrições ruidosas de compras e notas fiscais a 100 ingredientes canônicos. "
        "O limiar de abstenção foi calibrado apenas na validação."
    )
    with gr.Row():
        raw_name = gr.Textbox(
            label="Descrição do fornecedor",
            placeholder="Ex.: QJ MUSS FAT PCT 1KG",
        )
        submit = gr.Button("Encontrar ingrediente", variant="primary")
    decision = gr.Markdown()
    candidates = gr.Dataframe(
        headers=["Ingrediente", "ID canônico", "Score"],
        datatype=["str", "str", "number"],
        interactive=False,
    )
    gr.Examples(
        examples=["QJ MUSS FAT PCT 1KG", "TOM ITALIANO CX 12UN", "DETERGENTE NEUTRO 5L"],
        inputs=raw_name,
    )
    submit.click(match_ingredient, inputs=raw_name, outputs=[decision, candidates])
    raw_name.submit(match_ingredient, inputs=raw_name, outputs=[decision, candidates])


if __name__ == "__main__":
    demo.launch()
