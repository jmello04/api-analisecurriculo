"""Módulo responsável pela extração de texto de arquivos PDF."""

import io

import pdfplumber

from app.core.exceptions import PDFExtractionError


class PDFExtractorService:
    """Serviço para extração de conteúdo textual de arquivos PDF.

    Utiliza a biblioteca pdfplumber para iterar sobre as páginas do documento
    e concatenar os textos extraídos de cada página com conteúdo legível.
    """

    def extract_text(self, file_bytes: bytes) -> str:
        """Extrai o texto de todas as páginas legíveis de um arquivo PDF.

        Args:
            file_bytes: Conteúdo binário do arquivo PDF.

        Returns:
            Texto consolidado de todas as páginas, separadas por newline.

        Raises:
            PDFExtractionError: Se o arquivo não puder ser aberto, processado
                ou se nenhum texto legível for encontrado.
        """
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages_with_text = [
                    page.extract_text()
                    for page in pdf.pages
                    if page.extract_text()
                ]
        except Exception as exc:
            raise PDFExtractionError(
                "Não foi possível abrir ou processar o arquivo PDF."
            ) from exc

        if not pages_with_text:
            raise PDFExtractionError("Nenhum texto legível foi encontrado no arquivo PDF.")

        return "\n".join(pages_with_text)
