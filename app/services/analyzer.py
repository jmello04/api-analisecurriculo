import json
import logging
import re

from anthropic import Anthropic, APIError

from app.core.config import settings
from app.core.exceptions import AnalysisServiceError
from app.domain.models import AnalysisResult

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = """Analise o currículo abaixo e retorne uma avaliação estruturada como objeto JSON.

O JSON deve conter exatamente estes campos:
- "score": inteiro entre 0 e 100 representando a qualidade geral do currículo
- "level": um dos valores "Júnior", "Pleno" ou "Sênior"
- "strong_points": lista de strings com os pontos fortes identificados
- "weak_points": lista de strings com os pontos fracos identificados
- "suggestions": lista de strings com sugestões concretas de melhoria
- "detected_skills": lista de habilidades técnicas e comportamentais encontradas no currículo

Conteúdo do currículo:
{resume_text}

Retorne apenas JSON válido. Não inclua markdown, blocos de código ou qualquer texto fora do objeto JSON."""


class ResumeAnalyzerService:
    def __init__(self) -> None:
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def analyze(self, resume_text: str) -> AnalysisResult:
        try:
            message = self.client.messages.create(
                model=settings.analysis_model,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": _PROMPT_TEMPLATE.format(resume_text=resume_text),
                    }
                ],
            )
        except APIError as exc:
            logger.error("Erro no servico de analise: %s", exc)
            raise AnalysisServiceError("O serviço de análise está indisponível no momento.") from exc
        except Exception as exc:
            logger.error("Erro inesperado durante a analise: %s", exc)
            raise AnalysisServiceError("Erro inesperado durante a análise do currículo.") from exc

        raw = message.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        try:
            data = json.loads(raw)
            return AnalysisResult(**data)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error("Falha ao interpretar resposta da analise: %s", exc)
            raise AnalysisServiceError("Não foi possível interpretar o resultado da análise.") from exc
