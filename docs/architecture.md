# RAG Assistant Architecture

## Recommended MVP architecture

The project is designed around a simple but credible flow:

1. `Ingestion`
   Accept source text, uploads, and metadata.
2. `Chunking`
   Split text into overlapping windows so retrieval can return focused evidence.
3. `Embedding`
   Convert chunks into vectors through a provider abstraction. The current build supports a deterministic local provider and an optional OpenAI provider.
4. `Persistence`
   Store documents and chunks in SQLAlchemy-managed tables so retrieval survives restarts.
5. `Retrieval`
   Rank chunks by semantic similarity to the question, using `pgvector` in PostgreSQL and a Python fallback in SQLite.
6. `Grounded generation`
   Compose an answer using only retrieved context and return citations.
7. `Evaluation`
   Measure whether the right chunks are retrieved and whether citations point to the right evidence.

## Why this is a good portfolio shape

- It demonstrates more than a chat wrapper.
- It separates ingestion, retrieval, and answer orchestration.
- It makes room for evaluation, which recruiters often do not see in student projects.
- It can grow naturally into a production-style service.

## Planned evolution path

### Phase 1

- text and PDF ingestion
- deterministic embeddings
- persistent document and chunk storage
- grounded answer API
- migration support

### Phase 2

- OpenAI embeddings in deployed environments
- verified PostgreSQL persistence
- verified `pgvector` retrieval in production-like environments
- document filters

### Phase 3

- hybrid search
- reranking
- streaming responses
- retrieval benchmarking dashboard
