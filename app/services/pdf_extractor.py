import io

import pdfplumber

from app.core.exceptions import PDFExtractionError


class PDFExtractorService:
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                paginas = [p.extract_text() for p in pdf.pages if p.extract_text()]
        except Exception as exc:
            raise PDFExtractionError("Não foi possível abrir ou processar o arquivo PDF.") from exc

        if not paginas:
            raise PDFExtractionError("Nenhum texto legível foi encontrado no arquivo PDF.")

        return "\n".join(paginas)
