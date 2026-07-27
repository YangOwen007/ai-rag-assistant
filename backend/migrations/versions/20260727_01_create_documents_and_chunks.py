"""create documents and chunks

Revision ID: 20260727_01
Revises: 
Create Date: 2026-07-27 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260727_01"
down_revision = None
branch_labels = None
depends_on = None


def _embedding_type():
    if op.get_bind().dialect.name == "postgresql":
        from pgvector.sqlalchemy import VECTOR

        return VECTOR(128)

    return sa.JSON()


def upgrade() -> None:
    # PostgreSQL needs the extension enabled before vector columns or vector operators can be used.
    if op.get_bind().dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("source_label", sa.String(length=100), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=True),
        sa.Column("content_type", sa.String(length=100), nullable=True),
    )

    op.create_table(
        "chunks",
        sa.Column("id", sa.String(length=80), primary_key=True),
        sa.Column("document_id", sa.String(length=36), sa.ForeignKey("documents.id", ondelete="CASCADE")),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("start_char", sa.Integer(), nullable=False),
        sa.Column("end_char", sa.Integer(), nullable=False),
        sa.Column("embedding", _embedding_type(), nullable=False),
        sa.Column("embedding_norm", sa.Float(), nullable=False),
    )

    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])
    op.create_index("ix_chunks_document_chunk_index", "chunks", ["document_id", "chunk_index"])

    if op.get_bind().dialect.name == "postgresql":
        op.create_index(
            "ix_chunks_embedding_hnsw",
            "chunks",
            ["embedding"],
            unique=False,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.drop_index("ix_chunks_embedding_hnsw", table_name="chunks")

    op.drop_index("ix_chunks_document_chunk_index", table_name="chunks")
    op.drop_index("ix_chunks_document_id", table_name="chunks")
    op.drop_table("chunks")
    op.drop_table("documents")
