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
    logger.info("Starting Resume Analyzer API")
    create_tables()
    yield
    logger.info("Resume Analyzer API stopped")


app = FastAPI(
    title="Resume Analyzer API",
    description="API for resume analysis with scoring, skill detection, and structured feedback.",
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
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "%s %s %d %.1fms [%s]",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response


app.include_router(analyze.router, tags=["Analysis"])
app.include_router(history.router, tags=["History"])


@app.get("/health", tags=["Health"], summary="Health check")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
