from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    DocumentSummaryResponse,
    HealthResponse,
    IngestTextRequest,
    QueryRequest,
    QueryResponse,
)
from app.services.rag import RAGService


# The FastAPI app wires API endpoints to the retrieval pipeline.
app = FastAPI(title=settings.app_name)

# CORS is enabled for local frontend development while the UI lives on a separate port.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# This single service instance is enough for the MVP's in-memory storage model.
rag_service = RAGService(settings=settings)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        indexed_chunks=rag_service.index.count(),
        indexed_documents=len(rag_service.documents),
    )


@app.get("/documents", response_model=list[DocumentSummaryResponse])
def list_documents() -> list[DocumentSummaryResponse]:
    return rag_service.list_documents()


@app.post("/documents/ingest-text", response_model=DocumentSummaryResponse)
def ingest_text(payload: IngestTextRequest) -> DocumentSummaryResponse:
    return rag_service.ingest_text(
        title=payload.title,
        source_label=payload.source_label,
        text=payload.text,
    )


@app.post("/query", response_model=QueryResponse)
def query(payload: QueryRequest) -> QueryResponse:
    return rag_service.answer_question(
        question=payload.question,
        top_k=payload.top_k,
    )

