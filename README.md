# Resume Analyzer API

![CI](https://github.com/jmello04/resume-analyzer-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)

API REST para análise automática de currículos em PDF, com pontuação, classificação de nível profissional, detecção de habilidades e feedback estruturado.

---

## Funcionalidades

- Upload de currículo em PDF com extração automática de texto
- Pontuação de 0 a 100 com classificação de nível (Júnior / Pleno / Sênior)
- Identificação de pontos fortes, pontos fracos e sugestões de melhoria
- Detecção de habilidades técnicas e comportamentais
- Histórico de análises com paginação, armazenado em PostgreSQL
- Migrações de banco de dados com Alembic
- Logs estruturados em JSON
- Suporte a CORS
- Pipeline de CI/CD com GitHub Actions

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Framework | FastAPI |
| Banco de dados | PostgreSQL + SQLAlchemy |
| Migrações | Alembic |
| Extração de PDF | pdfplumber |
| Validação | Pydantic v2 |
| Containerização | Docker + Docker Compose |
| Linting | Ruff |
| Testes | pytest |

---

## Requisitos

- Docker e Docker Compose instalados
- Chave de API da Anthropic

---

## Início Rápido

```bash
git clone https://github.com/jmello04/resume-analyzer-api.git
cd resume-analyzer-api

cp .env.example .env
```

Edite o arquivo `.env` e preencha o campo `ANTHROPIC_API_KEY` com sua chave.

```bash
docker-compose up --build
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa: `http://localhost:8000/docs`

---

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/analyze` | Envia um currículo PDF para análise |
| `GET` | `/history` | Lista o histórico de análises (paginado) |
| `GET` | `/history/{id}` | Retorna uma análise específica por ID |
| `GET` | `/health` | Verificação de saúde da API |

### POST /analyze

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@curriculo.pdf"
```

**Resposta:**

```json
{
  "id": 1,
  "filename": "curriculo.pdf",
  "score": 78,
  "level": "Pleno",
  "strong_points": ["Experiência sólida com Python", "Portfólio relevante"],
  "weak_points": ["Sem certificações em nuvem"],
  "suggestions": ["Obter certificação AWS ou GCP"],
  "detected_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "created_at": "2024-01-01T00:00:00"
}
```

### GET /history

Suporte à paginação via query params:

```bash
curl "http://localhost:8000/history?page=1&page_size=20"
```

**Resposta:**

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

---

## Desenvolvimento

```bash
pip install -r requirements.txt

make test      # Executa os testes
make lint      # Verifica o código
make format    # Formata o código
make migrate   # Aplica as migrações
make up        # Sobe com Docker
```

---

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `ANTHROPIC_API_KEY` | Chave da API (obrigatório) | — |
| `DATABASE_URL` | URL de conexão do PostgreSQL | `postgresql://postgres:postgres@localhost:5432/resume_analyzer` |
| `ANALYSIS_MODEL` | Modelo utilizado para análise | `claude-opus-4-6` |
| `LOG_LEVEL` | Nível de log | `INFO` |
| `MAX_UPLOAD_SIZE_MB` | Tamanho máximo do PDF em MB | `10` |

---

## Estrutura do Projeto

```
resume-analyzer-api/
├── .github/
│   └── workflows/
│       └── ci.yml                  # Pipeline CI (lint + testes)
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py   # Migração inicial
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── analyze.py          # POST /analyze
│   │       └── history.py          # GET /history, GET /history/{id}
│   ├── core/
│   │   ├── config.py               # Configurações da aplicação
│   │   ├── exceptions.py           # Exceções de domínio
│   │   └── logging_config.py       # Log estruturado em JSON
│   ├── domain/
│   │   └── models.py               # Schemas Pydantic
│   ├── infra/
│   │   └── database/
│   │       ├── connection.py       # Engine SQLAlchemy e modelo ORM
│   │       └── repositories.py     # Camada de acesso a dados
│   ├── services/
│   │   ├── analyzer.py             # Serviço de análise de currículo
│   │   └── pdf_extractor.py        # Extração de texto do PDF
│   └── main.py                     # Aplicação FastAPI
├── tests/
│   ├── conftest.py
│   └── test_analyze.py
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── requirements.txt
```

---

## Testes

Os testes utilizam SQLite em memória e mocks dos serviços externos. Não é necessário PostgreSQL nem chave de API válida para executá-los.

```bash
pytest tests/ -v
```

---

## Licença

MIT
