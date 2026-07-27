# AI RAG Assistant

An internship-ready retrieval-augmented generation assistant focused on grounded answers, traceable citations, and a clear ingestion pipeline.

## Current state

This repository started empty, so the first build establishes:

- A `FastAPI` backend with a commented RAG pipeline
- Persistent document and chunk storage through `SQLAlchemy`
- Text and PDF upload ingestion
- Alembic migrations for schema management
- A `pgvector`-ready retrieval path for PostgreSQL plus a SQLite fallback for local development
- A `Next.js + TypeScript` frontend for ingestion and question answering
- An embeddings provider abstraction with deterministic local embeddings and optional OpenAI embeddings
- Project docs and evaluation fixtures that make the architecture easy to explain in interviews

## Recommended MVP scope

This MVP is scoped as a study and research assistant that can:

- ingest text documents
- chunk them into retrieval-friendly segments
- embed and index chunks
- retrieve relevant chunks for a question
- answer with grounded citations
- expose simple retrieval diagnostics

That scope is narrow enough to finish cleanly and strong enough to demonstrate real AI engineering decisions.

## Target production stack

- Backend: `Python + FastAPI`
- Frontend: `Next.js + TypeScript`
- Database: `PostgreSQL`
- Vector storage: `pgvector`
- Validation/config: `Pydantic`

## Why the backend currently uses a local embedding fallback

The current implementation keeps the core retrieval pipeline runnable without needing:

- API keys
- external model calls in local development
- a running PostgreSQL instance for every contributor

This is useful for learning and for fast iteration. The code is structured so we can later swap in:

- `OpenAI` embeddings by setting `RAG_EMBEDDING_PROVIDER=openai`
- `PostgreSQL + pgvector` as the default deployed database/vector path
- background ingestion jobs
- OCR for scanned PDFs

without rewriting the application shape.

## Project layout

```text
backend/    FastAPI app, RAG services, and tests
frontend/   Next.js UI
docs/       Architecture notes
eval/       Sample RAG evaluation fixtures
```

## Architecture summary

1. Documents are ingested into the backend.
2. Source text is persisted along with document metadata.
3. Text is normalized and chunked with overlap.
4. Chunks are embedded through a provider abstraction and stored in the database.
5. PostgreSQL deployments can use `pgvector` cosine search, while SQLite development falls back to application-side ranking.
6. The answer composer builds a grounded response using retrieved context.
7. The API returns the answer plus citations and retrieval evidence.

## Running locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

Optional:
- Set `RAG_DATABASE_URL=postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_assistant` when you want to point the app at PostgreSQL instead of the default local SQLite database.
- Copy `backend/.env.example` to `backend/.env` and switch `RAG_EMBEDDING_PROVIDER=openai` when you are ready to use production embeddings.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000` in `frontend/.env.local` if needed.

## Next build steps

- stand up a real PostgreSQL instance with the `vector` extension and validate the `pgvector` retrieval path end to end
- add answer generation through a real LLM instead of the current deterministic answer composer
- add OCR for scanned PDFs
- build an evaluation harness for retrieval tuning
- add background ingestion jobs and deployment manifests
