.PHONY: help up down build test coverage lint format migrate shell

help:
	@echo "Comandos disponíveis:"
	@echo "  up        - Sobe todos os serviços com Docker Compose"
	@echo "  down      - Para todos os serviços"
	@echo "  build     - Reconstrói as imagens Docker"
	@echo "  test      - Executa os testes"
	@echo "  coverage  - Executa os testes com relatório de cobertura"
	@echo "  lint      - Verifica o código com ruff"
	@echo "  format    - Formata o código com ruff"
	@echo "  migrate   - Aplica as migrações do banco de dados"
	@echo "  shell     - Abre um shell no container da API"

up:
	docker-compose up --build

down:
	docker-compose down

build:
	docker-compose build

test:
	pytest tests/ -v --tb=short

coverage:
	pytest tests/ --cov=app --cov-report=term-missing --cov-report=html

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/

migrate:
	alembic upgrade head

shell:
	docker-compose exec api bash
