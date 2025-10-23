.PHONY: help install install-hooks sync test test-cov lint format check type-check pre-commit up down restart logs build clean

help:
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make install-hooks - Install pre-commit hooks"
	@echo "  make sync          - Sync dependencies"
	@echo "  make test          - Run tests"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code"
	@echo "  make check         - Run all checks (format, lint, type-check)"
	@echo "  make type-check    - Run type checking"
	@echo "  make pre-commit    - Run pre-commit hooks"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make build         - Build Docker images"
	@echo "  make logs          - Show logs from all services"
	@echo "  make clean         - Clean up generated files"

install:
	uv sync --all-packages

install-hooks:
	uv run pre-commit install

sync:
	uv sync --all-packages

test:
	uv run pytest

test-cov:
	uv run pytest --cov=. --cov-report=html --cov-report=term-missing

lint:
	uv run ruff check .
	uv run flake8 .

format:
	uv run ruff format .
	uv run ruff check . --fix

type-check:
	uv run pyright

check: format lint type-check
	@echo "All checks passed!"

pre-commit:
	uv run pre-commit run --all-files

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

build:
	docker compose up -d --build

logs:
	docker compose logs -f

logs-task-1:
	docker compose logs -f task-1

logs-task-2:
	docker compose logs -f task-2

logs-task-3:
	docker compose logs -f task-3

logs-task-4:
	docker compose logs -f task-4

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
