"""Módulo responsável pela análise estruturada de currículos em texto."""

import json
import logging
import re

from anthropic import Anthropic, APIConnectionError, APIStatusError, RateLimitError

from app.core.config import settings
from app.core.exceptions import AnalysisServiceError
from app.domain.models import AnalysisResult

logger = logging.getLogger(__name__)

_PROMPT_PREFIX = """Analise o currículo abaixo e retorne uma avaliação estruturada como objeto JSON.

O JSON deve conter exatamente estes campos:
- "score": inteiro entre 0 e 100 representando a qualidade geral do currículo
- "level": um dos valores "Júnior", "Pleno" ou "Sênior"
- "strong_points": lista de strings com os pontos fortes identificados
- "weak_points": lista de strings com os pontos fracos identificados
- "suggestions": lista de strings com sugestões concretas de melhoria
- "detected_skills": lista de habilidades técnicas e comportamentais encontradas no currículo

Conteúdo do currículo:
"""

_PROMPT_SUFFIX = (
    "\n\nRetorne apenas JSON válido. "
    "Não inclua markdown, blocos de código ou qualquer texto fora do objeto JSON."
)


def _build_analysis_prompt(resume_text: str) -> str:
    """Constrói o prompt completo para análise do currículo.

    Args:
        resume_text: Texto extraído do currículo a ser analisado.

    Returns:
        Prompt formatado pronto para envio à API de análise.
    """
    return _PROMPT_PREFIX + resume_text + _PROMPT_SUFFIX


class ResumeAnalyzerService:
    """Serviço responsável por enviar currículos à API de análise textual e interpretar os resultados.

    A comunicação com a API externa é encapsulada nesta classe.
    Erros de conectividade, limite de requisições e respostas malformadas
    são traduzidos para exceções de domínio.
    """

    def __init__(self) -> None:
        self.client = Anthropic(api_key=settings.anthropic_api_key)

    def analyze(self, resume_text: str) -> AnalysisResult:
        """Envia o texto do currículo para análise e retorna o resultado estruturado.

        Args:
            resume_text: Conteúdo textual extraído do currículo em PDF.

        Returns:
            Instância de AnalysisResult com score, level, pontos fortes,
            pontos fracos, sugestões e habilidades detectadas.

        Raises:
            AnalysisServiceError: Se a API retornar erro, a resposta for malformada
                ou ocorrer falha inesperada durante o processamento.
        """
        try:
            api_response = self.client.messages.create(
                model=settings.analysis_model,
                max_tokens=2048,
                messages=[{"role": "user", "content": _build_analysis_prompt(resume_text)}],
            )
        except APIConnectionError as exc:
            logger.error("Falha de conexão com o serviço de análise: %s", exc)
            raise AnalysisServiceError(
                "O serviço de análise está indisponível no momento."
            ) from exc
        except RateLimitError as exc:
            logger.error("Limite de requisições atingido no serviço de análise: %s", exc)
            raise AnalysisServiceError(
                "Limite de requisições atingido. Aguarde alguns instantes e tente novamente."
            ) from exc
        except APIStatusError as exc:
            logger.error("Erro de status no serviço de análise: %s", exc)
            raise AnalysisServiceError(
                f"Erro no serviço de análise (HTTP {exc.status_code})."
            ) from exc
        except Exception as exc:
            logger.error("Erro inesperado durante a análise: %s", exc)
            raise AnalysisServiceError(
                "Erro inesperado durante a análise do currículo."
            ) from exc

        raw_content = api_response.content[0].text.strip()
        raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content)
        raw_content = re.sub(r"\s*```$", "", raw_content)

        try:
            parsed_payload = json.loads(raw_content)
            return AnalysisResult(**parsed_payload)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.error("Falha ao interpretar resposta da análise: %s", exc)
            raise AnalysisServiceError(
                "Não foi possível interpretar o resultado da análise."
            ) from exc
