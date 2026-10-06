# Architecture

The system has three services in Compose: Next.js, FastAPI, and PostgreSQL with pgvector. A short-lived migration container applies Alembic revisions before the backend starts. SQLite is a development alternative.

## Ingestion And Retrieval

Text is normalized to single spaces, split into 600-character windows with 120-character overlap, and embedded. Document source text and chunk offsets are retained; offsets refer to normalized text, not PDF pages or the original bytes. A document and its chunks commit together after embedding succeeds.

The offline provider hashes lowercase whitespace-separated tokens with SHA-256 into 128 bins and normalizes the vector. It is reproducible across processes but collisions and punctuation affect results. It is lexical rather than semantic. OpenAI embeddings use a separate provider and model profile. Profile mismatches stop ingestion/query rather than combine unrelated vector spaces.

Queries embed the question and retrieve up to four chunks. PostgreSQL uses cosine distance; SQLite calculates dot products on normalized vectors. HNSW is an approximate index and small tables may use a sequential scan. A fixed template quotes the first two citation excerpts. This is evidence presentation, not language-model reasoning or a factuality guarantee. Unrelated queries can still return nearest neighbors.

## Storage And Boundaries

Documents own chunks through an ORM cascade. The delete endpoint removes both; backups have independent retention. The schema fixes vector dimensions at 128. Alembic's second revision marks older documents as legacy because their embeddings used Python's randomized hash. Re-ingestion requires the owner to preserve/export the source first.

FastAPI's body limit bounds input before parsing, and file/text/page limits constrain ingestion. Parsing runs in a thread pool rather than blocking the async event loop, but a malicious PDF can still consume excessive CPU or expanded memory. A separate resource-limited worker is a future change. The current trusted-workspace deployment is intentionally loopback-only.

Tests use a separate in-memory engine via dependency overrides and never drop application tables. Deployment checks use actual PostgreSQL and migrations, which exercise behavior that SQLite unit tests cannot establish.
