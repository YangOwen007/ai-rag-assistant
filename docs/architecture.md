# RAG Assistant Architecture

## Recommended MVP architecture

The project is designed around a simple but credible flow:

1. `Ingestion`
   Accept source text and metadata.
2. `Chunking`
   Split text into overlapping windows so retrieval can return focused evidence.
3. `Embedding`
   Convert chunks into vectors. The current build uses a deterministic local embedder for development.
4. `Retrieval`
   Rank chunks by semantic similarity to the question.
5. `Grounded generation`
   Compose an answer using only retrieved context and return citations.
6. `Evaluation`
   Measure whether the right chunks are retrieved and whether citations point to the right evidence.

## Why this is a good portfolio shape

- It demonstrates more than a chat wrapper.
- It separates ingestion, retrieval, and answer orchestration.
- It makes room for evaluation, which recruiters often do not see in student projects.
- It can grow naturally into a production-style service.

## Planned evolution path

### Phase 1

- text ingestion
- deterministic embeddings
- in-memory chunk index
- grounded answer API

### Phase 2

- PDF parsing
- PostgreSQL persistence
- `pgvector` retrieval
- document filters

### Phase 3

- hybrid search
- reranking
- streaming responses
- retrieval benchmarking dashboard

