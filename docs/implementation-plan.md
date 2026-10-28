# Ingredient Matcher PT-BR Implementation Plan

> **For the agent:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Construir e publicar um matcher reproduzível de nomes ruidosos de ingredientes em português, acompanhado de dataset, modelo fine-tuned, métricas, demo e currículo atualizado.

**Architecture:** Um pacote Python gera dados sintéticos auditáveis, executa três matchers sob a mesma interface e produz os artefatos de avaliação. O modelo fine-tuned e a aplicação Gradio reutilizam o pipeline de inferência para evitar divergência entre demo e benchmark.

**Tech Stack:** Python 3.12, pandas, RapidFuzz, sentence-transformers, Hugging Face Hub/Datasets, Gradio, pytest, GitHub Actions e HTML/LibreOffice para o currículo.

---

### Task 1: Estrutura e geração de dados

**Files:**
- Create: `pyproject.toml`
- Create: `src/ingredient_matcher/data.py`
- Create: `src/ingredient_matcher/normalize.py`
- Create: `data/canonicals.csv`
- Test: `tests/test_data.py`
- Test: `tests/test_normalize.py`

**Steps:**
1. Escrever testes para normalização, geração determinística, esquema e isolamento dos splits.
2. Executar `pytest` e confirmar a falha inicial.
3. Implementar normalização e geração mínima.
4. Executar `python -m ingredient_matcher.data` e confirmar 250 a 350 exemplos e 60 a 80 casos de teste.
5. Executar os testes e confirmar aprovação.

### Task 2: Baselines e avaliação

**Files:**
- Create: `src/ingredient_matcher/matchers.py`
- Create: `src/ingredient_matcher/evaluate.py`
- Test: `tests/test_evaluate.py`

**Steps:**
1. Escrever testes das métricas, top-k e abstenção.
2. Confirmar a falha inicial.
3. Implementar RapidFuzz e E5 sob uma interface comum.
4. Calibrar o limiar na validação e congelá-lo para o teste.
5. Gerar `results/metrics.json`, `results/predictions.csv` e `results/report.md`.

### Task 3: Fine-tuning

**Files:**
- Create: `src/ingredient_matcher/train.py`
- Create: `model_card.md`
- Test: `tests/test_training_data.py`

**Steps:**
1. Validar os pares e garantir que teste não entra no treino.
2. Treinar o modelo pequeno com seed fixa e registrar hiperparâmetros.
3. Avaliar o modelo na mesma suíte dos baselines.
4. Manter o modelo somente se o artefato carregar e reproduzir as previsões.

### Task 4: Demo, documentação e automação

**Files:**
- Create: `app.py`
- Create: `README.md`
- Create: `dataset_card.md`
- Create: `Makefile`
- Create: `.github/workflows/ci.yml`
- Create: `.gitignore`
- Create: `LICENSE`

**Steps:**
1. Implementar o Space com top-5, score e decisão.
2. Documentar instalação, reprodução, resultados, erros e limitações.
3. Configurar CI para testes e avaliação fuzzy sem downloads grandes.
4. Executar testes, avaliação e smoke test da aplicação.

### Task 5: Publicação

**Steps:**
1. Inicializar Git e criar commits pequenos por componente.
2. Publicar o repositório no GitHub.
3. Publicar dataset e modelo no Hugging Face com seus cards.
4. Publicar o Space e verificar uma consulta real.
5. Registrar URLs definitivas no README.

### Task 6: Currículo

**Files:**
- Create: `resume/curriculo_ifood_genai.html`
- Create: `output/pdf/curriculo_ifood_genai.pdf`

**Steps:**
1. Reduzir a experiência atual aos resultados mais fortes.
2. Remover métricas de linhas de código e nomes internos pouco claros.
3. Inserir o matcher com links e métricas produzidas pelo projeto.
4. Gerar o PDF, extrair o texto e renderizar a página.
5. Confirmar uma página, links, ausência de cortes e legibilidade.

### Task 7: Verificação final

**Steps:**
1. Rodar toda a suíte de testes em ambiente limpo.
2. Reexecutar a geração de dados e avaliação.
3. Verificar que números do README e do currículo batem com `results/metrics.json`.
4. Confirmar que todas as URLs públicas respondem.
5. Entregar o repositório e o PDF final.
