---
language:
- pt
license: odbl
task_categories:
- text-classification
tags:
- entity-matching
- food-tech
- synthetic-data
- open-food-facts
pretty_name: Ingredient Matcher PT-BR
size_categories:
- n<1K
---

# Ingredient Matcher PT-BR

Dataset auditável para ligar descrições ruidosas de compras de restaurantes a ingredientes canônicos em português brasileiro. Além do conjunto sintético, inclui uma fatia externa revisada com nomes observados no Open Prices.

## Estrutura

- 100 ingredientes canônicos de uso comum em food service.
- Três variantes positivas por ingrediente: abreviações de nota fiscal, marca/descritor e ruído semelhante a OCR.
- 30 exemplos fora do catálogo, rotulados como `NO_MATCH`.
- 330 exemplos no total, com splits por ingrediente: variantes do mesmo ingrediente nunca atravessam os splits.
- 80 nomes observados no Open Prices: 60 matches de ingredientes e 20 negativos difíceis, cobrindo 24 IDs canônicos positivos.

## Colunas

`raw_name`, `canonical_id`, `canonical_name`, `category`, `transformation`, `source_group`, `split` e `label_source`.

`open_prices_annotation.csv` contém `raw_name`, rótulo revisado, grupo de seleção, categoria de origem, código do produto e referência à observação de preço. O arquivo não contém sugestões automáticas.

## Geração e revisão

O dataset é produzido por regras determinísticas em `src/ingredient_matcher/data.py`, com seed fixa. Os exemplos `NO_MATCH` foram escritos manualmente. O conjunto de teste foi separado antes da calibração e contém ingredientes não vistos pelo fine-tuning.

A fatia externa foi obtida da API do [Open Prices](https://prices.openfoodfacts.org/), projeto do Open Food Facts. Primeiro foram selecionados produtos com ao menos uma observação de preço e nomes compatíveis com o catálogo; depois, 20 produtos brasileiros confundíveis foram adicionados como `NO_MATCH`. Os rótulos foram definidos olhando apenas o nome do produto, sem exibir sugestões do matcher. Os dados derivados do Open Food Facts são redistribuídos sob ODbL, com atribuição e share-alike.

## Uso pretendido

Benchmark educacional de entity matching, retrieval e calibração de abstenção. Não deve decidir compras, estoque ou informação nutricional sem revisão e dados reais do domínio.

## Limitações

O conjunto sintético não reproduz toda a variação de fornecedores reais e usa marcas fictícias. A fatia Open Prices é pequena, foi selecionada por compatibilidade com o catálogo e inclui nomes de produtos observados no Brasil e em Portugal; portanto, não estima a frequência natural dos itens em compras de restaurantes. As categorias e os canônicos são uma taxonomia pequena, criada para este experimento; não constituem uma cópia da TACO nem um catálogo comercial.
