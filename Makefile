.PHONY: run install install-dev lint fix test migrate migrate-down migrate-create cli

install:
	uv sync

install-dev:
	uv sync --dev

lint:
	uv run ruff check .

fix:
	uv run ruff check . --fix

test: install-dev
	uv run pytest

coverage: install-dev
	uv run pytest --cov=api api/tests

run:
	uv run uvicorn api.app.main:app --reload

cli:
	uv run textual run cli.app:main --dev

migrate:
	uv run alembic upgrade head

migrate-down:
	uv run alembic downgrade -1

migrate-create:
	uv run alembic revision --autogenerate -m "$(message)"


