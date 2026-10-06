"use client";

import { FormEvent, useEffect, useRef, useState } from "react";


type HealthResponse = {
  status: string;
  indexed_chunks: number;
  indexed_documents: number;
};

type DocumentSummary = {
  id: string;
  title: string;
  source_label: string;
  chunk_count: number;
  original_filename?: string | null;
};

type Citation = {
  chunk_id: string;
  document_title: string;
  source_label: string;
  excerpt: string;
  score: number;
};

type QueryResponse = {
  answer: string;
  citations: Citation[];
  retrieval_summary: string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

const starterText = `Retrieval-augmented generation combines information retrieval with answer generation.
In this project, the goal is to build a grounded assistant that can ingest documents, retrieve relevant chunks,
and return answers with citations so users can inspect the supporting evidence.`;


// This page provides one polished screen for text ingestion, file uploads, querying, and evidence inspection.
export default function HomePage() {
  const fileInput = useRef<HTMLInputElement>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [answer, setAnswer] = useState<QueryResponse | null>(null);
  const [title, setTitle] = useState("RAG Primer");
  const [sourceLabel, setSourceLabel] = useState("study-notes");
  const [text, setText] = useState(starterText);
  const [question, setQuestion] = useState("What does this assistant aim to do?");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [status, setStatus] = useState("Ready to ingest your first document.");
  const [loading, setLoading] = useState(false);

  // This startup load gives the dashboard a quick health snapshot and any indexed documents.
  useEffect(() => {
    void refreshWorkspace().catch(() => setStatus("Cannot reach the backend. Check its configuration and database readiness."));
  }, []);

  async function refreshWorkspace() {
    const [healthResponse, documentsResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/health`),
      fetch(`${API_BASE_URL}/documents`)
    ]);

    if (!healthResponse.ok || !documentsResponse.ok) {
      throw new Error("Workspace unavailable");
    }
    setHealth(await healthResponse.json());
    setDocuments(await documentsResponse.json());
  }

  // Display safe backend validation messages instead of treating every error as an outage.
  async function requireSuccess(response: Response) {
    if (response.ok) return;
    const payload = await response.json().catch(() => null);
    throw new Error(typeof payload?.detail === "string" ? payload.detail : `Request failed (${response.status}). Check your input or backend availability.`);
  }

  async function handleDelete(document: DocumentSummary) {
    if (!window.confirm(`Delete ${document.title} and all its indexed chunks?`)) return;
    setLoading(true);
    try {
      await requireSuccess(await fetch(`${API_BASE_URL}/documents/${document.id}`, { method: "DELETE" }));
      setAnswer(null);
      await refreshWorkspace();
      setStatus(`Deleted ${document.title}. Backups may still contain this document.`);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Deletion failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleIngest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus("Indexing document and generating chunks...");

    try {
      const response = await fetch(`${API_BASE_URL}/documents/ingest-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, source_label: sourceLabel, text })
      });

      await requireSuccess(response);

      const payload: DocumentSummary = await response.json();
      setStatus(`Indexed ${payload.chunk_count} chunks from ${payload.title}.`);
      await refreshWorkspace();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Ingestion failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile) {
      setStatus("Choose a .txt or .pdf file before uploading.");
      return;
    }

    setLoading(true);
    setStatus("Uploading file, extracting text, and indexing chunks...");

    try {
      const formData = new FormData();
      formData.append("title", title);
      formData.append("source_label", sourceLabel);
      formData.append("file", selectedFile);

      const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: "POST",
        body: formData
      });

      await requireSuccess(response);

      const payload: DocumentSummary = await response.json();
      setStatus(`Uploaded ${payload.original_filename ?? payload.title} and indexed ${payload.chunk_count} chunks.`);
      setSelectedFile(null);
      if (fileInput.current) fileInput.current.value = "";
      await refreshWorkspace();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleQuery(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setStatus("Retrieving evidence and composing a grounded answer...");

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      await requireSuccess(response);

      const payload: QueryResponse = await response.json();
      setAnswer(payload);
      setStatus(payload.retrieval_summary);
      await refreshWorkspace();
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Query failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-shell">
      <div className="page-grid">
        <section className="hero">
          <span className="eyebrow">Document retrieval</span>
          <h1>Find source evidence you can inspect.</h1>
          <p>
            Upload text or a PDF, then ask a question to see matching excerpts and citations.
            Responses summarize retrieved evidence using a fixed template, without language-model generation.
          </p>
          <div className="stats">
            <div className="stat-card">
              <strong>{health?.indexed_documents ?? 0}</strong>
              Indexed documents
            </div>
            <div className="stat-card">
              <strong>{health?.indexed_chunks ?? 0}</strong>
              Indexed chunks
            </div>
            <div className="stat-card">
              <strong>{health?.status ?? "offline"}</strong>
              Backend status
            </div>
          </div>
        </section>

        <section className="workspace">
          <div className="panel">
            <h2>Ingest Source Material</h2>
            <form onSubmit={handleIngest}>
              <div className="field">
                <label htmlFor="title">Document title</label>
                <input id="title" required minLength={3} maxLength={200} value={title} onChange={(event) => setTitle(event.target.value)} />
              </div>
              <div className="field">
                <label htmlFor="source-label">Source label</label>
                <input
                  id="source-label"
                  required minLength={2} maxLength={100}
                  value={sourceLabel}
                  onChange={(event) => setSourceLabel(event.target.value)}
                />
              </div>
              <div className="field">
                <label htmlFor="text">Paste source text</label>
                <textarea id="text" required minLength={50} maxLength={100000} value={text} onChange={(event) => setText(event.target.value)} />
              </div>
              <button className="action" disabled={loading} type="submit">
                Index pasted text
              </button>
            </form>

            <div className="splitter">
              <span />
              <small>or upload source files</small>
              <span />
            </div>

            <form onSubmit={handleUpload}>
              <div className="field">
                <label htmlFor="file">Upload .txt or .pdf</label>
                <input
                  id="file"
                  ref={fileInput}
                  type="file"
                  accept=".txt,.pdf"
                  onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                />
              </div>
              <button className="action secondary-action" disabled={loading} type="submit">
                Upload and index file
              </button>
            </form>

            <div className="document-list">
              {documents.length === 0 ? <p>No documents indexed yet.</p> : null}
              {documents.map((document) => (
                <article className="document-card" key={document.id}>
                  <strong>{document.title}</strong>
                  <small>{document.source_label} / {document.chunk_count} chunks</small>
                  {document.original_filename ? <small>Uploaded from {document.original_filename}</small> : null}
                  <button className="delete-action" disabled={loading} onClick={() => void handleDelete(document)} aria-label={`Delete ${document.title}`}>Delete document</button>
                </article>
              ))}
            </div>
          </div>

          <div className="panel">
            <h2>Ask Grounded Questions</h2>
            <form onSubmit={handleQuery}>
              <div className="field">
                <label htmlFor="question">Question</label>
                <textarea
                  id="question"
                  required minLength={5} maxLength={500}
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                />
              </div>
              <button className="action" disabled={loading} type="submit">
                Retrieve answer
              </button>
            </form>

            <p className="status" role="status" aria-live="polite">{status}</p>

            {answer ? (
              <>
                <article className="answer-card">
                  <strong>Answer</strong>
                  <p>{answer.answer}</p>
                </article>
                <div className="citation-list">
                  {answer.citations.map((citation) => (
                    <article className="citation-card" key={citation.chunk_id}>
                      <strong>{citation.document_title}</strong>
                      <small>{citation.source_label} / similarity {citation.score}</small>
                      <p>{citation.excerpt}</p>
                    </article>
                  ))}
                </div>
              </>
            ) : null}
          </div>
        </section>
      </div>
    </main>
  );
}
