from typing import List

from pydantic import BaseModel, Field


# This request accepts plain text so we can validate the retrieval pipeline before file upload work.
class IngestTextRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    source_label: str = Field(min_length=2, max_length=100)
    text: str = Field(min_length=50)


# This model captures the question we want to answer with grounded retrieval.
class QueryRequest(BaseModel):
    question: str = Field(min_length=5, max_length=500)
    top_k: int | None = Field(default=None, ge=1, le=10)


# This response shape keeps citation data explicit for frontend display and debugging.
class CitationResponse(BaseModel):
    chunk_id: str
    document_title: str
    source_label: str
    excerpt: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    citations: List[CitationResponse]
    retrieval_summary: str


class DocumentSummaryResponse(BaseModel):
    id: str
    title: str
    source_label: str
    chunk_count: int


class HealthResponse(BaseModel):
    status: str
    indexed_chunks: int
    indexed_documents: int

