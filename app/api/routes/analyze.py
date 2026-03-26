"""Endpoint para análise de currículos em PDF."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AnalysisServiceError, PDFExtractionError
from app.domain.models import AnalysisResponse
from app.infra.database.connection import get_db
from app.infra.database.repositories import AnalysisRepository
from app.services.analyzer import ResumeAnalyzerService
from app.services.pdf_extractor import PDFExtractorService

logger = logging.getLogger(__name__)
router = APIRouter()

pdf_extractor = PDFExtractorService()
analyzer = ResumeAnalyzerService()


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    status_code=201,
    summary="Analisar currículo",
    description=(
        "Envie um currículo em PDF e receba uma avaliação estruturada com pontuação, "
        "nível de carreira, pontos fortes, pontos fracos, "
        "sugestões de melhoria e habilidades detectadas."
    ),
)
async def analisar_curriculo(
    file: UploadFile = File(..., description="Arquivo do currículo em formato PDF"),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    """Recebe um currículo em PDF, executa a análise e persiste o resultado.

    Args:
        file: Arquivo PDF enviado via multipart/form-data.
        db: Sessão ativa do banco de dados (injetada via dependência).

    Returns:
        Registro de análise recém-criado com score, level, pontos e habilidades.

    Raises:
        HTTPException 400: Arquivo sem extensão .pdf ou vazio.
        HTTPException 413: Arquivo excede o limite configurado em MAX_UPLOAD_SIZE_MB.
        HTTPException 422: Falha na extração de texto do PDF.
        HTTPException 502: Serviço de análise indisponível ou com erro.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

    pdf_bytes = await file.read()

    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(pdf_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"O arquivo excede o limite de {settings.max_upload_size_mb}MB.",
        )

    try:
        resume_text = pdf_extractor.extract_text(pdf_bytes)
    except PDFExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    try:
        analysis_result = analyzer.analyze(resume_text)
    except AnalysisServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    repo = AnalysisRepository(db)
    saved_record = repo.save(file.filename, resume_text, analysis_result)
    logger.info(
        "Currículo analisado: arquivo=%s pontuacao=%d nivel=%s",
        file.filename,
        analysis_result.score,
        analysis_result.level,
    )
    return saved_record
