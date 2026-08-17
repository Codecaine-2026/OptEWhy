.PHONY: install dev api web test lint format

install:
	python -m pip install -e ".[dev]"
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

