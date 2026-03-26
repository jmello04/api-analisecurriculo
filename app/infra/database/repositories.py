"""Repositório de acesso a dados para análises de currículos."""

from sqlalchemy.orm import Session

from app.domain.models import AnalysisResult
from app.infra.database.connection import ResumeAnalysisORM


class AnalysisRepository:
    """Repositório SQLAlchemy para persistência e consulta de análises de currículos.

    Args:
        db: Sessão ativa do banco de dados fornecida via injeção de dependência.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def save(
        self, filename: str, raw_text: str, analysis_result: AnalysisResult
    ) -> ResumeAnalysisORM:
        """Persiste uma nova análise de currículo no banco de dados.

        Args:
            filename: Nome original do arquivo PDF enviado.
            raw_text: Texto bruto extraído do currículo.
            analysis_result: Resultado estruturado da análise com todos os campos avaliados.

        Returns:
            O registro ORM recém-criado e atualizado com o ID gerado.
        """
        new_record = ResumeAnalysisORM(
            filename=filename,
            raw_text=raw_text,
            score=analysis_result.score,
            level=analysis_result.level,
            strong_points=analysis_result.strong_points,
            weak_points=analysis_result.weak_points,
            suggestions=analysis_result.suggestions,
            detected_skills=analysis_result.detected_skills,
        )
        self.db.add(new_record)
        self.db.commit()
        self.db.refresh(new_record)
        return new_record

    def list_paginated(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[ResumeAnalysisORM], int]:
        """Recupera registros de análise com paginação baseada em número de página.

        Args:
            page: Número da página solicitada (base 1).
            page_size: Quantidade de registros por página.

        Returns:
            Tupla com a lista de registros da página solicitada e o total absoluto.
        """
        total = self.db.query(ResumeAnalysisORM).count()
        offset = (page - 1) * page_size
        paginated_records = (
            self.db.query(ResumeAnalysisORM)
            .order_by(ResumeAnalysisORM.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return paginated_records, total

    def get_by_id(self, analysis_id: int) -> ResumeAnalysisORM | None:
        """Busca um registro de análise pelo seu identificador único.

        Args:
            analysis_id: ID do registro a ser buscado.

        Returns:
            O registro correspondente, ou None se não encontrado.
        """
        return (
            self.db.query(ResumeAnalysisORM)
            .filter(ResumeAnalysisORM.id == analysis_id)
            .first()
        )
