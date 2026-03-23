
from sqlalchemy.orm import Session

from app.domain.models import AnalysisResult
from app.infra.database.connection import ResumeAnalysisORM


class AnalysisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, filename: str, raw_text: str, result: AnalysisResult) -> ResumeAnalysisORM:
        record = ResumeAnalysisORM(
            filename=filename,
            raw_text=raw_text,
            score=result.score,
            level=result.level,
            strong_points=result.strong_points,
            weak_points=result.weak_points,
            suggestions=result.suggestions,
            detected_skills=result.detected_skills,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_paginated(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[ResumeAnalysisORM], int]:
        total = self.db.query(ResumeAnalysisORM).count()
        offset = (page - 1) * page_size
        items = (
            self.db.query(ResumeAnalysisORM)
            .order_by(ResumeAnalysisORM.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_by_id(self, analysis_id: int) -> ResumeAnalysisORM | None:
        return (
            self.db.query(ResumeAnalysisORM)
            .filter(ResumeAnalysisORM.id == analysis_id)
            .first()
        )
