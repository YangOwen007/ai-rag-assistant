from fastapi.testclient import TestClient

from app.main import app


# This fixture text gives the retrieval pipeline a realistic-enough knowledge base for tests.
PROJECT_BRIEF = """
The AI RAG assistant is meant to demonstrate practical AI engineering through
document ingestion, chunking, embeddings, retrieval, grounded answers, and
traceable citations. The MVP should feel more serious than a toy chatbot and
should be easy to explain in internship interviews.
"""

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
    assert payload["original_filename"] is None


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


def test_upload_text_document_persists_filename() -> None:
    client = TestClient(app)

    response = client.post(
        "/documents/upload",
        data={
            "title": "Uploaded Notes",
            "source_label": "course-notes",
        },
        files={
            "file": ("notes.txt", (PROJECT_BRIEF * 3).encode("utf-8"), "text/plain"),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["original_filename"] == "notes.txt"
    assert payload["chunk_count"] >= 1
