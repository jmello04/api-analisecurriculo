import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.domain.models import AnalysisListItem, AnalysisResponse, PaginatedResponse
from app.infra.database.connection import get_db
from app.infra.database.repositories import AnalysisRepository

router = APIRouter()


@router.get(
    "/history",
    response_model=PaginatedResponse[AnalysisListItem],
    summary="List analysis history",
    description="Returns a paginated list of all previous resume analyses, ordered by most recent first.",
)
def list_history(
    page: int = Query(1, ge=1, description="Page number (starting at 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AnalysisListItem]:
    repo = AnalysisRepository(db)
    items, total = repo.list_paginated(page=page, page_size=page_size)
    pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.get(
    "/history/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Get a specific analysis",
    description="Returns the full details of a resume analysis by its ID.",
)
def get_analysis(analysis_id: int, db: Session = Depends(get_db)) -> AnalysisResponse:
    repo = AnalysisRepository(db)
    record = repo.get_by_id(analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return record
