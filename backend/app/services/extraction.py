from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader


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

    reader = PdfReader(BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()
