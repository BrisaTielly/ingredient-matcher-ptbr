# Ingredient Matcher PT-BR

Entity matching de descrições ruidosas de compras e notas fiscais para um catálogo de ingredientes em português.

[Demo](https://huggingface.co/spaces/BrisaTielly/ingredient-matcher-ptbr) · [Modelo](https://huggingface.co/BrisaTielly/ingredient-matcher-ptbr-model) · [Dataset](https://huggingface.co/datasets/BrisaTielly/ingredient-matcher-ptbr)

`QJ MUSS FAT PCT 1KG` → `queijo_mussarela`

## Por que

Restaurantes recebem o mesmo insumo com abreviações, marcas, unidades e descrições diferentes. Sem resolver essas identidades, custos, estoque e informação nutricional ficam fragmentados. Este projeto compara uma regra lexical, um retriever multilíngue pronto e o mesmo retriever após fine-tuning.

## Resultados

Os resultados abaixo são gerados por `make eval`. O limiar de abstenção é calibrado somente na validação; o teste contém ingredientes que não aparecem no fine-tuning.

<!-- RESULTS_START -->
| Método | F1 (IC 95%) | Precisão | Recall | Top-1 | Recall@5 | `NO_MATCH` | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| RapidFuzz | 0,900 [0,826; 0,959] | 0,900 | 0,900 | 0,933 | 1,000 | 0,667 | 0,909 |
| E5 base | 0,891 [0,821; 0,950] | 0,898 | 0,883 | 0,933 | 1,000 | 0,500 | 0,894 |
| **E5 fine-tuned** | **0,975 [0,932; 1,000]** | **0,983** | **0,967** | **0,983** | **1,000** | **1,000** | **0,894** |

O fine-tuning aumentou a estimativa pontual de F1 em 0,084 sobre o E5 base, mantendo todos os canônicos corretos no top-5. Os intervalos bootstrap se sobrepõem: com 66 exemplos de teste, a evidência ainda não sustenta uma conclusão forte de superioridade. A estratificação preserva 60 matches e 6 itens fora do catálogo em 2.000 reamostragens.
<!-- RESULTS_END -->

## Dataset

- 100 ingredientes canônicos.
- 300 descrições positivas geradas por regras versionadas.
- 30 itens fora do catálogo (`NO_MATCH`).
- 66 exemplos no teste, separados por ingrediente.
- Marcas fictícias e nenhum dado privado ou corporativo.

O teste é pequeno e sintético. Ele mede robustez controlada a abreviações e ruído, não desempenho de produção.

### Fatia externa em revisão

`scripts/fetch_open_prices.py` prepara uma fila com as descrições brasileiras únicas disponíveis na API do Open Prices/Open Food Facts, com sugestões automáticas separadas do rótulo final. Essa fatia só entra no benchmark depois que todas as linhas forem revisadas por uma pessoa e passarem em `scripts/validate_real_labels.py`.

Depois da revisão, `scripts/evaluate_llm.py` compara duas estratégias: LLM direto sobre os 100 canônicos e E5 top-5 com LLM para reordenar. A saída registra tokens, latência, custo total e custo por mil itens. Ainda não há números publicados para esses métodos porque a fatia real não foi rotulada e nenhuma chamada paga foi executada.

## Métodos

1. **RapidFuzz:** `WRatio` após normalização compartilhada.
2. **E5 base:** `intfloat/multilingual-e5-small`, similaridade de cosseno.
3. **E5 fine-tuned:** treinamento contrastivo com `MultipleNegativesRankingLoss`.

Todos recuperam top-5 no mesmo catálogo. O score top-1 precisa superar um limiar calibrado na validação; caso contrário, a resposta é `revisar`.

## Demo

O Space gratuito executa uma busca lexical no navegador para demonstrar o fluxo de match e abstenção. O E5 fine-tuned está publicado separadamente no Hub; seu resultado vem do benchmark reproduzível deste repositório. A aplicação Gradio completa continua disponível localmente com `make app`.

## Reproduzir

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,app,publish]'
make data
make test
make train
make eval
make app
```

O CI reavalia RapidFuzz e o E5 publicado em uma pasta isolada. `scripts/check_regression.py` compara F1 e top-1 com `results/metrics.json` e quebra o build quando a queda passa de 0,01.

## Avaliação

- `retrieval_top1_accuracy`: canônico correto na primeira posição, antes da abstenção.
- `recall_at_5`: canônico correto entre os cinco primeiros.
- `precision`, `recall` e `f1`: qualidade das decisões automatizadas sob o limiar.
- `coverage`: fração aceita automaticamente.
- `no_match_accuracy`: itens fora do catálogo corretamente enviados para revisão.

Artefatos reproduzíveis ficam em `results/metrics.json`, `results/predictions.csv` e `results/report.md`.

## Análise de erro

O único erro de retrieval do modelo fine-tuned foi `MACA PARA 2,5KG`. A descrição é uma truncagem sintética agressiva de “macarrão parafuso” e foi associada a `maca`. O canônico correto apareceu no top-5, por isso o recall@5 permaneceu em 1,000. Esse caso mostra que truncar palavras sem preservar tokens inteiros cria ambiguidades que nem o contexto curto nem a similaridade resolvem de forma confiável.

No próximo ciclo, esse padrão deve virar uma fatia própria de avaliação. A correção não deve ser simplesmente adicionar o exemplo ao treino: primeiro é necessário representar truncagens reais de fornecedores e medir a taxa de ambiguidade com rótulos humanos.

## Limitações

O dataset positivo é sintético, pequeno e cobre apenas 100 ingredientes. O fine-tuning aprende padrões de ruído controlados e precisa ser reavaliado com descrições reais antes de uso operacional. O conjunto `NO_MATCH` também é pequeno; por isso, o limiar publicado serve como demonstração, não como política de automação em produção.
