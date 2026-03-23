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
        "nível de carreira, pontos fortes, pontos fracos, sugestões de melhoria e habilidades detectadas."
    ),
)
async def analisar_curriculo(
    file: UploadFile = File(..., description="Arquivo do currículo em formato PDF"),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"O arquivo excede o limite de {settings.max_upload_size_mb}MB.",
        )

    try:
        texto = pdf_extractor.extract_text(file_bytes)
    except PDFExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    try:
        resultado = analyzer.analyze(texto)
    except AnalysisServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    repo = AnalysisRepository(db)
    registro = repo.save(file.filename, texto, resultado)
    logger.info("Currículo analisado: arquivo=%s pontuacao=%d nivel=%s", file.filename, resultado.score, resultado.level)
    return registro
