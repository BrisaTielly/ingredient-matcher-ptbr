.PHONY: setup data test eval regression train app lint

setup:
	python -m pip install -e '.[dev,app,publish]'

data:
	python -m ingredient_matcher.data

test:
	pytest -q

eval:
	python -m ingredient_matcher.evaluate --methods fuzzy,e5,fine_tuned

regression:
	python scripts/check_regression.py --baseline results/metrics.json --candidate .ci-results/metrics.json --method RapidFuzz --method 'E5 fine-tuned'

train:
	python -m ingredient_matcher.train

app:
	python app.py

lint:
	ruff check .
