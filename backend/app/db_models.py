from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.config import settings
from app.db import Base


def build_embedding_column_type():
    # PostgreSQL uses pgvector in production while SQLite falls back to JSON for local development and tests.
    if settings.is_postgres:
        from pgvector.sqlalchemy import VECTOR

        return VECTOR(settings.embedding_dimensions)

    return JSON


# This table stores top-level documents and the cleaned source text we ingest from uploads or text input.
class DocumentRecord(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    source_label: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # The relationship makes it easy to navigate from a document to its retrieval units.
    chunks: Mapped[list["ChunkRecord"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


# This table stores retrieval chunks plus their embedding vectors and scoring metadata.
class ChunkRecord(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        Index("ix_chunks_document_id", "document_id"),
        Index("ix_chunks_document_chunk_index", "document_id", "chunk_index"),
    )

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    start_char: Mapped[int] = mapped_column(Integer, nullable=False)
    end_char: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(build_embedding_column_type(), nullable=False)
    embedding_norm: Mapped[float] = mapped_column(Float, nullable=False)

    # The reverse relationship preserves the link back to the source document for citations.
    document: Mapped[DocumentRecord] = relationship(back_populates="chunks")
