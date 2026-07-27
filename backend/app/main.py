from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db_session
from app.schemas import (
    DocumentSummaryResponse,
    HealthResponse,
    IngestTextRequest,
    QueryRequest,
    QueryResponse,
)
from app.services.extraction import extract_text_from_upload
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

# This service instance now talks to persistent storage through request-scoped sessions.
rag_service = RAGService(settings=settings)


@app.get("/health", response_model=HealthResponse)
def health(db: Annotated[Session, Depends(get_db_session)]) -> HealthResponse:
    document_count, chunk_count = rag_service.get_index_counts(db)
    return HealthResponse(
        status="ok",
        indexed_chunks=chunk_count,
        indexed_documents=document_count,
    )


@app.get("/documents", response_model=list[DocumentSummaryResponse])
def list_documents(db: Annotated[Session, Depends(get_db_session)]) -> list[DocumentSummaryResponse]:
    return rag_service.list_documents(db)


@app.post("/documents/ingest-text", response_model=DocumentSummaryResponse)
def ingest_text(
    payload: IngestTextRequest,
    db: Annotated[Session, Depends(get_db_session)],
) -> DocumentSummaryResponse:
    return rag_service.ingest_text(
        session=db,
        title=payload.title,
        source_label=payload.source_label,
        text=payload.text,
    )


@app.post("/documents/upload", response_model=DocumentSummaryResponse)
async def upload_document(
    db: Annotated[Session, Depends(get_db_session)],
    title: Annotated[str, Form(min_length=3, max_length=200)],
    source_label: Annotated[str, Form(min_length=2, max_length=100)],
    file: UploadFile = File(...),
) -> DocumentSummaryResponse:
    content = await file.read()

    try:
        extracted_text = extract_text_from_upload(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Uploaded text files must be UTF-8 encoded.") from exc

    if len(extracted_text.strip()) < 50:
        raise HTTPException(status_code=400, detail="The uploaded file did not contain enough extractable text.")

    return rag_service.ingest_text(
        session=db,
        title=title,
        source_label=source_label,
        text=extracted_text,
        original_filename=file.filename,
        content_type=file.content_type,
    )


@app.post("/query", response_model=QueryResponse)
def query(
    payload: QueryRequest,
    db: Annotated[Session, Depends(get_db_session)],
) -> QueryResponse:
    return rag_service.answer_question(
        session=db,
        question=payload.question,
        top_k=payload.top_k,
    )
