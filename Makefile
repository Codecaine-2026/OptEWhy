.PHONY: install dev api web test lint format generate-synthetic train-causal

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

install:
	$(PYTHON) -m pip install -e ".[dev]"
	npm install

dev:
	docker compose up --build

api:
	uvicorn api.main:app --reload --app-dir apps/api/src

web:
	npm --workspace apps/web run dev

test:
	pytest
	npm --workspace apps/web run test

lint:
	ruff check .
	npm --workspace apps/web run lint

format:
	ruff format .

generate-synthetic:
	PYTHONPATH=packages/causal-engine/src $(PYTHON) scripts/generate-synthetic-data/generate.py

train-causal:
	PYTHONPATH=packages/causal-engine/src $(PYTHON) scripts/train-causal-weights/train.py
