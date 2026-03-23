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
    summary="Analyze a resume",
    description=(
        "Upload a PDF resume and receive a structured evaluation with score, "
        "career level, strengths, weaknesses, improvement suggestions, and detected skills."
    ),
)
async def analyze_resume(
    file: UploadFile = File(..., description="Resume file in PDF format"),
    db: Session = Depends(get_db),
) -> AnalysisResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_upload_size_mb}MB size limit.",
        )

    try:
        text = pdf_extractor.extract_text(file_bytes)
    except PDFExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    try:
        result = analyzer.analyze(text)
    except AnalysisServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    repo = AnalysisRepository(db)
    record = repo.save(file.filename, text, result)
    logger.info("Resume analyzed: filename=%s score=%d level=%s", file.filename, result.score, result.level)
    return record
