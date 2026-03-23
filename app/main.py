import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analyze, history
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.infra.database.connection import create_tables

setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Resume Analyzer API")
    create_tables()
    yield
    logger.info("Resume Analyzer API encerrada")


app = FastAPI(
    title="Resume Analyzer API",
    description="API para análise de currículos com pontuação, detecção de habilidades e feedback estruturado.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def middleware_log_requisicoes(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    inicio = time.perf_counter()
    response = await call_next(request)
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    logger.info(
        "%s %s %d %.1fms [%s]",
        request.method,
        request.url.path,
        response.status_code,
        duracao_ms,
        request_id,
    )
    return response


app.include_router(analyze.router, tags=["Análise"])
app.include_router(history.router, tags=["Histórico"])


@app.get("/health", tags=["Status"], summary="Verificação de saúde da API")
def health_check():
    return {"status": "ok", "versao": "1.0.0"}
