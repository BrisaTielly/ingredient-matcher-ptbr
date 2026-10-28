# Ingredient Matcher PT-BR - Design

## Objetivo

Publicar uma evidência técnica pequena e defensável para a candidatura ao iFood GEN AI: um dataset aberto de nomes ruidosos de ingredientes em português, três abordagens comparáveis e um modelo fine-tuned disponível no Hugging Face com demo.

## Escopo aprovado

- 100 a 150 ingredientes canônicos de uso comum em food service.
- 250 a 350 variantes ruidosas geradas por regras versionadas.
- Splits por grupo de origem para impedir que variantes equivalentes vazem entre treino e teste.
- Conjunto de teste revisável manualmente, com 60 a 80 exemplos.
- Métodos: RapidFuzz, `intfloat/multilingual-e5-small` e uma versão fine-tuned do E5.
- Métricas: top-1 accuracy, recall@5, precision, recall, F1 e coverage com abstenção.
- Dataset, modelo e Space no Hugging Face; repositório público no GitHub.
- README com números gerados por código, análise de erros e limitações.

## Alternativas consideradas

1. **Matcher pequeno e completo (escolhido).** Maximiza a qualidade dos artefatos públicos dentro de 48 horas.
2. **Matcher com LLM e arquitetura híbrida.** Mostraria mais GenAI, mas adicionaria custo e avaliação não determinística sem melhorar o sinal principal de ML.
3. **Dataset grande com Open Food Facts.** Seria mais realista, mas exigiria limpeza, revisão e tratamento de licença incompatíveis com o prazo.

## Arquitetura

`data/canonicals.csv` contém o catálogo canônico. Um gerador determinístico cria variantes com abreviações, remoção de acentos, unidades, marcas fictícias e truncamento. Cada exemplo mantém `source_group`, transformação e split para auditoria.

O pipeline de avaliação usa a mesma normalização e interface para todos os métodos. O limiar de abstenção é escolhido somente na validação; o teste é avaliado uma vez com a configuração congelada. Resultados e previsões são gravados em JSON e Markdown.

O fine-tuning usa pares `nome_ruidoso -> nome_canonico` e treinamento contrastivo. A demo carrega o modelo publicado ou um modelo local, retorna top-5 candidatos e mostra a decisão `match` ou `revisar`.

## Integridade da avaliação

- Seed fixa e geração reproduzível.
- Variantes do mesmo canônico e padrão de origem permanecem no mesmo split.
- Nenhum ajuste é feito usando o teste.
- O README consome números de `results/metrics.json`.
- O dataset card declara que os dados são sintéticos e descreve suas limitações.
- Métricas comparativas só serão publicadas quando calculadas pelo mesmo avaliador e conjunto de teste.

## Critério de pronto

O projeto está pronto para entrar no currículo quando o repositório executar testes e avaliação localmente, houver métricas reais salvas, dataset e modelo estiverem publicados, o Space responder a uma consulta e os links estiverem no PDF final.
