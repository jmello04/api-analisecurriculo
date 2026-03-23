import io

import pdfplumber

from app.core.exceptions import PDFExtractionError


class PDFExtractorService:
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages = [page.extract_text() for page in pdf.pages if page.extract_text()]
        except Exception as exc:
            raise PDFExtractionError("Failed to open or parse the PDF file.") from exc

        if not pages:
            raise PDFExtractionError("No readable text found in the PDF file.")

        return "\n".join(pages)
