---
language:
- pt
license: mit
task_categories:
- text-classification
tags:
- entity-matching
- food-tech
- synthetic-data
pretty_name: Ingredient Matcher PT-BR
size_categories:
- n<1K
---

# Ingredient Matcher PT-BR

Dataset sintético e auditável para ligar descrições ruidosas de compras de restaurantes a ingredientes canônicos em português brasileiro.

## Estrutura

- 100 ingredientes canônicos de uso comum em food service.
- Três variantes positivas por ingrediente: abreviações de nota fiscal, marca/descritor e ruído semelhante a OCR.
- 30 exemplos fora do catálogo, rotulados como `NO_MATCH`.
- 330 exemplos no total, com splits por ingrediente: variantes do mesmo ingrediente nunca atravessam os splits.

## Colunas

`raw_name`, `canonical_id`, `canonical_name`, `category`, `transformation`, `source_group`, `split` e `label_source`.

## Geração e revisão

O dataset é produzido por regras determinísticas em `src/ingredient_matcher/data.py`, com seed fixa. Os exemplos `NO_MATCH` foram escritos manualmente. O conjunto de teste foi separado antes da calibração e contém ingredientes não vistos pelo fine-tuning.

## Uso pretendido

Benchmark educacional de entity matching, retrieval e calibração de abstenção. Não deve decidir compras, estoque ou informação nutricional sem revisão e dados reais do domínio.

## Limitações

Os nomes positivos são sintéticos e não reproduzem toda a variação de fornecedores reais. Marcas são fictícias. As categorias e os canônicos são uma taxonomia pequena, criada para este experimento; não constituem uma cópia da TACO nem um catálogo comercial.
