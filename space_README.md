---
title: Ingredient Matcher PT-BR
emoji: 🧾
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 6.30.0
python_version: "3.12"
app_file: app.py
pinned: true
license: mit
models:
  - BrisaTielly/ingredient-matcher-ptbr-model
datasets:
  - BrisaTielly/ingredient-matcher-ptbr
preload_from_hub:
  - BrisaTielly/ingredient-matcher-ptbr-model
short_description: Entity matching de ingredientes em português com abstenção calibrada.
---

# Ingredient Matcher PT-BR

Liga descrições ruidosas de compras e notas fiscais a 100 ingredientes canônicos em português.

Experimente `QJ MUSS FAT PCT 1KG`. O modelo mostra os cinco candidatos mais próximos e abstém quando o score fica abaixo do limiar calibrado na validação.

O benchmark completo, os dados sintéticos e o código de treinamento estão no [GitHub](https://github.com/BrisaTielly/ingredient-matcher-ptbr).
