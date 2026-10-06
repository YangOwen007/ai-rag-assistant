from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError


# This helper validates the file type we support in the MVP ingestion path.
def detect_supported_suffix(filename: str | None) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix not in {".txt", ".pdf"}:
        raise ValueError("Only .txt and .pdf uploads are supported in the current MVP.")
    return suffix


# This helper routes uploaded files to the correct text extraction strategy.
def extract_text_from_upload(filename: str | None, content: bytes) -> str:
    suffix = detect_supported_suffix(filename)
    if suffix == ".txt":
        return content.decode("utf-8")

    try:
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted or len(reader.pages) > 100:
            raise ValueError("PDFs must be unencrypted and contain at most 100 pages.")
        pages = []
        for page in reader.pages:
            # Stop text expansion early; PDF parsing still needs a trusted/private deployment.
            pages.append(page.extract_text() or "")
            if sum(map(len, pages)) > 100_000:
                raise ValueError("Extracted text exceeds 100,000 characters.")
    except PdfReadError as exc:
        raise ValueError("The uploaded PDF could not be read.") from exc
    return "\n".join(pages).strip()
