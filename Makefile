.PHONY: help up down build test lint format migrate shell

help:
	@echo "Available commands:"
	@echo "  up        - Start all services with Docker Compose"
	@echo "  down      - Stop all services"
	@echo "  build     - Rebuild Docker images"
	@echo "  test      - Run the test suite"
	@echo "  lint      - Run the linter (ruff)"
	@echo "  format    - Auto-format code (ruff format)"
	@echo "  migrate   - Apply pending database migrations"
	@echo "  shell     - Open a shell inside the API container"

up:
	docker-compose up --build

down:
	docker-compose down

build:
	docker-compose build

test:
	pytest tests/ -v --tb=short

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/

migrate:
	alembic upgrade head

shell:
	docker-compose exec api bash
