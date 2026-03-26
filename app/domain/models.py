"""Modelos Pydantic para validação de entrada, saída e paginação da API."""

from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    """Resultado estruturado retornado pelo serviço de análise semântica.

    Attributes:
        score: Pontuação geral do currículo de 0 a 100.
        level: Nível profissional classificado (Júnior, Pleno ou Sênior).
        strong_points: Lista de pontos fortes identificados no currículo.
        weak_points: Lista de pontos fracos identificados no currículo.
        suggestions: Lista de sugestões concretas de melhoria.
        detected_skills: Lista de habilidades técnicas e comportamentais detectadas.
    """

    score: int = Field(..., ge=0, le=100)
    level: str
    strong_points: list[str]
    weak_points: list[str]
    suggestions: list[str]
    detected_skills: list[str]


class AnalysisResponse(AnalysisResult):
    """Resposta completa de uma análise persistida, incluindo metadados do registro.

    Attributes:
        id: Identificador único do registro no banco de dados.
        filename: Nome original do arquivo PDF enviado para análise.
        created_at: Data e hora em que a análise foi realizada.
    """

    id: int
    filename: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    """Item resumido de análise utilizado na listagem paginada do histórico.

    Attributes:
        id: Identificador único do registro.
        filename: Nome do arquivo analisado.
        score: Pontuação geral atribuída ao currículo.
        level: Nível profissional classificado.
        created_at: Data e hora de criação do registro.
    """

    id: int
    filename: str
    score: int
    level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedResponse[T](BaseModel):
    """Resposta paginada genérica utilizada nos endpoints de listagem.

    Attributes:
        items: Lista de itens da página solicitada.
        total: Total absoluto de registros disponíveis.
        page: Número da página atual.
        page_size: Quantidade de itens por página.
        pages: Total de páginas disponíveis.
    """

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int
