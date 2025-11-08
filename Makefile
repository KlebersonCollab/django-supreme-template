.PHONY: help install dev test lint format type-check clean migrate runserver shell superuser collectstatic

help: ## Show this help message
	@echo "Django Template - Available Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: ## Install development dependencies
	uv sync --extra dev

test: ## Run tests with coverage
	uv run pytest tests/ --cov=config --cov-report=term-missing --cov-report=html

test-watch: ## Run tests in watch mode
	uv run pytest tests/ --watch

lint: ## Run linter
	uv run ruff check .

format: ## Format code
	uv run ruff format .

type-check: ## Run type checker
	uv run mypy .

quality: lint format type-check test ## Run all quality checks

migrate: ## Run database migrations
	uv run python manage.py migrate

makemigrations: ## Create database migrations
	uv run python manage.py makemigrations

runserver: ## Run development server
	uv run python manage.py runserver

shell: ## Open Django shell
	uv run python manage.py shell

superuser: ## Create superuser
	uv run python manage.py createsuperuser

collectstatic: ## Collect static files
	uv run python manage.py collectstatic --noinput

check: ## Run Django system check
	uv run python manage.py check

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-shell: ## Open shell in Docker container
	docker-compose exec web bash

clean: ## Clean temporary files
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

