---
language:
- pt
license: mit
library_name: sentence-transformers
pipeline_tag: sentence-similarity
tags:
- sentence-transformers
- entity-matching
- food-tech
base_model: intfloat/multilingual-e5-small
---

# Ingredient Matcher PT-BR Model

Fine-tuning de `intfloat/multilingual-e5-small` para recuperar ingredientes canônicos a partir de descrições ruidosas em português brasileiro.

## Treinamento

- Objetivo: `MultipleNegativesRankingLoss`.
- Base: `intfloat/multilingual-e5-small`.
- Dados: 210 pares sintéticos do split de treino do dataset Ingredient Matcher PT-BR.
- Entradas: prefixos E5 `query:` e `passage:`.
- Épocas: 2; batch size: 16; learning rate: `2e-5`.
- Ingredientes do teste não aparecem no treino.
- Seed: 42.

## Avaliação

Os números publicados no README do repositório são gerados por `python -m ingredient_matcher.evaluate` usando o mesmo catálogo e avaliador para RapidFuzz, E5 base e este modelo. O limiar de abstenção é calibrado na validação e congelado antes do teste.

No teste de 66 exemplos, o modelo atingiu F1 0,975, top-1 accuracy 0,983, recall@5 1,000 e acurácia de `NO_MATCH` 1,000. O E5 base obteve F1 0,891 sob o mesmo protocolo.

## Uso

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BrisaTielly/ingredient-matcher-ptbr-model")
embedding = model.encode(["query: qj muss fat 1kg"], normalize_embeddings=True)
```

## Limitações

O modelo foi ajustado em poucos exemplos sintéticos. Deve ser reavaliado com nomes reais, respeitando privacidade e licença dos dados, antes de qualquer uso operacional.
