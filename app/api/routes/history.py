"""Endpoints para consulta do histórico de análises de currículos."""

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
    summary="Listar histórico de análises",
    description=(
        "Retorna uma lista paginada de todas as análises realizadas, "
        "ordenadas da mais recente para a mais antiga."
    ),
)
def listar_historico(
    page: int = Query(1, ge=1, description="Número da página (a partir de 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Quantidade de itens por página"),
    db: Session = Depends(get_db),
) -> PaginatedResponse[AnalysisListItem]:
    """Lista o histórico de análises com paginação baseada em número de página.

    Args:
        page: Número da página solicitada (base 1).
        page_size: Quantidade de registros por página (máximo 100).
        db: Sessão ativa do banco de dados (injetada via dependência).

    Returns:
        Resposta paginada contendo os itens, total, página atual e total de páginas.
    """
    repo = AnalysisRepository(db)
    paginated_items, total = repo.list_paginated(page=page, page_size=page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    return PaginatedResponse(
        items=paginated_items,
        total=total,
        page=page,
        page_size=page_size,
        pages=total_pages,
    )


@router.get(
    "/history/{analysis_id}",
    response_model=AnalysisResponse,
    summary="Buscar análise por ID",
    description="Retorna os detalhes completos de uma análise específica pelo seu ID.",
)
def buscar_analise(analysis_id: int, db: Session = Depends(get_db)) -> AnalysisResponse:
    """Recupera uma análise específica pelo seu identificador único.

    Args:
        analysis_id: Identificador único da análise.
        db: Sessão ativa do banco de dados (injetada via dependência).

    Returns:
        Registro completo da análise correspondente ao ID.

    Raises:
        HTTPException 404: Se nenhuma análise com o ID informado for encontrada.
    """
    repo = AnalysisRepository(db)
    saved_record = repo.get_by_id(analysis_id)
    if not saved_record:
        raise HTTPException(status_code=404, detail="Análise não encontrada.")
    return saved_record
