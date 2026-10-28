.PHONY: setup data test eval train app lint

setup:
	python -m pip install -e '.[dev,app,publish]'

data:
	python -m ingredient_matcher.data

test:
	pytest -q

eval:
	python -m ingredient_matcher.evaluate --methods fuzzy,e5,fine_tuned

train:
	python -m ingredient_matcher.train

app:
	python app.py

lint:
	ruff check .
