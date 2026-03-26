"""Exceções de domínio utilizadas em toda a aplicação."""


class ResumeAnalyzerError(Exception):
    """Exceção base para todos os erros da aplicação Resume Analyzer."""


class PDFExtractionError(ResumeAnalyzerError):
    """Erro lançado quando a extração de texto de um arquivo PDF falha.

    Pode ocorrer por arquivo corrompido, protegido por senha,
    digitalizado sem OCR ou com formato incompatível.
    """


class AnalysisServiceError(ResumeAnalyzerError):
    """Erro lançado quando o serviço de análise semântica falha.

    Inclui falhas de conectividade, limite de requisições excedido
    e respostas malformadas retornadas pela API de análise.
    """


class AnalysisNotFoundError(ResumeAnalyzerError):
    """Erro lançado quando uma análise solicitada não é encontrada no banco de dados.

    Args:
        analysis_id: Identificador único da análise que não foi encontrada.
    """

    def __init__(self, analysis_id: int) -> None:
        super().__init__(f"Análise com ID {analysis_id} não encontrada.")
        self.analysis_id = analysis_id
