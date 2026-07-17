from fastapi.testclient import TestClient

from app.main import app, rag_service


# This fixture text gives the retrieval pipeline a realistic-enough knowledge base for tests.
PROJECT_BRIEF = """
The AI RAG assistant is meant to demonstrate practical AI engineering through
document ingestion, chunking, embeddings, retrieval, grounded answers, and
traceable citations. The MVP should feel more serious than a toy chatbot and
should be easy to explain in internship interviews.
"""


def setup_function() -> None:
    # Each test resets the in-memory index so assertions stay isolated and deterministic.
    rag_service.documents.clear()
    rag_service.document_chunks.clear()
    rag_service.index._chunks.clear()


def test_ingest_text_creates_chunks() -> None:
    client = TestClient(app)

    response = client.post(
        "/documents/ingest-text",
        json={
            "title": "Project Brief",
            "source_label": "project-brief",
            "text": PROJECT_BRIEF * 4,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Project Brief"
    assert payload["chunk_count"] >= 1


def test_query_returns_grounded_citations() -> None:
    client = TestClient(app)
    client.post(
        "/documents/ingest-text",
        json={
            "title": "Project Brief",
            "source_label": "project-brief",
            "text": PROJECT_BRIEF * 4,
        },
    )

    response = client.post(
        "/query",
        json={"question": "What should this project demonstrate?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "Grounded answer" in payload["answer"]
    assert len(payload["citations"]) >= 1
    assert payload["citations"][0]["source_label"] == "project-brief"

