from __future__ import annotations

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.db_models import ChunkRecord, DocumentRecord
from app.models import SourceDocument
from app.schemas import CitationResponse, DocumentSummaryResponse, QueryResponse
from app.services.chunking import chunk_document
from app.services.embeddings import build_embedding_provider, cosine_similarity


# This service orchestrates ingestion and answering while delegating persistence to the database.
class RAGService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedding_provider = build_embedding_provider(settings)

    def ingest_text(
        self,
        session: Session,
        title: str,
        source_label: str,
        text: str,
        original_filename: str | None = None,
        content_type: str | None = None,
    ) -> DocumentSummaryResponse:
        document = SourceDocument(
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
        chunk_embeddings = self.embedding_provider.embed_texts([chunk.text for chunk in chunks])

        session.add(
            DocumentRecord(
                id=document.id,
                title=document.title,
                source_label=document.source_label,
                raw_text=document.text,
                original_filename=original_filename,
                content_type=content_type,
            )
        )

        for chunk_index, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings, strict=True)):
            session.add(
                ChunkRecord(
                    id=chunk.id,
                    document_id=document.id,
                    chunk_index=chunk_index,
                    text=chunk.text,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    embedding=embedding,
                    embedding_norm=1.0,
                )
            )

        session.commit()

        return DocumentSummaryResponse(
            id=document.id,
            title=document.title,
            source_label=document.source_label,
            chunk_count=len(chunks),
            original_filename=original_filename,
        )

    def list_documents(self, session: Session) -> list[DocumentSummaryResponse]:
        chunk_count_subquery = (
            select(
                ChunkRecord.document_id,
                func.count(ChunkRecord.id).label("chunk_count"),
            )
            .group_by(ChunkRecord.document_id)
            .subquery()
        )
        rows = session.execute(
            select(DocumentRecord, chunk_count_subquery.c.chunk_count)
            .outerjoin(chunk_count_subquery, DocumentRecord.id == chunk_count_subquery.c.document_id)
            .order_by(DocumentRecord.title.asc())
        ).all()

        return [
            DocumentSummaryResponse(
                id=document.id,
                title=document.title,
                source_label=document.source_label,
                chunk_count=chunk_count or 0,
                original_filename=document.original_filename,
            )
            for document, chunk_count in rows
        ]

    def answer_question(self, session: Session, question: str, top_k: int | None = None) -> QueryResponse:
        effective_top_k = top_k or self.settings.top_k
        query_embedding = self.embedding_provider.embed_query(question)
        ranked_chunks = self._search_chunks(
            session=session,
            query_embedding=query_embedding,
            top_k=effective_top_k,
        )

        if not ranked_chunks:
            return QueryResponse(
                answer="I do not have any indexed documents yet, so I cannot answer with grounded citations.",
                citations=[],
                retrieval_summary="No chunks are currently indexed.",
            )

        citations = [
            CitationResponse(
                chunk_id=chunk.id,
                document_title=document.title,
                source_label=document.source_label,
                excerpt=chunk.text[:220],
                score=round(score, 4),
            )
            for chunk, document, score in ranked_chunks
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

    def _search_chunks(
        self,
        session: Session,
        query_embedding: list[float],
        top_k: int,
    ) -> list[tuple[ChunkRecord, DocumentRecord, float]]:
        # PostgreSQL can execute cosine search directly in SQL once pgvector is enabled.
        if self.settings.is_postgres:
            rows = session.execute(
                select(
                    ChunkRecord,
                    DocumentRecord,
                    ChunkRecord.embedding.cosine_distance(query_embedding).label("distance"),
                )
                .join(DocumentRecord, ChunkRecord.document_id == DocumentRecord.id)
                .order_by("distance")
                .limit(top_k)
            ).all()
            return [(chunk, document, round(1 - distance, 8)) for chunk, document, distance in rows]

        # SQLite falls back to application-side ranking so local development still works without pgvector.
        chunk_rows = session.execute(
            select(ChunkRecord, DocumentRecord).join(DocumentRecord, ChunkRecord.document_id == DocumentRecord.id)
        ).all()
        return sorted(
            [
                (
                    chunk_record,
                    document_record,
                    cosine_similarity(query_embedding, chunk_record.embedding),
                )
                for chunk_record, document_record in chunk_rows
            ],
            key=lambda item: item[2],
            reverse=True,
        )[:top_k]

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

    def get_index_counts(self, session: Session) -> tuple[int, int]:
        # These aggregates let the API report health without loading every document or chunk.
        document_count = session.scalar(select(func.count(DocumentRecord.id))) or 0
        chunk_count = session.scalar(select(func.count(ChunkRecord.id))) or 0
        return int(document_count), int(chunk_count)
