from __future__ import annotations

from app.models import SourceChunk, SourceDocument


# This helper normalizes whitespace so chunking behaves more predictably across documents.
def normalize_text(text: str) -> str:
    return " ".join(text.split())


# This splitter creates overlapping character windows to preserve local context across chunk boundaries.
def chunk_document(document: SourceDocument, chunk_size: int, chunk_overlap: int) -> list[SourceChunk]:
    normalized = normalize_text(document.text)
    chunks: list[SourceChunk] = []
    start = 0
    index = 0

    while start < len(normalized):
        end = min(start + chunk_size, len(normalized))
        chunk_text = normalized[start:end]

        chunks.append(
            SourceChunk(
                id=f"{document.id}-chunk-{index}",
                document_id=document.id,
                title=document.title,
                source_label=document.source_label,
                text=chunk_text,
                start_char=start,
                end_char=end,
            )
        )

        if end == len(normalized):
            break

        start = max(end - chunk_overlap, start + 1)
        index += 1

    return chunks
