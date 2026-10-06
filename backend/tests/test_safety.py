import hashlib

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.services.embeddings import DeterministicEmbeddingProvider


def test_stable_embedding_slot():
    # Expected slot is independent of Python's per-process hash seed.
    vector = DeterministicEmbeddingProvider(128).embed_query("evidence")
    expected = int.from_bytes(hashlib.sha256(b"evidence").digest()[:8], "big") % 128
    assert vector[expected] == 1.0
    assert sum(vector) == 1.0


def test_invalid_utf8_and_pdf_return_client_errors():
    client = TestClient(app)
    for filename, content in [("notes.txt", b"\xff"), ("notes.pdf", b"not a pdf")]:
        response = client.post("/documents/upload", data={"title": "Notes", "source_label": "test"}, files={"file": (filename, content)})
        assert response.status_code == 400


def test_request_size_limit():
    response = TestClient(app).post("/documents/upload", content=b"x" * (6 * 1024 * 1024))
    assert response.status_code == 413


def test_delete_removes_citations():
    client = TestClient(app)
    document = client.post("/documents/ingest-text", json={"title": "Notes", "source_label": "test", "text": "Evidence for document retention and deletion. " * 5}).json()
    assert client.delete(f"/documents/{document['id']}").status_code == 204
    assert client.get("/health").json()["indexed_chunks"] == 0
    assert client.post("/query", json={"question": "What evidence exists?"}).json()["citations"] == []


def test_invalid_overlap_rejected():
    import pytest
    with pytest.raises(ValueError, match="chunk_overlap"):
        Settings(chunk_size=200, chunk_overlap=200)


def test_legacy_vectors_refuse_mixed_queries(reset_database):
    from sqlalchemy.orm import Session
    from app.db_models import DocumentRecord
    # A migrated legacy document must not be ranked against a new embedding space.
    with Session(reset_database) as session:
        session.add(DocumentRecord(id="legacy", title="Old notes", source_label="test", raw_text="old text", embedding_profile="legacy"))
        session.commit()
    client = TestClient(app)
    assert client.post("/query", json={"question": "What evidence exists?"}).status_code == 409
    assert client.post("/documents/ingest-text", json={"title": "New notes", "source_label": "test", "text": "New source evidence. " * 5}).status_code == 409


def test_whitespace_and_text_limits():
    client = TestClient(app)
    for text in [" " * 100, "x" * 100001]:
        response = client.post("/documents/ingest-text", json={"title": "Notes", "source_label": "test", "text": text})
        assert response.status_code == 422
