# AI RAG Assistant

An internship-ready retrieval-augmented generation assistant focused on grounded answers, traceable citations, and a clear ingestion pipeline.

## Current state

This repository started empty, so the first build establishes:

- A `FastAPI` backend with a commented RAG pipeline
- A `Next.js + TypeScript` frontend for ingestion and question answering
- A deterministic local embedding fallback so we can verify retrieval behavior without external services
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

The first implementation keeps the core retrieval pipeline runnable without needing:

- a database instance
- API keys
- external model calls

This is useful for learning and for fast iteration. The code is structured so we can later swap in:

- `OpenAI` embeddings
- `PostgreSQL + pgvector`
- background ingestion jobs
- PDF extraction

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
2. Text is normalized and chunked with overlap.
3. Each chunk is embedded with a deterministic dev embedder.
4. The retriever ranks chunks with cosine similarity.
5. The answer composer builds a grounded response using retrieved context.
6. The API returns the answer plus citations and retrieval evidence.

## Running locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000` in `frontend/.env.local` if needed.

## Next build steps

- add PDF parsing and upload support
- persist documents and chunks in PostgreSQL
- add `pgvector` similarity search
- support OpenAI embeddings and answer generation
- build an evaluation harness for retrieval tuning

