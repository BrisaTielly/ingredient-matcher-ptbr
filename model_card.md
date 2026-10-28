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

No teste sintético de 66 exemplos, o modelo atingiu F1 0,975 (IC bootstrap 95% [0,932; 1,000]), top-1 accuracy 0,983, recall@5 1,000 e acurácia de `NO_MATCH` 1,000. O E5 base obteve F1 0,891 (IC 95% [0,821; 0,950]) sob o mesmo protocolo. Os intervalos se sobrepõem; a amostra pequena não sustenta uma conclusão forte de superioridade.

Em uma fatia externa revisada do Open Prices com 60 matches e 20 negativos difíceis, o modelo obteve F1 0,874 (IC bootstrap 95% [0,810; 0,931]), top-1 0,950, recall@5 1,000 e acurácia de `NO_MATCH` 0,700. O RapidFuzz obteve F1 0,605 (IC 95% [0,492; 0,708]) sob os mesmos rótulos e limiares calibrados na validação sintética.

## Uso

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BrisaTielly/ingredient-matcher-ptbr-model")
embedding = model.encode(["query: qj muss fat 1kg"], normalize_embeddings=True)
```

## Limitações

O modelo foi ajustado em poucos exemplos sintéticos. A fatia real foi selecionada para conter 60 itens compatíveis com o catálogo e não representa a frequência natural de compras de restaurantes. Avaliações operacionais ainda precisam de dados do domínio e monitoramento contínuo.
