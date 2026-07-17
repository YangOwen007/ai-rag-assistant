from __future__ import annotations

from uuid import uuid4

from app.config import Settings
from app.models import Document
from app.schemas import CitationResponse, DocumentSummaryResponse, QueryResponse
from app.services.chunking import chunk_document
from app.services.embeddings import DeterministicEmbedder
from app.services.retrieval import InMemoryChunkIndex


# This service orchestrates ingestion and answering so the API layer stays thin and easy to read.
class RAGService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedder = DeterministicEmbedder(settings.embedding_dimensions)
        self.index = InMemoryChunkIndex(self.embedder)
        self.documents: dict[str, Document] = {}
        self.document_chunks: dict[str, int] = {}

    def ingest_text(self, title: str, source_label: str, text: str) -> DocumentSummaryResponse:
        document = Document(
            id=str(uuid4()),
            title=title,
            source_label=source_label,
            text=text,
        )
        chunks = chunk_document(
            document=document,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

        self.documents[document.id] = document
        self.document_chunks[document.id] = len(chunks)
        self.index.add_chunks(chunks)

        return DocumentSummaryResponse(
            id=document.id,
            title=document.title,
            source_label=document.source_label,
            chunk_count=len(chunks),
        )

    def list_documents(self) -> list[DocumentSummaryResponse]:
        return [
            DocumentSummaryResponse(
                id=document.id,
                title=document.title,
                source_label=document.source_label,
                chunk_count=self.document_chunks.get(document.id, 0),
            )
            for document in self.documents.values()
        ]

    def answer_question(self, question: str, top_k: int | None = None) -> QueryResponse:
        effective_top_k = top_k or self.settings.top_k
        ranked_chunks = self.index.search(question, effective_top_k)

        if not ranked_chunks:
            return QueryResponse(
                answer="I do not have any indexed documents yet, so I cannot answer with grounded citations.",
                citations=[],
                retrieval_summary="No chunks are currently indexed.",
            )

        citations = [
            CitationResponse(
                chunk_id=chunk.id,
                document_title=chunk.title,
                source_label=chunk.source_label,
                excerpt=chunk.text[:220],
                score=round(score, 4),
            )
            for chunk, score in ranked_chunks
        ]

        answer = self._compose_grounded_answer(question=question, citations=citations)
        retrieval_summary = (
            f"Retrieved {len(citations)} chunks across {len({c.document_title for c in citations})} document(s)."
        )
        return QueryResponse(
            answer=answer,
            citations=citations,
            retrieval_summary=retrieval_summary,
        )

    # This answer composer deliberately stays deterministic so the retrieval quality is easy to inspect.
    def _compose_grounded_answer(
        self,
        question: str,
        citations: list[CitationResponse],
    ) -> str:
        evidence_lines = [
            f"Source {index + 1} ({citation.document_title}): {citation.excerpt}"
            for index, citation in enumerate(citations[:2])
        ]
        evidence_block = " ".join(evidence_lines)
        return (
            f"Grounded answer for: '{question}'. "
            f"Based on the top retrieved evidence, the most relevant context is: {evidence_block}"
        )

