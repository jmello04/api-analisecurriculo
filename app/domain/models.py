from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    level: str
    strong_points: list[str]
    weak_points: list[str]
    suggestions: list[str]
    detected_skills: list[str]


class AnalysisResponse(AnalysisResult):
    id: int
    filename: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    id: int
    filename: str
    score: int
    level: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int
