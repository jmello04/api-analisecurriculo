# Resume Analyzer API

![CI](https://github.com/jmello04/resume-analyzer-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)

REST API for resume analysis with automatic scoring, skill detection, and structured feedback.

## Features

- PDF upload and text extraction via `pdfplumber`
- Automated scoring (0–100) and career level classification (Júnior / Pleno / Sênior)
- Strengths, weaknesses, improvement suggestions, and detected skills
- Paginated analysis history stored in PostgreSQL
- Database migrations with Alembic
- Structured JSON logging
- CORS support
- CI/CD pipeline with GitHub Actions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy |
| Migrations | Alembic |
| PDF Extraction | pdfplumber |
| Validation | Pydantic v2 |
| Containerization | Docker + Docker Compose |
| Linting | Ruff |
| Testing | pytest |

## Requirements

- Docker and Docker Compose
- Anthropic API Key

## Quick Start

```bash
git clone https://github.com/jmello04/resume-analyzer-api.git
cd resume-analyzer-api

cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY

docker-compose up --build
```

The API will be available at `http://localhost:8000`.

Interactive documentation: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/analyze` | Upload and analyze a PDF resume |
| `GET` | `/history` | List previous analyses (paginated) |
| `GET` | `/history/{id}` | Get a specific analysis by ID |
| `GET` | `/health` | Health check |

### POST /analyze

```bash
curl -X POST http://localhost:8000/analyze \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "id": 1,
  "filename": "resume.pdf",
  "score": 78,
  "level": "Pleno",
  "strong_points": ["Strong Python background", "Relevant project experience"],
  "weak_points": ["No cloud certifications"],
  "suggestions": ["Obtain AWS or GCP certification"],
  "detected_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
  "created_at": "2024-01-01T00:00:00"
}
```

### GET /history

Supports pagination via query parameters:

```bash
curl "http://localhost:8000/history?page=1&page_size=20"
```

**Response:**
```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "pages": 3
}
```

### GET /history/{id}

```bash
curl http://localhost:8000/history/1
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
make test

# Lint code
make lint

# Format code
make format

# Apply database migrations
make migrate

# Start with Docker
make up
```

## Environment Variables

| Variable | Description | Default |
|----------|-----------|---------|
| `ANTHROPIC_API_KEY` | API key (required) | — |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/resume_analyzer` |
| `ANALYSIS_MODEL` | Model identifier | `claude-opus-4-6` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `MAX_UPLOAD_SIZE_MB` | Maximum PDF upload size in MB | `10` |

## Project Structure

```
resume-analyzer-api/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI pipeline (lint + test)
├── alembic/
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── analyze.py      # POST /analyze
│   │       └── history.py      # GET /history, GET /history/{id}
│   ├── core/
│   │   ├── config.py           # Application settings
│   │   ├── exceptions.py       # Domain exceptions
│   │   └── logging_config.py   # Structured JSON logging
│   ├── domain/
│   │   └── models.py           # Pydantic schemas
│   ├── infra/
│   │   └── database/
│   │       ├── connection.py   # SQLAlchemy engine and ORM model
│   │       └── repositories.py # Data access layer
│   ├── services/
│   │   ├── analyzer.py         # Resume analysis service
│   │   └── pdf_extractor.py    # PDF text extraction
│   └── main.py                 # FastAPI application
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

## Running Tests

Tests use an in-memory SQLite database and mock external services — no PostgreSQL or API key required.

```bash
pytest tests/ -v
```
